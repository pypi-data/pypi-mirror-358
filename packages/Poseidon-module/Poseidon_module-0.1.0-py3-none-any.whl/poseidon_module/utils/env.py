# -*- coding:utf-8 -*-
import os
import random
import re
import threading
import time
from queue import Queue
from typing import Optional
from typing import Union

import serial

from poseidon_module.core.const import COMMUNICATION_WITH_UART, COMMUNICATION_WITH_WLAN
from poseidon_module.core.decorators import TraceActionMeta, PoseidonError
from poseidon_module.core.globals import Globals
from poseidon_module.core.logger import sys_log, log_manager
from poseidon_module.core.poseidon import Poseidon
from poseidon_module.core.shell import Shell
from poseidon_module.utils.device import UtilDevice
from poseidon_module.utils.pc import UtilPC


class UtilEnv(Shell, metaclass=TraceActionMeta):
    def __init__(self):
        super().__init__()
        self.device = UtilDevice()
        self.pc = UtilPC()
        self.poseidon = Poseidon()

    @staticmethod
    def __clear_queue(queue2):
        while not queue2.empty():
            queue2.get()

    def __get_ser_data(self, port, queue1, queue2):
        serial_log = log_manager.register_logger("SerialLog", log_to_console=False)
        read_buf = ""  # 本地缓存
        sys_log.debug(f"{port} 开始存日志")
        while True:
            if not Globals.get("CheckDebug"):
                self.__clear_queue(queue2)
            if queue1.empty():
                time.sleep(0.1)
                continue
            data = queue1.get()
            read_buf += data
            if "\n\r" in read_buf or "\r\n" in read_buf:  # 默认换行符为 \r\n 或 \n\r
                lines = re.split("[\r\n]", read_buf)
                if not read_buf.endswith("\n\r") and not read_buf.endswith("\r\n"):
                    read_buf = lines.pop()
                else:
                    read_buf = ""
                for line in lines:
                    line = re.sub(r'\x1b\[.*?m', '', line).strip()
                    if line:
                        serial_log.debug(line)
                        if Globals.get("CheckDebug"):
                            queue2.put(line)
        sys_log.debug(f"{port} 停止存日志")

    @staticmethod
    def __debug_read_always(debug_ser, queue1):
        """优化的持续串口读取线程
        Args:
            debug_ser: 串口对象
            queue1: 数据存储队列
        """
        retry_count = 0
        max_retries = 10
        while True:
            try:
                if debug_ser.in_waiting > 0:
                    b_data = debug_ser.read(debug_ser.in_waiting)
                    data = b_data.decode("ISO-8859-1", errors="replace")
                    queue1.put(data)
                    retry_count = 0  # 成功读取重置重试计数
            except serial.SerialException as e:
                sys_log.warning(f"串口通信异常: {str(e)}")
                retry_count += 1
                if retry_count > max_retries:
                    sys_log.critical("达到最大重试次数，终止读取线程")
                    break
                try:
                    if debug_ser.is_open:
                        debug_ser.close()
                    debug_ser.open()
                    sys_log.info(f"串口重连成功 (尝试 {retry_count}/{max_retries})")
                except Exception as reconnect_error:
                    sys_log.warning(f"重连失败: {str(reconnect_error)}")
                    time.sleep(2 ** retry_count)  # 指数退避
            except Exception as e:
                sys_log.critical(f"不可恢复错误: {str(e)}")
                break
            finally:
                time.sleep(0.01)  # 防止CPU占用过高

    @staticmethod
    def __init_serial_connection(port: str) -> Optional[serial.Serial]:
        """初始化串口连接"""
        try:
            return serial.Serial(
                port=port,
                baudrate=115200,
                bytesize=8,
                parity="N",
                stopbits=1,
                timeout=1
            )
        except serial.SerialException as e:
            raise serial.SerialException(f"串口{port}连接失败: {e}") from e

    def bind_devices_info(self, communication: int = COMMUNICATION_WITH_WLAN):
        """ 绑定设备信息 """
        config = Globals.get("Config")
        app_list = []
        if communication == COMMUNICATION_WITH_UART:
            raise Exception("暂不支持")
        assert config.get("G_DEV_IDS") is not None, "设备ID不能为空"
        for i, dev_id in enumerate(config.get("G_DEV_IDS")):
            debug_port = config.get("G_DEBUGS")[i]
            if debug_port != "COM0":
                debug_ser = self.__init_serial_connection(debug_port)
                d_queue1 = Queue()
                d_queue2 = Queue()
                th = threading.Thread(target=self.__debug_read_always, args=(debug_ser, d_queue1), daemon=True)
                th.start()
                th = threading.Thread(target=self.__get_ser_data, args=(debug_port, d_queue1, d_queue2), daemon=True)
                th.start()
            else:
                debug_ser = None
                d_queue2 = None
            app_info = {
                "dev_id": dev_id,
                "communication": communication,
                "pwd": config.get("G_DEV_PWD")[i],
                "phone_num": config.get("G_PHONE_NUM")[i],
                "relay_info": config.get("G_RES")[i],
                "debug_port": config.get("G_DEBUGS")[i],
                "debug_obj": debug_ser,
                "debug_queue": d_queue2,
                "module_info": config.get("G_MODULE_INFO")[i],
                "dev_gw": Globals.get("DEV_GW"),
                "dev_ip": ""
            }
            app_list.append(app_info)
        Globals.set("PoseidonList", app_list)

    def __check_rndis(self, dev_index):
        port_list = self.pc.regedit_get_modem_usb_device(dev_index)
        assert port_list, "未检测到USB设备端口信息！"
        for port in port_list:
            if "NDIS" in port["description"]:
                return True
        return False

    def __remount_app_dir(self, dev_index=1):
        try:
            device_id = Globals.dev_id(dev_index)
            app_dir = Globals.get("APP_DIR")
            ret, info = self.execute_adb_shell(f"mount | grep 'on /{app_dir} '", dev_index=dev_index)
            assert ret, f"设备【{device_id}】查询挂载信息失败!"
            sys_log.info(f"设备【{device_id}】当前挂载情况为 {info}")
            if "noexec" in info:
                sys_log.info(f"设备【{device_id}】重新挂载 {app_dir} 分区")
                ret, info = self.execute_adb_shell(f"mount -o remount rw, /{app_dir}", dev_index=dev_index)
                assert ret, f"设备【{device_id}】重新挂载 {app_dir} 目录失败！"
                time.sleep(2)
        except Exception as e:
            sys_log.error(e)
            return False
        return True

    def __set_module_usb_mode_to_rndis(self, dev_index: Union[int, str] = 1) -> bool:
        """ 设置模块USB模式为RNDIS模式 """
        try:
            sys_log.info("设置模块USB模式为RNDIS模式")
            default_mode = Globals.get("USBMode")
            if self.__check_rndis(dev_index):
                return True
            assert self.__remount_app_dir(dev_index=dev_index), "重新挂载App目录失败！"
            ret, _ = self.device.poseidon_shortcut_action(1, f"AT+GTUSBMODE={default_mode}", dev_index, check=False)
            assert ret, "设置USB模式失败！"
            ret = self.device.check_adb_status(False, timeout=3, dev_index=dev_index)  # 等待usb端口刷新
            if not ret:  # 模块未重启，需要主动重启使端口组合生效
                assert self.device.adb_shell_reboot(dev_index=dev_index), "reboot 重启失败！"
                assert self.device.check_module_boot_status(Globals.get("START_PROCESS"), dev_index=dev_index)
            else:
                ret = self.device.check_adb_status(True, timeout=10, dev_index=dev_index)  # 等待 USB 端口重连
                if not ret:  # 10秒后仍未重连成功，认为模块已发生重启，需要检查启动状态
                    assert self.device.check_module_boot_status(Globals.get("START_PROCESS"), dev_index=dev_index)
            return self.__check_rndis(dev_index)
        except Exception as e:
            sys_log.error(e)
            return False

    def __set_module_env_for_wlan(self, dev_index=1):
        try:
            gw = Globals.get("DEV_GW")
            assert self.__set_module_usb_mode_to_rndis(dev_index=dev_index), "设置模块USB模式为RNDIS模式失败！"
            ret, iface_name = self.pc.rndis_name(dev_index=dev_index)
            assert ret, f"获取 {dev_index} 网卡名称失败！"
            prefix = ".".join(gw.split(".")[:-1])
            ret, cur_ip = self.pc.get_target_ip_addr(prefix, iface_name, timeout=1)
            tmp_list = []
            if not ret:
                Globals.set("ServerState", False)
                ip_list = self.pc.rndis_ips()
                for ip in ip_list:
                    if re.findall(prefix, ip):
                        tmp_list.append(int(ip.split(".")[-1]))
                cur_ip = f"{prefix}.{random.choice(list(set(range(10, 100)) - set(tmp_list)))}"
                ret = self.pc.set_static_ip_addr(iface_name, cur_ip, "255.255.255.0", gw)
                assert ret, "静态IP设置失败！"
                time.sleep(3)
            Globals.set_module("dev_ip", cur_ip, dev_index)
        except Exception as e:
            raise PoseidonError(f"设置模块环境失败！{e}")

    def start_poseidon(self, dev_index=1):
        app_dir = Globals.get("APP_DIR")
        cmd = f"/{app_dir}/poseidon.sh"
        try:
            assert self.__remount_app_dir(dev_index=dev_index), "重新挂载App目录失败！"
            ret, info = self.execute_adb_shell_background(cmd, proc_name="poseidon_centre", dev_index=dev_index)
            assert ret, "Poseidon启动失败！"
            assert self.poseidon.handshake_to_poseidon(dev_index=dev_index), "Poseidon handshake失败！"
        except Exception as e:
            raise PoseidonError(f"启动Poseidon失败！{e}")

    def setup_test_env(self, start_app: bool = True, dev_index: Union[int, str] = 1):
        Globals.set("ServerState", False)
        try:
            assert self.device.check_adb_status(True, 1, timeout=3, dev_index=dev_index), "设备未启动！"
            assert self.device.adb_shell_root(dev_index=dev_index), "root权限获取失败！"
            assert self.device.set_localtime_in_module(dev_index=dev_index), "时间同步失败！"
            if start_app:
                self.__set_module_env_for_wlan(dev_index=dev_index)
                if self.device.check_poseidon_online(timeout=1, dev_index=dev_index):
                    if self.poseidon.handshake_to_poseidon(dev_index=dev_index):
                        return True
                self.start_poseidon(dev_index=dev_index)
            return True
        except Exception as e:
            sys_log.error(e)
            return False

    def send_log_tag(self):
        """ 给所有日志发送用例编号 """
        module_num = Globals.module_num()
        case_name = Globals.get("CaseName")
        assert module_num, "未获取到模组数量！"
        for dev_id in range(1, module_num + 1):
            ret = self.poseidon.send_case_num_to_module(case_name, dev_index=dev_id)
            assert ret, f"发送 {case_name} 时间到模块{dev_id}失败！"
            self.execute_adb_shell(f"echo {case_name} > /dev/kmsg", dev_index=dev_id)

    @staticmethod
    def __pc_get_case_log():
        """提取指定测试用例的日志片段"""
        cur_log = rf"{Globals.log_path()}\SystemLog\SystemLog_current.log"
        case_log = rf"{Globals.log_path()}\system.log"
        try:
            with open(cur_log, "r", encoding="utf-8") as rfd:
                content = rfd.read()
            start_tag = f'CASE {Globals.get("CaseName")} START'
            end_tag = f'CASE {Globals.get("CaseName")} END'
            start_idx = content.find(start_tag)
            end_idx = content.find(end_tag)
            if start_idx == -1 or end_idx == -1:
                raise ValueError(f'未找到{Globals.get("CaseName")}的日志标记')
            with open(case_log, "w", encoding="utf-8") as wfd:
                wfd.write(content[start_idx:end_idx + len(end_tag)])
        except FileNotFoundError:
            print(f"日志文件不存在: {cur_log}")
        except Exception as e:
            print(f"日志提取失败: {str(e)}")

    def __get_log(self, dev_index):
        ret = self.poseidon.pkg_module_logs(Globals.get("CaseName"), dev_index)
        if not ret:
            sys_log.warning(f"设备{dev_index} 未能成功打包日志！！")
            return False
        device_id = Globals.dev_id(dev_index)
        cmd = f"adb -s {device_id} pull /oemdata/case_logs {Globals.log_path()}/{device_id}_{dev_index}"
        tz_cmd = f"adb -s {device_id} pull /tmp/qsee.log {Globals.log_path()}/{device_id}_{dev_index}"
        ret, info = self.execute_common_shell(cmd)
        if "TZ" in Globals.get("CaseName"):
            tz_ret, info = self.execute_common_shell(tz_cmd)
            if not tz_ret:
                sys_log.warning(f"设备{device_id} 未能成功导出TZ日志！！")
                return False
        if not ret:
            sys_log.warning(f"设备{device_id} 未能成功导出日志！！")
            return False
        self.execute_adb_shell("rm /oemdata/case_logs/*", dev_index=dev_index)
        if "TZ" in Globals.get("CaseName"):
            self.execute_adb_shell("rm /tmp/qsee.log", dev_index=dev_index)
        return True

    def get_modem_logs(self, log_tag):
        """ 获取模组日志并存储到本地 """
        module_num = Globals.module_num()
        assert module_num, "未获取到模组数量！"
        case_name = Globals.get("CaseName")
        # 根据测试结果保存日志，PASS 只保存执行日志，FAIL 保存执行日志，app0 日志和 umdp 日志
        if not log_tag:
            log_path = f"{Globals.log_path()}/case_logs/PASS/{case_name}"
        else:
            log_path = f"{Globals.log_path()}/case_logs/FAIL/{case_name}"
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        if re.findall("_IN_|_FN_|_RU_|_IF_", case_name):
            sys_log.debug("抓取测试执行日志并保存")
            self.__pc_get_case_log()
            if "TZ" in case_name:
                for dev_index in range(1, module_num + 1):
                    cmd = "ps -Af | grep '/proc/tzdbg/qsee_log' | awk '{print $1}'"
                    ret, info = self.execute_adb_shell(commands=cmd, dev_index=dev_index)
                    tz_list = info.split("\n")
                    for tz_pid in tz_list:
                        self.execute_adb_shell(commands=f"kill -9 {tz_pid}", dev_index=dev_index)
            if log_tag:
                th_list = []
                for dev_index in range(1, module_num + 1):
                    sys_log.debug(f"抓取设备{dev_index}模组内日志")
                    th = threading.Thread(target=self.__get_log, args=(case_name, log_path, dev_index))
                    th.start()
                    th_list.append(th)
                for i in th_list:
                    i.join()

    def check_poseidon_state(self):
        """检查app状态"""
        module_num = Globals.module_num()
        assert module_num, "未获取到模组数量！"
        for dev_index in range(1, module_num + 1):
            ret, info = self.execute_adb_shell("ps -ef | grep poseidon | grep -v grep", dev_index=dev_index)
            list1 = re.findall(r"poseidon_server 0 (\d+) \d+ /oemdata", info)
            ret, info = self.execute_adb_shell("cat /oemdata/poseidon.conf", dev_index=dev_index)
            result = re.findall(r".*_SERVER=(\w+),(\d+),", info)
            list2 = [i[1] for i in result if i[0] == "TRUE"]
            if list1 != list2:
                self.start_poseidon(dev_index=dev_index)

# -*- coding:utf-8 -*-
import datetime
import os
import random
import re
import time
import urllib
import urllib.request
from typing import Union, List, Optional, Tuple, Dict

from poseidon_module.core.decorators import TraceActionMeta, PoseidonError
from poseidon_module.core.globals import Globals
from poseidon_module.core.logger import sys_log
from poseidon_module.core.poseidon import poseidon
from poseidon_module.utils._device import _Device
from poseidon_module.utils._registry import register


class Device(_Device, metaclass=TraceActionMeta):
    def __init__(self, dev_index: Union[int, str] = 1, pwd: Optional[str] = None):
        super().__init__(dev_index=dev_index, pwd=pwd)
        self.dev_index = dev_index

    def check_adb_status(self, status, interval: int = 1, timeout: int = 18) -> bool:
        """
        获取设备 adb 连接状态
        Args:
            status: 状态： False：判断设备不在 ，True：判断设备在
            interval: 查询间隔
            timeout: 超时时间
        Returns:
            True/False
        """
        return self.__check_device_status(status, interval, timeout, "adb")

    def check_fastboot_status(self, status, interval: int = 1, timeout: int = 18) -> bool:
        """
        获取设备 fastboot 连接状态
        Args:
            status: 状态： False：判断设备不在 ，True：判断设备在
            interval: 查询间隔
            timeout: 超时时间
        Returns:
            True/False
        """
        return self.__check_device_status(status, interval, timeout, "fastboot")

    @property
    def adb_devices(self) -> List[str]:
        """
        获取 adb 设备列表
        Returns:
            设备列表
        """
        ret, info = self.execute_common_shell("adb devices")
        result = re.findall(r"(\w+).*?device", info)
        assert len(result) >= 1, "device id 匹配失败！"
        device_list = result[1:]
        return device_list

    def adb_shell_root(self) -> bool:
        """
        获取设备 root 权限
        Returns:
            True/False
        """
        if self.pwd is None:
            ret, info = self.execute_adb_shell("whoami")
            if ret and "root" in info:
                return True
        cmd = f"adb -s {self.device_id} shell root" if self.pwd is None else f"echo {self.pwd} | adb -s {self.device_id} shell root"
        start_time = time.time()
        while time.time() - start_time < 30:
            self.execute_common_shell(cmd)
            cmd = f"adb -s {self.device_id} wait-for-device"
            sys_log.info(f"{cmd} 等待 adb 连接")
            ret, info = self.execute_common_shell(cmd, timeout=10)
            if not ret:
                continue
            time.sleep(1)
            ret, info = self.execute_adb_shell("whoami")
            if ret and "root" in info:
                return True
            time.sleep(3)
        return False

    def adb_shell_reboot(self, force: bool = True, reboot_timeout: int = 60) -> bool:
        """
        adb 重启模块
        Args:
            force: 是否强制重启
            reboot_timeout: 重启超时时间
        Returns:
            True/False
        """
        try:
            ret, info = self.execute_adb_shell(f"reboot{f' -f' if force else ''}")
            assert ret, f"指令 reboot 执行失败！"
            ret = self.check_adb_status(False, timeout=reboot_timeout)
            assert ret, f"下发 reboot 后 {reboot_timeout} 秒模块未进入重启"
            Globals.set("ServerState", False)
            return True
        except Exception as e:
            sys_log.error(e)
            return False

    def reboot_bootloader(self, reboot_timeout: int = 60) -> bool:
        """
        reboot bootloader 进入fastboot 模式
        Args:
            reboot_timeout: 重启超时时间
        Returns:
            True/False
        """
        try:
            cmd = f"{f'echo {self.pwd} | ' if self.pwd else ''}adb -s {self.device_id} reboot bootloader"
            ret, info = self.execute_common_shell(cmd)
            assert ret, f"指令 {cmd} 执行失败！"
            ret = self.check_fastboot_status(True, timeout=reboot_timeout)
            assert ret, f"下发 reboot 后 {reboot_timeout} 秒模块未进入重启"
            Globals.set("ServerState", False)
            return True
        except Exception as e:
            sys_log.error(e)
            return False

    def fastboot_reboot(self, reboot_timeout: int = 60):
        """
        fastboot 重启模块
        Args:
            reboot_timeout: 重启超时时间
        Returns:
            True/False
        """
        try:
            cmd = f"{f'echo {self.pwd} | ' if self.pwd else ''}fastboot -s {self.device_id} reboot"
            self.execute_common_shell(cmd)
            ret = self.check_fastboot_status(False, timeout=reboot_timeout)
            assert ret, f"下发 reboot 后 {reboot_timeout} 秒模块未进入重启"
            Globals.set("ServerState", False)
            return True
        except Exception as e:
            sys_log.error(e)
            return False

    def check_module_boot_status(self, started_flag: Optional[Union[str, List]] = None, timeout: int = 120) -> bool:
        """
        检查模块启动状态
        Args:
            started_flag: 系统完全可用的标志进程
            timeout: 检测超时时间
        Returns:
            True/False
        """
        try:
            Globals.set("ServerState", False)
            assert self.check_adb_status(True, timeout=timeout), "adb 状态检查失败！"
            assert self.adb_shell_root(), "获取 root 权限失败！"
            if started_flag is not None:
                wait_time = 30
                sys_log.info(f"开始检查设备{self.device_id}：{started_flag}进程是否已启动")
                start_time = time.time()
                while time.time() - start_time < timeout:
                    grep_str = "\" -e \"".join(started_flag) if isinstance(started_flag, list) else started_flag
                    ps_cmd = f"ps -ef | grep -e \"{grep_str}\" | grep -v grep"
                    ret, info = self.execute_adb_shell(ps_cmd)
                    if ret:
                        sys_log.info(
                            f"检测设备{self.device_id}：{started_flag}进程已启动，等待{wait_time}秒后进行后续操作")
                        time.sleep(wait_time)
                        return True
                    time.sleep(5)
                sys_log.error(f"{timeout}秒内未检测设备{self.device_id}：{started_flag}进程，本次开机检查失败！")
                return False
            else:
                wait_time_no_check = 10
                sys_log.info(f"检测设备 [{self.device_id}] adb 枚举，等待{wait_time_no_check}秒后进行操作")
                time.sleep(wait_time_no_check)
                return True
        except Exception as e:
            sys_log.error(e)
            return False

    def set_localtime_in_module(self) -> bool:
        """
        模块和主机时间同步
        :return: 返回布尔型
        """
        try:
            ret, s_time = self.execute_adb_shell("date +%s")
            assert ret, '模块时间查询失败！'
            if 0 <= abs(int(s_time) - time.time()) < 1:  # 小于1s
                return True
            ret, date_type = self.execute_adb_shell("date")
            assert ret, '模块时间查询失败！'
            if "UTC" in date_type:
                localtime = datetime.datetime.now(datetime.timezone.utc)
                localtime = re.findall(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})", str(localtime))[0]
            else:
                localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            cmd = "date -s \'{}\'".format(localtime)
            ret, info = self.execute_adb_shell(cmd)
            return ret
        except Exception as e:
            sys_log.error(e)
            return False

    def poseidon_shortcut_action(self, act_id: int, at_cmd: str = "", check=True):
        """
        执行 poseidon_server 快捷指令
        Args:
            act_id: -h 查看
            at_cmd: AT指令
            check: 是否检查返回值
        Returns:
            True/False，返回执行结果
        """
        app_dir = Globals.get("APP_DIR")
        cmd = f"/{app_dir}/poseidon_server {act_id} {at_cmd}"
        try:
            ret, _ = self.execute_adb_shell(f"ls /{app_dir} | grep poseidon_server")
            assert ret, "poseidon_server 未安装！"
            ret, info = self.execute_adb_shell(cmd)
            if check:
                result = re.findall(r"ret:\s+(\d+)", info, re.S)
                assert result, "未获取到API返回值！"
                assert int(result[0]) == 0, "API执行失败！"
        except Exception as e:
            sys_log.error(e)
            return False, str(e)
        return True, info

    def check_poseidon_online(self, timeout: int = 10) -> bool:
        """ 检查 poseidon_centre 进程是否在线 """
        start_time = time.time()
        while time.time() - start_time < timeout:
            ret, info = self.execute_adb_shell('ps -ef | grep poseidon_centre | grep -v grep')
            if ret:
                Globals.set("ServerState", True)
                return True
            time.sleep(2)
        return False

    def adb_push_poseidon(self, pc_path: str) -> bool:
        """
        adb 推送 poseidon 到模块
        Args:
            pc_path: PC端poseidon路径 如：D:\poseidon_module
        Returns:
            bool: True/False
        """
        file_list = ["killapp.sh", "poseidon.conf", "poseidon.sh", "poseidon_centre", "poseidon_log.conf",
                     "poseidon_server"]
        target_path = "/oemdata"
        self.execute_adb_shell(f"killall -9 poseidon_server")
        self.execute_adb_shell(f"killall -9 poseidon_centre")
        for i, j, k in os.walk(pc_path):
            for file in k:
                if file in file_list:
                    src_file = pc_path + os.sep + file
                    cmd = f"adb -s {self.device_id} push {src_file} {target_path}"
                    ret, info = self.execute_common_shell(cmd)
                    if not ret:
                        sys_log.error(f"push {file} 文件失败！")
                        return False
                    ret, info = self.execute_adb_shell(f"chmod 777 {target_path}/{file}")
                    if not ret:
                        sys_log.error(f"修改{file}文件权限失败！")
                        return False
        self.execute_adb_shell(f"sync")
        return True

    def check_eth_status(self, eth_name: str, state: str, timeout: int = 10) -> bool:
        """
        检测以太网 link 状态
        Args:
            eth_name: 以太网名称 如：eth0
            state: 状态 "yes"/"no"
            timeout: 超时时间
        Returns:
            True/False
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            ret, info = self.execute_adb_shell(f"ethtool {eth_name} | grep Link")
            if ret:
                result = re.findall(r"Link detected:(.*)$", info)
                if result:
                    status = result[0]
                    if state == status.strip():
                        return True
            time.sleep(1)
        return False

    def check_syslog(self, start_time: int, key_words: str, log_path: str = "/oemdata/logs") -> bool:
        """
        检查日志是否有关键字
        Args:
            start_time: 开始时间
            key_words: 关键字 如："poseidon_server"
            log_path: 日志路径 默认为/oemdata/logs
        Returns:
            True/False
        """
        try:
            ret, info = self.execute_adb_shell(f"ls {log_path}")
            assert ret, "log 路径错误！"
            result = re.findall(r"syslog.*current", info)
            assert result, "未检测到syslog!"
            log_file = result[0]
            ret, info = self.execute_adb_shell(f"cat {log_path}/{log_file} | grep '{key_words}'")
            assert ret, f"未检测到任何{key_words}标志"
            info_list = info.split("\n")
            if not info_list:
                return False
            current_year = datetime.datetime.now().year
            for line in info_list:
                result1 = re.findall(r"^(.*?)sa525m", line)
                result2 = re.findall(r"^(.*?)\[UMDP", line)
                if not result1 and not result2:
                    continue
                time_str = result1[0].strip() if result1 else result2[0].strip()
                form = "%Y %b %d %H:%M:%S.%f" if result1 else "%Y %m %d %H:%M:%S.%f"
                time_array = time.strptime(f"{current_year} {time_str}", form)
                timestamp = time.mktime(time_array)
                timestamp = timestamp + 3600 * 8
                if timestamp >= start_time:
                    return True
        except Exception as e:
            sys_log.error(e)
            return False
        return False

    def get_mtd_num(self, part: str) -> Tuple[bool, int]:
        """
        获取分区mtd号
        Args:
            part: 分区名称 如：boot
        Returns:
            元组，第一个元素为 bool，True 表示获取成功，False 表示获取失败；第二个元素为 int，获取到的 mtd 号
        """
        try:
            ret, mtd_info = self.execute_adb_shell(f'cat /proc/mtd | grep -w {part}')
            assert ret, "cat /proc/mtd命令执行失败"
            num = re.findall(r'mtd(\w+):.*?', mtd_info)[0]
            return True, num
        except Exception as e:
            sys_log.error(e)
            return False, -1

    def wait_for_system_boot(self, expect_uptime: int, overtime: bool = False) -> bool:
        """
        系统启动时间检查
        Args:
            expect_uptime: 预期启动时间(秒)
            overtime: 是否允许超时(默认False)
        Returns:
            bool: 是否在预期时间内完成启动
        """
        try:
            start_time = time.time()
            while True:
                ret, info = self.execute_adb_shell(r"cat /proc/uptime | awk '{print int($1)}'")
                current_uptime = int(info)
                if current_uptime >= expect_uptime:
                    sys_log.debug(f"实际启动时间: {current_uptime}s")
                    return True if overtime else False
                remaining = max(1, expect_uptime - current_uptime)
                sys_log.info(f"已启动 {current_uptime}s，剩余等待 {remaining}s")
                if time.time() - start_time > expect_uptime * 1.5:
                    sys_log.warning("等待超时强制终止")
                    return False
                time.sleep(min(remaining, 5))  # 最大休眠5秒避免长阻塞
        except Exception as e:
            sys_log.error(f"检测异常: {str(e)}", exc_info=True)
            return False

    def check_module_file_size(self, file_name: str, check_state: int = 1, times: int = 6) -> bool:
        """
        文件大小变化检测
        Args:
            file_name: 文件绝对路径
            check_state: 1检测变化/0检测不变
            times: 检测次数(默认6次)
        Returns:
            bool: 检测结果是否符合预期
        """
        max_retry = 5  # 最大重试次数
        retry_delay = 2  # 重试间隔(秒)
        check_interval = 10  # 检查间隔(秒)
        try:
            for _ in range(max_retry):
                ret, _ = self.execute_adb_shell(f"[ -f '{file_name}' ] && echo 1 || echo 0")
                if ret and _.strip() == "1":
                    break
                time.sleep(retry_delay)
            else:
                raise FileNotFoundError(f"文件不存在: {file_name}")
            size_history = []
            for _ in range(times):
                ret, size = self.execute_adb_shell(f"stat -c %s '{file_name}' 2>/dev/null || echo 0")
                size_history.append(int(size.strip()))
                unique_sizes = len(set(size_history))
                if check_state == 0 and unique_sizes > 1:
                    return False
                if check_state == 1 and unique_sizes > 1 and len(size_history) >= 2:
                    return True
                time.sleep(check_interval)
            return (len(set(size_history)) == 1) if check_state == 0 else (len(set(size_history)) > 1)
        except Exception as e:
            sys_log.error(f"文件检查失败: {str(e)}", exc_info=True)
            return False

    def modify_config_file_value(self, key: str, value: str, file: str) -> bool:
        """
        修改配置文件 key=value 格式的值
        Args:
            key: 键
            value: 值
            file: 文件路径 如：/oemdata/poseidon.conf
        Returns:
            bool: 修改结果
        """
        try:
            cmd = f"sed -i '/{key}/ s/=.*/={value},\\r/' {file}"
            ret, info = self.execute_adb_shell(cmd)
            assert ret, f"修改 {file} 文件，{key} 失败！"
            for i in range(10):
                sys_log.info(f"第 {i + 1} 次读取配置文件")
                ret, info = self.execute_adb_shell(f"cat {file} | grep {key}")
                if not ret:
                    time.sleep(1)
                    continue
                result = re.findall(rf"{key}.*?(\w+)", info)
                cur_value = result[0]
                assert cur_value == f"{value}", "修改内容未生效"
                break
            else:
                sys_log.error(f"读取 {file} 文件，{key} 失败！")
            return True
        except Exception as e:
            sys_log.error(e)
            return False

    def add_line_to_file(self, words, file):
        """ 新增多行到文件 """
        words = words if isinstance(words, list) else [words]
        for item in words:
            cmd = f'echo {item} >> {file}'
            ret, info = self.execute_adb_shell(cmd)
            if not ret:
                return False
        return True

    def del_line_from_file(self, words, file):
        """ 删除 words 所在的行"""
        words = words if isinstance(words, list) else [words]
        for item in words:
            try:
                cmd = f'grep -n "." {file} | grep {item}'
                ret, info = self.execute_adb_shell(cmd)
                assert ret, f"未找到{file} 文件，{item} 行！"
                colum = info.split(":")[0]
                assert colum.isdigit(), "获取行号失败！"
                cmd = f'sed -i "{colum}d" {file}'
                ret, info = self.execute_adb_shell(cmd)
                assert ret, f"删除{item}行失败！"
            except Exception as e:
                sys_log.error(e)
                return False
        return True

    def execute_tcpdump(self):
        dump_cmd = f'tcpdump -i any -w /{Globals.get("APP_DIR")}/tcpdump.pcap'
        return self.execute_adb_shell_background(dump_cmd, proc_name="tcpdump")

    def start_qcmap_cli(self):
        """单独使用subprocess执行QCMAP_CLI后台运行，不对子进程进行阻塞"""
        return self.execute_adb_shell_background("QCMAP_CLI")

    def module_iperf_server(self):
        """ 模组端开启 iperf3 服务"""
        return self.execute_adb_shell_background("iperf3 -s", proc_name="iperf3")

    @property
    def rndis_name(self) -> str:
        """
        获取指定模块的 RNDIS 网卡名称
        Returns:
             元组，第一个元素为 bool，True 表示获取成功，False 表示获取失败；第二个元素为 str，获取到的 RNDIS 网卡名称
        """
        info_dic = register.regedit_get_module_usb_devices()
        for k, v in info_dic.items():
            if k != self.device_id:
                continue
            rndis_name = [i["description"] for i in v if "NDIS" in i["description"]]
            if not rndis_name:
                sys_log.info(f"注册表中未找到 {self.device_id} 的 rndis 网卡！")
                return ""
            rndis_name = rndis_name[0]
            net_dic_lst = self.__ipconfig_all()
            for net in net_dic_lst:
                if net.get("description") == rndis_name:
                    iface_name = net.get("name")
                    return iface_name
        sys_log.info(f"未找到 {self.device_id} 的 rndis 网卡！")
        return ""

    def set_module_usb_mode_to_rndis(self) -> bool:
        """ 设置模块USB模式为RNDIS模式 """
        try:
            sys_log.info("设置模块USB模式为RNDIS模式")
            default_mode = Globals.get("USBMode")
            if self.__check_rndis():
                return True
            assert self.__remount_app_dir(), "重新挂载App目录失败！"
            ret, _ = self.poseidon_shortcut_action(1, f"AT+GTUSBMODE={default_mode}", check=False)
            assert ret, "设置USB模式失败！"
            ret = self.check_adb_status(False, timeout=3)  # 等待usb端口刷新
            if not ret:  # 模块未重启，需要主动重启使端口组合生效
                assert self.adb_shell_reboot(), "reboot 重启失败！"
                assert self.check_module_boot_status(Globals.get("START_PROCESS"))
            else:
                ret = self.check_adb_status(True, timeout=10)  # 等待 USB 端口重连
                if not ret:  # 10秒后仍未重连成功，认为模块已发生重启，需要检查启动状态
                    assert self.check_module_boot_status(Globals.get("START_PROCESS"))
            return self.__check_rndis()
        except Exception as e:
            sys_log.error(e)
            return False

    def get_target_adapter_info(self, adapter_name: str) -> Dict[str, any]:
        """
        获取指定网卡信息
        Args:
            adapter_name: 网卡名称 eg: 以太网
        Returns:
            字典，包含指定网卡信息
        """
        for net in self.__ipconfig_all():
            if net.get("name").upper() == adapter_name.upper():
                return net
        return {}

    def get_target_ip_addr(self, target_ip: str, adapter_name: str, timeout: int = 10) -> Tuple[bool, str]:
        """
        获取指定模块的指定网卡的 IP 地址
        Args:
            target_ip: 目标iP, 支持部分匹配 eg: 192.168.101.1 or 192.168.101
            adapter_name: 网卡名称 eg: 以太网
            timeout: 检测超时时间
        Returns:
            元组，第一个元素为 bool，True 表示获取成功，False 表示获取失败；第二个元素为 str，获取到的 IP 地址
        """
        adapter_info = {}
        start_time = time.time()
        while time.time() - start_time < timeout:
            adapter_info = self.get_target_adapter_info(adapter_name)
            cur_ip = adapter_info.get("ipv4", "")
            if cur_ip and target_ip in cur_ip:
                return True, cur_ip
            time.sleep(3)
        sys_log.warning(f"超时未匹配到目标IP，最后获取信息: {adapter_info}")
        return False, ""

    def __set_module_env_for_wlan(self):
        """ 设置模块静态IP环境 """
        try:
            gw = Globals.get("DEV_GW")
            assert self.set_module_usb_mode_to_rndis(), "设置模块USB模式为RNDIS模式失败！"
            iface_name = self.rndis_name
            assert iface_name, f"获取 {self.device_id} 网卡名称失败！"
            prefix = ".".join(gw.split(".")[:-1])
            ret, cur_ip = self.get_target_ip_addr(prefix, iface_name, timeout=1)
            tmp_list = []
            if not ret:
                Globals.set("ServerState", False)
                ip_list = self.__rndis_ips()
                for ip in ip_list:
                    if re.findall(prefix, ip):
                        tmp_list.append(int(ip.split(".")[-1]))
                cur_ip = f"{prefix}.{random.choice(list(set(range(10, 100)) - set(tmp_list)))}"
                ret = self.set_static_ip_addr(iface_name, cur_ip, "255.255.255.0", gw)
                assert ret, "静态IP设置失败！"
                time.sleep(3)
            assert isinstance(self.dev_index, int), "绑定设备时dev_index必须为整型！"
            Globals.set_module("dev_ip", cur_ip, self.dev_index)
        except Exception as e:
            raise PoseidonError(f"设置模块环境失败！{e}")

    def start_poseidon(self):
        """ 启动Poseidon """
        app_dir = Globals.get("APP_DIR")
        cmd = f"/{app_dir}/poseidon.sh"
        try:
            assert self.__remount_app_dir(), "重新挂载App目录失败！"
            ret, info = self.execute_adb_shell_background(cmd, proc_name="poseidon_centre")
            assert ret, "Poseidon启动失败！"
            assert isinstance(self.dev_index, int), "与Poseidon通信时dev_index必须为整型！"
            assert poseidon.handshake_to_poseidon(dev_index=self.dev_index), "Poseidon handshake失败！"
        except Exception as e:
            raise PoseidonError(f"启动Poseidon失败！{e}")

    def setup_env(self, start_app: bool = True) -> bool:
        """
        设置测试环境, 包括 1 root权限，2 设置时间，3 启动Poseidon
        Args:
            start_app: 是否启动Poseidon
        Returns:
            bool: True 成功，False 失败
        """
        Globals.set("ServerState", False)
        try:
            assert self.check_adb_status(True, 1, timeout=3), "设备未启动！"
            assert self.adb_shell_root(), "root权限获取失败！"
            assert self.set_localtime_in_module(), "时间同步失败！"
            if start_app:
                self.__set_module_env_for_wlan()
                if self.check_poseidon_online(timeout=1):
                    assert isinstance(self.dev_index, int), "与Poseidon通信时dev_index必须为整型！"
                    if poseidon.handshake_to_poseidon(dev_index=self.dev_index):
                        return True
                self.start_poseidon()
            return True
        except Exception as e:
            sys_log.error(e)
            return False

    @property
    def wifi_channel_lst(self):
        """ 查看信道列表 """
        try:
            ret, info = self.execute_adb_shell("iw list")
            assert ret, "下发 iw list 指令失败"
            result = re.findall(r"\[(\d+)] \(\d+\.\d dBm\)", info, re.S)
            result = [int(i) for i in result]
            channel_lst1 = [i for i in result if i < 15]
            channel_lst2 = [i for i in result if i > 14]
            return True, channel_lst1, channel_lst2
        except Exception as e:
            sys_log.error(e)
            return False, None, None

    def wifi_check_mac(self, iface_name):
        """ 检查 wifi mac 地址 """
        try:
            ret, info = self.execute_adb_shell(f"ifconfig {iface_name}")
            assert ret, f"ifconfig {iface_name} 指令下发失败！"
            result = re.findall(r"HWaddr (.+:.+:.+:.+:.+:..)\n", info, re.S)
            assert result, "未匹配到正确的 mac 地址"
            mac = result[0]
            header = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/63.0.3239.132 Safari/537.36'}
            url = f"https://mac.51240.com/{mac}__mac/"
            req = urllib.request.Request(url, headers=header)
            res = urllib.request.urlopen(req)
            cont = res.read().decode()
            pattern = re.compile('组织名称</td>\n<td .*?>(.*?)</td>')
            items = re.findall(pattern, str(cont))
            assert items, "未匹配到正确的名称！"
            return True, items[0]
        except Exception as e:
            sys_log.error(e)
            return False, ""

    def check_wifi_hostapd_or_wap_proc(self, tag):
        cmd = f"pgrep {tag}"
        ret, info = self.execute_adb_shell(cmd)
        if ret:
            if len(info.split("\n")) == 2:
                return True
        return False

    def check_wifi_hostapd_and_wap_recovery(self, tag, timeout):
        """
        检查hostapd 和 wap 恢复机制
        :param tag: 0 —— wpa 1——hostapd 2 ——wap & hostapd
        :param timeout: 检查超时时间
        :return: True / False
        """
        start_time = time.time()
        while time.time() - start_time <= timeout:
            ret1 = self.check_wifi_hostapd_or_wap_proc("wpa")
            ret2 = self.check_wifi_hostapd_or_wap_proc("hostapd")
            if tag == 0:
                if ret1:
                    return True
            elif tag == 1:
                if ret2:
                    return True
            elif tag == 2:
                if ret1 and ret2:
                    return True
            else:
                return False
            time.sleep(2)
        return False

    def check_device_all_usb_alive(self, ports):
        """ 通过注册表检查指定的端口组合存在与否 """
        info_list = self.__get_modem_usb_device()
        if len(info_list) != len(ports):
            return False
        info_list = [i["description"] for i in info_list]
        for port in ports:
            tmp_list = [i for i in info_list if port.upper() in i.upper()]
            if not tmp_list:
                sys_log.error(f"未发现{port}端口！")
                return False
        return True

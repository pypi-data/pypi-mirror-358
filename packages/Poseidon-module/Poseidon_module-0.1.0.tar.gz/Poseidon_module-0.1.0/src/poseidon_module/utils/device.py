# -*- coding:utf-8 -*-
import datetime
import os
import re
import time
from typing import Union, List, Optional

from poseidon_module.core.decorators import TraceActionMeta
from poseidon_module.core.globals import Globals
from poseidon_module.core.logger import sys_log
from poseidon_module.core.shell import Shell


class UtilDevice(Shell, metaclass=TraceActionMeta):
    def __init__(self):
        super().__init__()

    def __check_device_status(self, status: bool, interval: int = 1, timeout: int = 60 * 3, dev_type: str = "adb",
                              dev_index: Union[int, str] = 1) -> bool:
        """检查设备状态"""
        device_id = dev_index if isinstance(dev_index, str) else Globals.get_module("dev_id", dev_index)
        start_time = time.time()
        while time.time() - start_time < timeout:
            time.sleep(interval)
            ret, info = self.execute_common_shell(f"{dev_type} devices")
            if not ret:
                continue
            state = bool(re.search(rf"{device_id}.*?{dev_type if dev_type == 'fastboot' else 'device'}", info, re.S))
            if state == status:
                return True
        sys_log.debug(f"设备 {device_id} 未在 {timeout} 秒内{'连接' if status else '断开'}")
        return False

    def check_adb_status(self, status, interval: int = 1, timeout: int = 18,
                         dev_index: Union[int, str] = 1) -> bool:
        """
        获取设备 adb 连接状态
        Args:
            status: 状态： False：判断设备不在 ，True：判断设备在
            interval: 查询间隔
            timeout: 超时时间
            dev_index: device id(设备ID) or device index(设备绑定编号)
        Returns:
            True/False
        """
        return self.__check_device_status(status, interval, timeout, "adb", dev_index)

    def check_fastboot_status(self, status, interval: int = 1, timeout: int = 18,
                              dev_index: Union[int, str] = 1) -> bool:
        """
        获取设备 fastboot 连接状态
        Args:
            status: 状态： False：判断设备不在 ，True：判断设备在
            interval: 查询间隔
            timeout: 超时时间
            dev_index: device id(设备ID) or device index(设备绑定编号)
        Returns:
            True/False
        """
        return self.__check_device_status(status, interval, timeout, "fastboot", dev_index)

    def get_devices(self) -> List[str]:
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

    def adb_shell_root(self, dev_index: Union[int, str] = 1) -> bool:
        """
        获取设备 root 权限
        Args:
            dev_index: device id(设备ID) or device index(设备绑定编号)
        Returns:
            True/False
        """
        pwd, device_id = Globals.pwd(dev_index), Globals.dev_id(dev_index)
        if pwd is None:
            ret, info = self.execute_adb_shell("whoami", dev_index=dev_index)
            if ret and "root" in info:
                return True
        cmd = f"adb -s {device_id} shell root" if pwd is None else f"echo {pwd} | adb -s {device_id} shell root"
        start_time = time.time()
        while time.time() - start_time < 30:
            self.execute_common_shell(cmd)
            cmd = f"adb -s {device_id} wait-for-device"
            sys_log.info(f"{cmd} 等待 adb 连接")
            ret, info = self.execute_common_shell(cmd, timeout=10)
            if not ret:
                continue
            time.sleep(1)
            ret, info = self.execute_adb_shell("whoami", dev_index=dev_index)
            if ret and "root" in info:
                return True
            time.sleep(3)
        return False

    def adb_shell_reboot(self, force: bool = True, reboot_timeout: int = 60, dev_index: Union[int, str] = 1):
        """
        adb 重启模块
        Args:
            force: 是否强制重启
            reboot_timeout: 重启超时时间
            dev_index: device id(设备ID) or device index(设备绑定编号)
        Returns:
            True/False
        """
        try:
            ret, info = self.execute_adb_shell(f"reboot{f' -f' if force else ''}", dev_index=dev_index)
            assert ret, f"指令 reboot 执行失败！"
            ret = self.check_adb_status(False, timeout=reboot_timeout, dev_index=dev_index)
            assert ret, f"下发 reboot 后 {reboot_timeout} 秒模块未进入重启"
            Globals.set("ServerState", False)
            return True
        except Exception as e:
            sys_log.error(e)
            return False

    def reboot_bootloader(self, reboot_timeout: int = 60, dev_index: Union[int, str] = 1) -> bool:
        """
        reboot bootloader 进入fastboot 模式
        Args:
            reboot_timeout: 重启超时时间
            dev_index: device id(设备ID) or device index(设备绑定编号)
        Returns:
            True/False
        """
        try:
            pwd, device_id = Globals.pwd(dev_index), Globals.dev_id(dev_index)
            cmd = f"{f'echo {pwd} | ' if pwd else ''}adb -s {device_id} reboot bootloader"
            ret, info = self.execute_common_shell(cmd)
            assert ret, f"指令 {cmd} 执行失败！"
            ret = self.check_fastboot_status(True, timeout=reboot_timeout, dev_index=dev_index)
            assert ret, f"下发 reboot 后 {reboot_timeout} 秒模块未进入重启"
            Globals.set("ServerState", False)
            return True
        except Exception as e:
            sys_log.error(e)
            return False

    def fastboot_reboot(self, reboot_timeout: int = 60, dev_index: Union[int, str] = 1):
        """
        fastboot 重启模块
        Args:
            reboot_timeout: 重启超时时间
            dev_index: device id(设备ID) or device index(设备绑定编号)
        Returns:
            True/False
        """
        try:
            pwd, device_id = Globals.pwd(dev_index), Globals.dev_id(dev_index)
            cmd = f"{f'echo {pwd} | ' if pwd else ''}fastboot -s {device_id} reboot"
            self.execute_common_shell(cmd)
            ret = self.check_fastboot_status(False, timeout=reboot_timeout, dev_index=dev_index)
            assert ret, f"下发 reboot 后 {reboot_timeout} 秒模块未进入重启"
            Globals.set("ServerState", False)
            return True
        except Exception as e:
            sys_log.error(e)
            return False

    def check_module_boot_status(self, started_flag: Optional[Union[str, List]] = None, timeout: int = 120,
                                 dev_index: Union[int, str] = 1) -> bool:
        """
        检查模块启动状态
        Args:
            started_flag: 系统完全可用的标志进程
            timeout: 检测超时时间
            dev_index: device id(设备ID) or device index(设备绑定编号)
        Returns:
            True/False
        """
        try:
            Globals.set("ServerState", False)
            assert self.check_adb_status(True, timeout=timeout, dev_index=dev_index), "adb 状态检查失败！"
            assert self.adb_shell_root(dev_index=dev_index), "获取 root 权限失败！"
            if started_flag is not None:
                wait_time = 30
                sys_log.info(f"开始检查设备{dev_index}：{started_flag}进程是否已启动")
                start_time = time.time()
                while time.time() - start_time < timeout:
                    grep_str = "\" -e \"".join(started_flag) if isinstance(started_flag, list) else started_flag
                    ps_cmd = f"ps -ef | grep -e \"{grep_str}\" | grep -v grep"
                    ret, info = self.execute_adb_shell(ps_cmd, dev_index=dev_index)
                    if ret:
                        sys_log.info(f"检测设备{dev_index}：{started_flag}进程已启动，等待{wait_time}秒后进行后续操作")
                        time.sleep(wait_time)
                        return True
                    time.sleep(5)
                sys_log.error(f"{timeout}秒内未检测设备{dev_index}：{started_flag}进程，本次开机检查失败！")
                return False
            else:
                wait_time_no_check = 10
                sys_log.info(f"检测设备 [{dev_index}] adb 枚举，等待{wait_time_no_check}秒后进行操作")
                time.sleep(wait_time_no_check)
                return True
        except Exception as e:
            sys_log.error(e)
            return False

    def set_localtime_in_module(self, dev_index: Union[int, str] = 1) -> bool:
        """
        模块和主机时间同步
        :param dev_index: 设备序号
        :return: 返回布尔型
        """
        try:
            ret, s_time = self.execute_adb_shell("date +%s", dev_index)
            assert ret, '模块时间查询失败！'
            if 0 <= abs(int(s_time) - time.time()) < 1:  # 小于1s
                return True
            ret, date_type = self.execute_adb_shell("date", dev_index)
            assert ret, '模块时间查询失败！'
            if "UTC" in date_type:
                localtime = datetime.datetime.now(datetime.timezone.utc)
                localtime = re.findall(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})", str(localtime))[0]
            else:
                localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            cmd = "date -s \'{}\'".format(localtime)
            ret, info = self.execute_adb_shell(cmd, dev_index)
            return ret
        except Exception as e:
            sys_log.error(e)
            return False

    def poseidon_shortcut_action(self, act_id: int, at_cmd: str = "", dev_index: Union[int, str] = 1, check=True):
        """
        执行 poseidon_server 快捷指令
        Args:
            act_id: -h 查看
            at_cmd: AT指令
            dev_index: device id(设备ID) or device index(设备绑定编号)
            check: 是否检查返回值
        Returns:
            True/False，返回执行结果
        """
        app_dir = Globals.get("APP_DIR")
        cmd = f"/{app_dir}/poseidon_server {act_id} {at_cmd}"
        try:
            ret, _ = self.execute_adb_shell(f"ls /{app_dir} | grep poseidon_server", dev_index=dev_index)
            assert ret, "poseidon_server 未安装！"
            ret, info = self.execute_adb_shell(cmd, dev_index=dev_index)
            if check:
                result = re.findall(r"ret:\s+(\d+)", info, re.S)
                assert result, "未获取到API返回值！"
                assert int(result[0]) == 0, "API执行失败！"
        except Exception as e:
            sys_log.error(e)
            return False, str(e)
        return True, info

    def check_poseidon_online(self, timeout: int = 10, dev_index: Union[int, str] = 1) -> bool:
        start_time = time.time()
        while time.time() - start_time < timeout:
            ret, info = self.execute_adb_shell('ps -ef | grep poseidon_centre | grep -v grep', dev_index)
            if ret:
                Globals.set("ServerState", True)
                return True
            time.sleep(2)
        return False

    def adb_push_app_to_module(self, pc_path, dev_index=1):
        file_list = ["killapp.sh", "poseidon.conf", "poseidon.sh", "poseidon_centre", "poseidon_log.conf",
                     "poseidon_server"]
        device_id = Globals.dev_id(dev_index)
        target_path = "/oemdata"
        self.execute_adb_shell(f"killall -9 poseidon_server", dev_index=dev_index)
        self.execute_adb_shell(f"killall -9 poseidon_centre", dev_index=dev_index)
        for i, j, k in os.walk(pc_path):
            for file in k:
                if file in file_list:
                    src_file = pc_path + os.sep + file
                    cmd = f"adb -s {device_id} push {src_file} {target_path}"
                    ret, info = self.execute_common_shell(cmd)
                    if not ret:
                        sys_log.error(f"push {file} 文件失败！")
                        return False
                    ret, info = self.execute_adb_shell(f"chmod 777 {target_path}/{file}", dev_index=dev_index)
                    if not ret:
                        sys_log.error(f"修改{file}文件权限失败！")
                        return False
        self.execute_adb_shell(f"sync")
        return True

    def check_eth_status(self, eth_name, state, timeout=10, dev_index=1):
        """ 检测以太网 link 状态 """
        start_time = time.time()
        while time.time() - start_time < timeout:
            ret, info = self.execute_adb_shell(f"ethtool {eth_name} | grep Link", dev_index)
            if ret:
                result = re.findall(r"Link detected:(.*)$", info)
                if result:
                    status = result[0]
                    if state == status.strip():
                        return True
            time.sleep(1)
        return False

    def check_syslog(self, start_time, key_words, log_path="/oemdata/logs", dev_index=1):
        try:
            ret, info = self.execute_adb_shell(f"ls {log_path}", dev_index)
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

    def get_mtd_num(self, part, dev_index=1):
        """获取分区mtd号"""
        try:
            ret, mtd_info = self.execute_adb_shell(f'cat /proc/mtd | grep -w {part}', dev_index)
            assert ret, "cat /proc/mtd命令执行失败"
            num = re.findall(r'mtd(\w+):.*?', mtd_info)[0]
            return True, num
        except Exception as e:
            sys_log.error(e)
            return False, -1

    def wait_for_system_boot(self, expect_uptime, overtime=False, dev_index=1):
        """
        系统启动时间检查
        Args:
            expect_uptime: 预期启动时间(秒)
            overtime: 是否允许超时(默认False)
            dev_index: 设备索引
        Returns:
            bool: 是否在预期时间内完成启动
        """
        try:
            start_time = time.time()
            while True:
                ret, info = self.execute_adb_shell(r"cat /proc/uptime | awk '{print int($1)}'", dev_index=dev_index)
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

    def check_module_file_size(self, file_name, check_state=1, times=6, dev_index=1):
        """
        文件大小变化检测
        Args:
            file_name: 文件绝对路径
            check_state: 1检测变化/0检测不变
            times: 检测次数(默认6次)
            dev_index: 设备索引
        Returns:
            bool: 检测结果是否符合预期
        """
        max_retry = 5  # 最大重试次数
        retry_delay = 2  # 重试间隔(秒)
        check_interval = 10  # 检查间隔(秒)
        try:
            for _ in range(max_retry):
                ret, _ = self.execute_adb_shell(f"[ -f '{file_name}' ] && echo 1 || echo 0", dev_index=dev_index)
                if ret and _.strip() == "1":
                    break
                time.sleep(retry_delay)
            else:
                raise FileNotFoundError(f"文件不存在: {file_name}")
            size_history = []
            for _ in range(times):
                ret, size = self.execute_adb_shell(f"stat -c %s '{file_name}' 2>/dev/null || echo 0",
                                                   dev_index=dev_index)
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

    def modify_config_file_value(self, key, value, file, dev_index=1):
        """ 修改key=value 格式的文件 value 值"""
        try:
            cmd = f"sed -i '/{key}/ s/=.*/={value},\\r/' {file}"
            ret, info = self.execute_adb_shell(cmd, dev_index=dev_index)
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

    def add_line_to_file(self, words, file, dev_index=1):
        """ 新增多行到文件 """
        words = words if isinstance(words, list) else [words]
        for item in words:
            cmd = f'echo {item} >> {file}'
            ret, info = self.execute_adb_shell(cmd, dev_index=dev_index)
            if not ret:
                return False
        return True

    def del_line_from_file(self, words, file, dev_index=1):
        """ 删除 words 所在的行"""
        words = words if isinstance(words, list) else [words]
        for item in words:
            try:
                cmd = f'grep -n "." {file} | grep {item}'
                ret, info = self.execute_adb_shell(cmd, dev_index=dev_index)
                assert ret, f"未找到{file} 文件，{item} 行！"
                colum = info.split(":")[0]
                assert colum.isdigit(), "获取行号失败！"
                cmd = f'sed -i "{colum}d" {file}'
                ret, info = self.execute_adb_shell(cmd, dev_index=dev_index)
                assert ret, f"删除{item}行失败！"
            except Exception as e:
                sys_log.error(e)
                return False
        return True

    def execute_tcpdump(self, dev_index: Union[int, str] = 1):
        dump_cmd = f'tcpdump -i any -w /{Globals.get("APP_DIR")}/tcpdump.pcap'
        return self.execute_adb_shell_background(dump_cmd, proc_name="tcpdump", dev_index=dev_index)

    def start_qcmap_cli(self, dev_index: Union[int, str] = 1):
        """单独使用subprocess执行QCMAP_CLI后台运行，不对子进程进行阻塞"""
        return self.execute_adb_shell_background("QCMAP_CLI", dev_index=dev_index)

    def module_iperf_server(self, dev_index: Union[int, str] = 1):
        """ 模组端开启 iperf3 服务"""
        return self.execute_adb_shell_background("iperf3 -s", proc_name="iperf3", dev_index=dev_index)

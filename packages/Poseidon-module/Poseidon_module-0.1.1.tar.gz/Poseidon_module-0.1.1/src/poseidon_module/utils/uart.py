#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import re
import string
import threading
import time
from queue import Queue
from typing import Tuple, List, Dict, Union

from poseidon_module.core.decorators import trace_action
from poseidon_module.core.globals import Globals
from poseidon_module.core.logger import sys_log, log_manager
from serial import Serial, SerialException


class Uart(Serial):
    _instances = {}
    _lock = threading.Lock()

    def __new__(cls, port: str, *args, **kwargs):
        if port not in cls._instances:
            with cls._lock:
                if port not in cls._instances:
                    instance = super().__new__(cls)
                    instance._initialized = False
                    cls._instances[port] = instance
        return cls._instances[port]

    def __init__(self, port: str, baudrate: int = 115200, timeout: int = 1):
        if not self._initialized:
            super().__init__(port=port, baudrate=baudrate, timeout=timeout)
            self._port_lock = threading.RLock()
            self._threads = []
            self._queues = {self.port: (Queue(), Queue())}  # 初始化队列 0: 串口接收队列 1: 串口数据处理队列
            self._running = True
            self._start_threads()  # 启动工作线程
            self._initialized = True

    def _start_threads(self):
        """安全启动工作线程"""
        threads = [
            threading.Thread(target=self.__debug_read_always, daemon=True),
            threading.Thread(target=self.__get_ser_data, daemon=True)
        ]
        [t.start() for t in threads]

    def __clear_queue(self):
        while not self._queues[self.port][1].empty():
            self._queues[self.port][1].get()

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self._port_lock:
            self._running = False
        self.close()
        Uart._instances.pop(self.port, None)

    def __get_ser_data(self):
        serial_log = log_manager.register_logger("SerialLog", log_to_console=False)
        read_buf = ""  # 本地缓存
        sys_log.debug(f"{self.port} 开始存日志")
        while True:
            if not self._running:
                break
            if not Globals.get("CheckDebug"):
                self.__clear_queue()
            if self._queues[self.port][0].empty():
                time.sleep(0.1)
                continue
            data = self._queues[self.port][0].get()
            read_buf += data
            # 处理换行符
            if any(eol in read_buf for eol in ("\n\r", "\r\n")):
                lines = re.split(r"[\r\n]+", read_buf)
                read_buf = lines.pop() if not (read_buf.endswith("\n\r") or read_buf.endswith("\r\n")) else ""
                # 处理每一行数据
                for line in lines:
                    clean_line = re.sub(r'\x1b\[.*?m', '', line).strip()
                    if clean_line:
                        serial_log.debug(clean_line)
                        if Globals.get("CheckDebug"):
                            self._queues[self.port][1].put(clean_line)
        sys_log.debug(f"{self.port} 停止存日志")

    def __debug_read_always(self):
        """持续串口读取线程"""
        retry_count = 0
        max_retries = 10
        while True:
            if not self._running:
                break
            try:
                if self.in_waiting > 0:
                    b_data = self.read(self.in_waiting)
                    data = b_data.decode("ISO-8859-1", errors="replace")
                    self._queues[self.port][0].put(data)
                    retry_count = 0  # 成功读取重置重试计数
            except SerialException as e:
                sys_log.warning(f"串口通信异常: {str(e)}")
                retry_count += 1
                if retry_count > max_retries:
                    sys_log.critical("达到最大重试次数，终止读取线程")
                    break
                try:
                    if self.is_open:
                        self.close()
                    self.open()
                    sys_log.info(f"串口重连成功 (尝试 {retry_count}/{max_retries})")
                except Exception as reconnect_error:
                    sys_log.warning(f"重连失败: {str(reconnect_error)}")
                    time.sleep(2 ** retry_count)  # 指数退避
            except Exception as e:
                sys_log.critical(f"不可恢复错误: {str(e)}")
                break
            finally:
                time.sleep(0.01)  # 防止CPU占用过高

    @trace_action
    def serial_check_sleep_status(self, timeout: int = 60) -> bool:
        """优化版休眠状态检测
        Args:
            timeout: 总检测超时(秒)
        Returns:
            bool: 是否成功进入休眠
        """
        check_interval = 0.1  # 队列检查间隔
        sleep_confirm_duration = 10  # 休眠确认时长
        try:
            Globals.set("CheckDebug", True)
            sleep_flag = Globals.get("SLEEP_FLAG")
            sys_log.info(f"开始检测休眠标志[{sleep_flag}]，超时:{timeout}s")
            detection_start = time.monotonic()
            sleep_start = -1.0
            while time.monotonic() - detection_start <= timeout:
                if sleep_start > 0 and time.monotonic() - sleep_start >= sleep_confirm_duration:
                    sys_log.info(f"休眠确认完成(持续{sleep_confirm_duration}s)")
                    Globals.set("CheckDebug", False)
                    return True
                if not self._queues[self.port][1].empty():
                    data = self._queues[self.port][1].get_nowait()
                    if sleep_flag in data:
                        sleep_start = time.monotonic()
                        sys_log.info(f"捕获休眠标志[{sleep_flag}]")
                time.sleep(check_interval)
            sys_log.warning(f"检测超时(未捕获休眠标志)")
        except Exception as e:
            sys_log.error(f"检测异常: {str(e)}")
        Globals.set("CheckDebug", False)
        return False

    @trace_action
    def serial_stat_abnormal_wakeup(self, sleep_time=180):
        """
        统计异常唤醒次数
        :return: None
        """
        pass

    @trace_action
    def serial_check_wakeup_status(self, timeout: int = 30) -> bool:
        """
        唤醒状态检测
        Args:
            timeout: 检测超时时间(秒)
        Returns:
            bool: 是否成功检测到唤醒标志
        """
        check_interval = 0.05
        try:
            Globals.set("CheckDebug", True)
            wakeup_flag = Globals.get("WAKEUP_FLAG")
            sys_log.info(f"启动唤醒检测[标志:{wakeup_flag}] 超时:{timeout}s")
            detection_start = time.monotonic()
            while time.monotonic() - detection_start <= timeout:
                if not self._queues[self.port][1].empty():
                    data = self._queues[self.port][1].get_nowait()
                    if wakeup_flag in data:
                        sys_log.info(f"成功捕获唤醒标志 | 耗时:{time.monotonic() - detection_start:.2f}s")
                        Globals.set("CheckDebug", False)
                        return True
                time.sleep(check_interval)
            sys_log.warning(f"唤醒检测超时 | 实际等待:{time.monotonic() - detection_start:.2f}s")
        except Exception as e:
            sys_log.error(f"唤醒检测异常: {str(e)}")
        Globals.set("CheckDebug", False)
        return False

    @trace_action
    def serial_check_sleep_status_no_debug(self, timeout=60):
        """ debug 口无休眠日志打印的情况使用 ，休眠状态下开关机的用例外不推荐 """
        start_sleep_time = time.time()
        while time.time() - start_sleep_time < timeout:
            time.sleep(5)
            ret, info = self.serial_send_shell_cmd("\r\n", 10)
            if not ret:
                return True
        sys_log.error(f"超过 {timeout} 秒模块没有休眠！")
        return False

    @trace_action
    def serial_send_shell_cmd(self, cmd: str, timeout: int = 3) -> Tuple[bool, str]:
        """优化版串口Shell命令执行
        Args:
            cmd: 要执行的命令字符串
            timeout: 超时时间(秒)
        Returns:
            tuple: (执行状态, 返回文本)
        """
        check_interval = 0.05  # 更精细的检查间隔
        shell_return = []
        try:
            Globals.set("CheckDebug", True)
            if cmd == "\r\n":
                end_tag = "#"
            else:
                end_tag = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                cmd = f"{cmd.strip()} && echo {end_tag}\r\n"
            sys_log.debug(f"发送Shell命令: {cmd.strip()}")
            self.write(cmd.encode("utf-8"))
            start_time = time.monotonic()
            while time.monotonic() - start_time <= timeout:
                if not self._queues[self.port][1].empty():
                    line = self._queues[self.port][1].get_nowait()
                    shell_return.append(line)
                    if end_tag in line and (cmd.strip() not in line if cmd.strip() else True):
                        result = "\n".join(shell_return[1:-1]) if len(shell_return) >= 2 else "\n".join(shell_return)
                        sys_log.debug(f"返回结果: {result}")
                        sys_log.info(f"命令执行成功 | 耗时:{time.monotonic() - start_time:.3f}s")
                        Globals.set("CheckDebug", False)
                        return True, result
                time.sleep(check_interval)
            sys_log.warning(f"命令执行超时 | 耗时:{timeout}s")
        except Exception as e:
            sys_log.error(f"命令执行异常: {str(e)}")
        Globals.set("CheckDebug", False)
        result = "\n".join(shell_return)
        sys_log.debug(f'返回结果: {result}')
        return False, result

    @trace_action
    def serial_load_linux(self, root_name: str = "root", pwd: str = "oelinux123") -> bool:
        """
        通过串口登录Linux系统
        Args:
            root_name: 用户名（默认root）
            pwd: 密码（默认oelinux123）
        Returns:
            bool: 登录是否成功
        """
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                sys_log.debug(f"尝试登录（第{attempt}次）")
                ret, info = self.serial_send_shell_cmd("\r\n", 3)
                if ret:
                    sys_log.debug("已处于登录状态")
                    return True
                if "login" not in info.lower():
                    sys_log.warning(f"未找到登录提示，当前输出: {info.strip()}")
                    time.sleep(2)
                    continue
                sys_log.debug(f"输入用户名: {root_name}")
                self.write(f"{root_name}\r\n".encode("utf-8"))
                time.sleep(1)
                sys_log.debug("输入密码")
                self.write(f"{pwd}\r\n".encode("utf-8"))
                ret, _ = self.serial_send_shell_cmd("\r\n", 3)
                if ret:
                    sys_log.info("登录成功")
                    return True
            except Exception as e:
                sys_log.error(f"登录失败（尝试{attempt}次）: {str(e)}")
                time.sleep(2)
        sys_log.error(f"登录失败，已达最大尝试次数{max_retries}")
        return False

    @staticmethod
    def _process_line(line: str, check_list: List[str], ret_dict: Dict[str, float], rematch_mode: int):
        """处理单行数据并更新检测结果"""
        for item in check_list:
            if item in ret_dict:
                continue
            matched = (item in line if rematch_mode == 0 else re.findall(item, line))
            if matched:
                sys_log.info(f"找到关键字: {item}")
                ret_dict[item] = time.time()

    @staticmethod
    def _check_conditions(check_list: List[str], ret_dict: Dict[str, float],
                          start_time: float, check_mode: int) -> Union[Tuple[bool, List[float]], None]:
        """检查是否满足返回条件"""
        if not ret_dict:
            return None
        # 模式0: 检测到任意一个关键字
        if check_mode == 0:
            time_list = [ret_dict.get(i, None) - start_time if i in ret_dict else None for i in check_list]
            return True, time_list
        # 需要检测所有关键字的情况
        if len(ret_dict) == len(check_list):
            check_time = [ret_dict[i] - start_time for i in check_list]
            # 模式1: 按顺序检测
            if check_mode == 1:
                return (check_time == sorted(check_time)), check_time
            # 模式2: 不按顺序检测
            if check_mode == 2:
                return True, check_time
        return None

    @staticmethod
    def _generate_final_result(check_list: List[str], ret_dict: Dict[str, float], start_time: float
                               ) -> Tuple[bool, List[float]]:
        """生成最终结果"""
        time_list = [ret_dict[word] - start_time if word in ret_dict else -1 for word in check_list]
        Globals.set("CheckDebug", False)
        return False, time_list

    @trace_action
    def check_keywords(self, keyword: Union[str, List[str]], timeout: int = 60, check_mode: int = 0,
                       rematch_mode: int = 0) -> Tuple[bool, List[float]]:
        """
        串口关键字检测方法
        参数:
            keyword: 要检测的关键字(字符串或列表)
            timeout: 超时时间(秒)
            check_mode: 检测模式(0-任意一个,1-按顺序多个,2-不按顺序多个)
            dev_index: 设备索引
            rematch_mode: 正则匹配模式(0-普通匹配,1-正则匹配)
        返回:
            (检测结果, 各关键字检测时间列表)
        """
        Globals.set("CheckDebug", True)
        check_list = [keyword] if isinstance(keyword, str) else keyword
        ret_dict = {}
        sys_log.debug(f"开始检测关键字: {check_list}")
        start_time = time.time()
        while time.time() - start_time <= timeout:
            if self._queues[self.port][1].empty():
                time.sleep(0.1)
                continue
            line = self._queues[self.port][1].get()
            self._process_line(line, check_list, ret_dict, rematch_mode)
            result = self._check_conditions(check_list, ret_dict, start_time, check_mode)
            if result is not None:
                Globals.set("CheckDebug", False)
                return result
        return self._generate_final_result(check_list, ret_dict, start_time)


def debug_ser(dev_index: int):
    return Uart(Globals.debug_port(dev_index), baudrate=Globals.get("BAUD_RATE"), timeout=1)

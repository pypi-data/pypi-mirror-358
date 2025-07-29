#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from typing import Tuple, Optional, List, Dict, Union

import serial
import time, binascii
from poseidon_module.core.globals import Globals
from poseidon_module.core.logger import sys_log
from poseidon_module.core.decorators import TraceActionMeta
from poseidon_module.utils.atb import UtilATB
import poseidon_module.utils.comm as comm


class UtilUart(metaclass=TraceActionMeta):

    def __init__(self):
        self.sleep_timeout = 60
        self.wakeup_timeout = 60
        self.check_timeout = 60
        self.lc_atb = UtilATB()

    @staticmethod
    def _serial_read(ser_obj, timeout):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if ser_obj.in_waiting:
                data = ser_obj.read(ser_obj.in_waiting)
                return data
        return b""

    def _read_re_cmd_return(self, start_time, ser_obj, data_len):
        response = b""
        while time.time() - start_time < 10:
            info = self._serial_read(ser_obj, 3)
            response += info
            if len(response) == data_len:
                return str(binascii.b2a_hex(response))[2:-1]
        return ""

    def serial_control_relay(self, port: str, action: str, re_type: int = 0, num: Union[int, List[int]] = 1) -> bool:
        """
        串口控制继电器方法
        Args:
            port: 串口号 (如 "COM44")
            action: 控制状态 (0: COM-NO, 1: COM-NC)
            re_type: 继电器类型 (0-5)
            num: 继电器编号或ID列表(仅re_type=5时使用列表)
        Returns:
            bool: 操作是否成功
        """
        try:
            baud = 115200 if re_type == 5 else 9600
            with serial.Serial(port, baudrate=baud, timeout=1) as ser_obj:
                if re_type == 5:
                    pass
                else:
                    cmd_map = self.generate_command(re_type, num)
                ser_obj.write(bytes.fromhex(cmd_map[action]))
                self._verify_response(ser_obj, re_type, cmd_map[action])
            return True
        except Exception as e:
            sys_log.error(f"继电器控制失败: {str(e)}")
            return False

    @staticmethod
    def __crc16_modbus(data: bytes) -> str:
        """
        计算 MODBUS 协议的 CRC-16 校验码
        :param data: 输入字节数据 (如: b'\xFF\x05\x00\x00\xFF\x00')
        :return: CRC-16 校验码 (整数形式)
        """
        crc = 0xFFFF
        polynomial = 0xA001  # MODBUS 多项式 (0x8005 的位反转)
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc >>= 1
                    crc ^= polynomial
                else:
                    crc >>= 1
        rmp_crc = f'{((crc & 0xFF) << 8) | ((crc >> 8) & 0xFF):04X}'
        return rmp_crc[:2] + " " + rmp_crc[2:]

    def generate_command(self, re_type: int, num: int):
        """生成对应继电器类型的控制命令"""
        if re_type == 1:
            cmd_map = {"open": "A0 01 01 A2", "close": "A0 01 00 A1"}
        elif re_type == 4:
            tmp_cmd = [f"FF 05 00 0{num - 1} FF 00", f"FF 05 00 0{num - 1} 00 00"]
            crc1 = self.__crc16_modbus(bytes.fromhex(tmp_cmd[0]))
            crc2 = self.__crc16_modbus(bytes.fromhex(tmp_cmd[1]))
            cmd_map = {"open": f"{tmp_cmd[0]} {crc1}", "close": f"{tmp_cmd[1]} {crc2}"}
        elif re_type == 8:
            cmd_map = {"open": f"A0 0{num} 01 A{num + 1}", "close": f"A0 0{num} 00 A{num}"}
        elif re_type == 16:
            num = f"{num:04x}"  # 格式化为4位16进制
            num = f"{num[:2]} {num[2:]}"
            cmd_map = {"open": f"48 3a 01 70 {num} 01 00 00 45 44", "close": f"48 3a 01 70 {num} 00 00 00 45 44"}
        else:
            raise ValueError(f"不支持的继电器类型: {re_type}")
        return cmd_map

    def _verify_response(self, ser_obj, re_type: int, cmd: str):
        """验证设备响应"""
        if re_type in [1, 8, 16]:
            time.sleep(0.01)
        elif re_type == 4:
            data = self._read_re_cmd_return(time.time(), ser_obj, 8)
            if data.upper() != cmd.replace(" ", ""):
                raise ValueError("响应数据不匹配")
        else:
            raise ValueError(f"不支持的继电器类型: {re_type}")

    @staticmethod
    def control_shielding_box(port: str, action: int) -> bool:
        """串口控制屏蔽箱
        Args:
            port: 串口号(如COM44)
            action: 继电器状态(1:关闭 0:打开)
        Returns:
            bool: 操作是否成功
        """
        valid_actions = {0, 1}
        cmd_map = {1: b"close\r\n", 0: b"open\r\n"}
        resp_tags = {0: "OK", 1: "READY"}
        if action not in valid_actions:
            sys_log.error(f"无效操作:{action}")
            return False
        try:
            with serial.Serial(port=port, baudrate=9600, timeout=1) as client:
                time.sleep(2)  # 等待串口稳定
                cmd = cmd_map[action]
                expected_tag = resp_tags[action]
                for attempt in range(3):
                    sys_log.info(f"尝试#{attempt + 1} 操作屏蔽箱")
                    client.write(cmd)
                    client.flush()
                    start_time = time.time()
                    while time.time() - start_time < 10:  # 总超时10秒
                        ret_info = client.readline().decode('utf-8').strip()
                        if ret_info:
                            sys_log.debug(f"收到响应:{ret_info}")
                            if expected_tag in ret_info:
                                return True
                        time.sleep(0.5)  # 降低CPU占用
                    time.sleep(1)  # 重试间隔
                return False
        except serial.SerialException as e:
            sys_log.error(f"串口异常:{str(e)}")
        except Exception as e:
            sys_log.error(f"未知错误:{str(e)}")
        return False

    @staticmethod
    def serial_at_send_cmd(cmd: str, port: str, baudrate: int = 921600, timeout: int = 60) -> Tuple[
        bool, Optional[str]]:
        """
        AT指令发送
        Args:
            cmd: 待发送指令(自动追加\r\n)
            port: 串口号(如COM3)
            baudrate: 波特率(默认921600)
            timeout: 总超时秒数(默认60)
        Returns:
            tuple: (是否成功, 响应内容/None)
        """
        end_flags = {
            "OK": True,
            "ERROR": False,
            "CONNECT": True,
            "NO CARRIER": False,
            "BUSY": False
        }
        try:
            with serial.Serial(port, baudrate, timeout=1) as ser:
                ser.write(f"{cmd}\r\n".encode('utf-8'))
                ser.flush()
                buffer = []
                start_time = time.time()
                while time.time() - start_time <= timeout:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if not line:
                        continue
                    buffer.append(line)
                    if line in end_flags:
                        return end_flags[line], '\n'.join(buffer)
                    if "ERROR" in line:
                        return False, None
                return False, None
        except serial.SerialException as e:
            sys_log.error(f"串口异常: {e}")
            return False, None
        except Exception as e:
            sys_log.error(f"系统异常: {e}")
            return False, None

    @staticmethod
    def serial_check_sleep_status(timeout: int = 60, dev_index: int = 1) -> bool:
        """优化版休眠状态检测
        Args:
            timeout: 总检测超时(秒)
            dev_index: 设备索引
        Returns:
            bool: 是否成功进入休眠
        """
        check_interval = 0.1  # 队列检查间隔
        sleep_confirm_duration = 10  # 休眠确认时长
        try:
            Globals.set("CheckDebug", True)
            debug_queue = Globals.debug_queue(dev_index)
            sleep_flag = Globals.get("SLEEP_FLAG")
            sys_log.info(f"开始检测休眠标志[{sleep_flag}]，超时:{timeout}s")
            detection_start = time.monotonic()
            sleep_start = -1.0
            while time.monotonic() - detection_start <= timeout:
                if sleep_start > 0 and time.monotonic() - sleep_start >= sleep_confirm_duration:
                    sys_log.info(f"休眠确认完成(持续{sleep_confirm_duration}s)")
                    Globals.set("CheckDebug", False)
                    return True
                if not debug_queue.empty():
                    data = debug_queue.get_nowait()
                    if sleep_flag in data:
                        sleep_start = time.monotonic()
                        sys_log.info(f"捕获休眠标志[{sleep_flag}]")
                time.sleep(check_interval)
            sys_log.warning(f"检测超时(未捕获休眠标志)")
        except Exception as e:
            sys_log.error(f"检测异常: {str(e)}")
        Globals.set("CheckDebug", False)
        return False

    def lc_serial_stat_abnormal_wakeup(self, debug_ser, sleep_time=180, dev_index=1):
        """
        统计异常唤醒次数
        :return: None
        """
        pass

    @staticmethod
    def serial_check_wakeup_status(timeout: int = 30, dev_index: int = 1) -> bool:
        """
        唤醒状态检测
        Args:
            timeout: 检测超时时间(秒)
            dev_index: 设备索引
        Returns:
            bool: 是否成功检测到唤醒标志
        """
        check_interval = 0.05
        try:
            Globals.set("CheckDebug", True)
            debug_queue = Globals.debug_queue(dev_index)
            wakeup_flag = Globals.get("WAKEUP_FLAG")
            sys_log.info(f"启动唤醒检测[标志:{wakeup_flag}] 超时:{timeout}s")
            detection_start = time.monotonic()
            while time.monotonic() - detection_start <= timeout:
                if not debug_queue.empty():
                    data = debug_queue.get_nowait()
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

    def serial_check_sleep_status_no_debug(self, timeout=60, dev_index=1):
        """ debug 口无休眠日志打印的情况使用 ，休眠状态下开关机的用例外不推荐 """
        start_sleep_time = time.time()
        while time.time() - start_sleep_time < timeout:
            time.sleep(5)
            ret, info = self.serial_send_shell_cmd("\r\n", 10, dev_index)
            if not ret:
                return True
        sys_log.error(f"超过 {timeout} 秒模块没有休眠！")
        return False

    @staticmethod
    def serial_send_shell_cmd(cmd: str, timeout: int = 3, dev_index: int = 1) -> Tuple[bool, str]:
        """优化版串口Shell命令执行
        Args:
            cmd: 要执行的命令字符串
            timeout: 超时时间(秒)
            dev_index: 设备索引
        Returns:
            tuple: (执行状态, 返回文本)
        """
        check_interval = 0.05  # 更精细的检查间隔
        shell_return = []
        try:
            Globals.set("CheckDebug", True)
            debug_queue = Globals.debug_queue(dev_index)
            debug_ser = Globals.debug_obj(dev_index)
            if cmd == "\r\n":
                end_tag = "#"
            else:
                _, end_tag, _ = comm.content_create(5, 10, 0)
                cmd = f"{cmd.strip()} && echo {end_tag}\r\n"
            sys_log.debug(f"发送Shell命令: {cmd.strip()}")
            debug_ser.write(cmd.encode("utf-8"))
            start_time = time.monotonic()
            while time.monotonic() - start_time <= timeout:
                if not debug_queue.empty():
                    line = debug_queue.get_nowait()
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

    def serial_load_linux(self, root_name: str = "root", pwd: str = "oelinux123", dev_index: int = 1) -> bool:
        """
        通过串口登录Linux系统
        Args:
            root_name: 用户名（默认root）
            pwd: 密码（默认oelinux123）
            dev_index: 串口设备索引（默认1）
        Returns:
            bool: 登录是否成功
        """
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                sys_log.debug(f"尝试登录（第{attempt}次）")
                debug_ser = Globals.debug_obj(dev_index)
                ret, info = self.serial_send_shell_cmd("\r\n", 3, dev_index)
                if ret:
                    sys_log.debug("已处于登录状态")
                    return True
                if "login" not in info.lower():
                    sys_log.warning(f"未找到登录提示，当前输出: {info.strip()}")
                    time.sleep(2)
                    continue
                sys_log.debug(f"输入用户名: {root_name}")
                debug_ser.write(f"{root_name}\r\n".encode("utf-8"))
                time.sleep(1)
                sys_log.debug("输入密码")
                debug_ser.write(f"{pwd}\r\n".encode("utf-8"))
                ret, _ = self.serial_send_shell_cmd("\r\n", 3, dev_index)
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
    def _generate_final_result(check_list: List[str],
                               ret_dict: Dict[str, float],
                               start_time: float) -> Tuple[bool, List[float]]:
        """生成最终结果"""
        time_list = [ret_dict[word] - start_time if word in ret_dict else -1 for word in check_list]
        Globals.set("CheckDebug", False)
        return False, time_list

    def check_keywords(self, keyword: Union[str, List[str]], timeout: int = 60, check_mode: int = 0, dev_index: int = 1,
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
        debug_queue = Globals.debug_queue(dev_index)
        sys_log.debug(f"开始检测关键字: {check_list}")
        start_time = time.time()
        while time.time() - start_time <= timeout:
            if debug_queue.empty():
                time.sleep(0.1)
                continue
            line = debug_queue.get()
            self._process_line(line, check_list, ret_dict, rematch_mode)
            result = self._check_conditions(check_list, ret_dict, start_time, check_mode)
            if result is not None:
                Globals.set("CheckDebug", False)
                return result
        return self._generate_final_result(check_list, ret_dict, start_time)

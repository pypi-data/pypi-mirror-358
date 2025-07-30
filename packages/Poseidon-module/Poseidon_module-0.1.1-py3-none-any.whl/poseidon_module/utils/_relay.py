#!/usr/bin/env python
# -*- coding: utf-8 -*-
import binascii
import time
from typing import List, Union

import serial
from poseidon_module.core.decorators import trace_action
from poseidon_module.core.logger import sys_log


class _Relay:

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

    def __generate_command(self, re_type: int, num: int):
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

    @trace_action
    def serial_control_relay(self, port: str, action: str, re_type: int = 0, num: Union[int, List[int]] = 1) -> bool:
        """
        串口控制继电器方法
        Args:
            port: 串口号 (如 "COM44")
            action: 控制状态 (open: COM-NO, close: COM-NC)
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
                    cmd_map = self.__generate_command(re_type, num)
                ser_obj.write(bytes.fromhex(cmd_map[action]))
                self._verify_response(ser_obj, re_type, cmd_map[action])
            return True
        except Exception as e:
            sys_log.error(f"继电器控制失败: {str(e)}")
            return False


relay = _Relay()

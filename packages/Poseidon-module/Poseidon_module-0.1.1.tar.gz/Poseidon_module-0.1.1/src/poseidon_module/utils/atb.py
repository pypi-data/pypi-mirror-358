#!/usr/bin/env python
# -*- coding: utf-8 -*-
import serial
import time
from poseidon_module.core.globals import Globals
from poseidon_module.core.decorators import TraceActionMeta

PACK_HEAD = bytes.fromhex("AA33")
MCU_HEAD = bytes.fromhex("AA44")


class UtilATB(metaclass=TraceActionMeta):

    @staticmethod
    def __pack_data(MCU_FUNC_LIST, DATA_LIST):
        pack_len = len(MCU_FUNC_LIST) + len(DATA_LIST) + 1
        assert pack_len < 0xFFFF, '数据包长度超过最大长度 0XFFFFF'
        buffer = bytearray()
        crc = 0
        for byte in MCU_FUNC_LIST:
            buffer.append(byte)
            crc += byte
        for byte in DATA_LIST:
            buffer.append(byte)
            crc += byte
        return PACK_HEAD + pack_len.to_bytes(2, 'little') + bytes(buffer) + (crc & 0xFF).to_bytes(1, 'little')

    @staticmethod
    def __parse_data(mcu_func_index, func_type_index, recv_buf):
        recv_head = recv_buf[0:2]
        recv_data_len = int(recv_buf[2] + recv_buf[3])
        recv_data = recv_buf[4:7]
        recv_crc = recv_buf[7]
        assert recv_head == MCU_HEAD, f'HEAD数据异常！{recv_buf}'
        assert recv_data_len == (len(recv_data) + 1), f'LEN数据异常！{recv_buf}'
        assert recv_data[0] == mcu_func_index and recv_data[1] == func_type_index, f'MCU FUNC数据异常！{recv_buf}'
        crc_check = 0
        for i in range(len(recv_data)):
            crc_check = crc_check + recv_data[i]
        assert recv_crc == crc_check, f'CRC数据异常！{recv_buf}'
        return recv_data[-1]

    def get_mcu_func_cmd(self, mcu_func_index, func_type_index, action, adapter=True):
        """
        action : 拉低:0x00 拉高:0x01
        adapter: 适配继电器脚本休眠唤醒逻辑
        管脚检测功能 (0x00):
            0x00: NAND_DR_SYNC
            0x01: BOOT_STATUS
            0x02: SLEEP_IND_N
            0x03: WAKEUP_OUT
        控制类信号 (0x01):
            0x00: RESIN_N
            0x01: PWRKEY(ON/OFF)
            0x02: WAKEUP_IN
            0x03: FORCE_BOOT
            0x04: FASTBOOT
            0x05: VBUS
        电源开关控制 (0x04):
            0x00: Module_VCC
            0x01: V2X_VCC
            0x02: IMU_VCC
            0x03: HSM_VCC
            0x04: CODEC_VCC
            0x05: VSYS_1V8
            0x06: SIM1&2_VCC
        外设切换开关控制 (0x05)
            0x00: CODEC
            0x01: HSM
            0x02: PHY
        外设连接通断控制 (0x06)
            0x00: 以太网
            0x01: SIM1
            0x02: SIM2
        """
        if mcu_func_index == 0x01:
            if func_type_index == 0x00 or func_type_index == 0x01:
                # power key 与 reset 加了反向器
                action = 0 if action == 1 else 1
            elif func_type_index == 0x02 and adapter:
                action = 0 if action == 1 else 1
        return self.__pack_data([mcu_func_index, func_type_index], [action])

    def check_mcu_return(self, send_cmd, recv_cmd):
        raw_datas = bytes.fromhex(recv_cmd)
        self.__parse_data(send_cmd[4], send_cmd[5], raw_datas)

    def control_mcu_func(self, mcu_func_index, func_type_index, action=0, recv_len=8, dev_index=1):
        """
        详细功能协议在lc_get_mcu_func_cmd
        本函数返回值只有在使用管脚检测功能有效，返回电平值
        """
        relay_info = Globals.get_module(key='relay_info', dev_index=dev_index)
        port = relay_info[0][0]
        ser_obj = serial.Serial(port=port, baudrate=115200, timeout=1)
        time.sleep(1)
        mcu_cmd = self.get_mcu_func_cmd(mcu_func_index, func_type_index, action, adapter=False)
        ser_obj.write(mcu_cmd)
        recv_data = b''
        for i in range(2):
            recv_data = recv_data + ser_obj.readline()
            if len(recv_data) == recv_len:
                break
            time.sleep(0.1)
        ser_obj.close()
        assert len(recv_data) == recv_len, f'接收数据超时：{recv_data}'
        return self.__parse_data(mcu_func_index, func_type_index, recv_data)

    def restore_mcu_init_status(self, dev_index):
        relay_info = Globals.get_module(key='relay_info', dev_index=dev_index)
        port = relay_info[0][0]
        ser_obj = serial.Serial(port=port, baudrate=115200, timeout=1)
        time.sleep(1)
        init_cmd = [
            [0x01, 0x00, 0x01],  # RESET
            [0x01, 0x01, 0x01],  # PWR KEY
            [0x01, 0x02, 0x01],  # WAKEUP IN
            [0x01, 0x03, 0x00],  # FORCE BOOT
            [0x01, 0x04, 0x00],  # FASTBOOT
            [0x01, 0x05, 0x01],  # VBUS
            [0x04, 0x00, 0x01],  # Module_VCC
            [0x04, 0x06, 0x01],  # SIM1&2_VCC
            [0x06, 0x00, 0x00],  # 以太网
            [0x06, 0x01, 0x01],  # SIM1
            [0x06, 0x02, 0x01],  # SIM2
        ]
        recv_len = 8
        try:
            for cmd in init_cmd:
                mcu_cmd = self.get_mcu_func_cmd(cmd[0], cmd[1], cmd[2])
                ser_obj.write(mcu_cmd)
                recv_data = ser_obj.read(8)
                assert len(recv_data) == recv_len, f'接收数据超时：{recv_data}'
                self.__parse_data(cmd[0], cmd[1], recv_data)
                time.sleep(0.1)
        finally:
            ser_obj.close()

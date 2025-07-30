# -*- coding:utf-8 -*-
"""
Created on 2022年7月27日
@author: 杜阿勇
"""
import re
import winreg as wr
from typing import Dict, List

from poseidon_module.core.decorators import trace_action
from poseidon_module.core.logger import sys_log


class _Registry:
    def __init__(self):
        self.usb_port_dic = {}
        self.all_path = {}

    @staticmethod
    def __open_regedit_file(key_path: str) -> wr.HKEYType:
        """
        打开指定注册表
        :param key_path: 注册表路径
        :return: key
        """
        key = None
        try:
            key = wr.OpenKey(wr.HKEY_LOCAL_MACHINE, key_path)
        except FileNotFoundError as e:
            sys_log.debug(rf"{e}: {key_path}")
        finally:
            return key

    @staticmethod
    def __query_info_key(key: wr.HKEYType) -> tuple:
        """
        获取注册表基本信息
        :param key: 注册表key
        :return: An integer that identifies the number of sub keys this key has.
                 An integer that identifies the number of values this key has.
                 An integer that identifies when the key was last modified (if available)
        """
        return wr.QueryInfoKey(key)

    @staticmethod
    def __read_regedit_items(key: wr.HKEYType, val_num: int) -> tuple:
        """
        读取注册表项
        :param key:
        :param val_num:
        :return: value_name -- A string that identifies the value.
                 value_data -- An object that holds the value data, and whose type depends
                               on the underlying registry type.
                 data_type -- An integer that identifies the type of the value data.
        """
        return wr.EnumValue(key, val_num)

    def __get_target_items_value(self, key: wr.HKEYType, t_item: str) -> str:
        sub_key_num, val_num, _ = self.__query_info_key(key)
        for i in range(val_num):
            item, value, _ = self.__read_regedit_items(key, i)
            if item == t_item:
                return value
        return ""

    def __get_all_regedit_path(self, base_path: str, key_id: str) -> None:
        base_key = self.__open_regedit_file(base_path)
        if base_key is None:
            return
        key_num, val_num, _ = self.__query_info_key(base_key)
        if key_num == 0:
            return
        for i in range(key_num):
            sub_name = wr.EnumKey(base_key, i)
            sub_path = rf"{base_path}\{sub_name}"
            if key_id in sub_name:
                if self.all_path.get(key_id) is None:
                    self.all_path[key_id] = []
                self.all_path[key_id].append(sub_path)
            self.__get_all_regedit_path(sub_path, key_id)

    def __get_usb_info(self, path, port_info):
        key = self.__open_regedit_file(path)
        key_num, val_num, _ = self.__query_info_key(key)
        value_dic = {}
        for i in range(val_num):
            value, data, _ = self.__read_regedit_items(key, i)
            value_dic[value] = data
        if value_dic.get("FriendlyName") is not None and port_info.get("description") is None:
            port_info["description"] = value_dic.get("FriendlyName")
        if port_info.get("description") is None:
            port_info["description"] = value_dic.get("DeviceDesc")
        if value_dic.get("PortName") is not None:
            port_info["port"] = value_dic.get("PortName")
        return port_info

    def __regedit_get_usb_serial_port(self, key_id):
        for path in self.all_path[key_id]:
            port_info = {}
            port_info = self.__get_usb_info(path, port_info)
            port_info = self.__get_usb_info(rf"{path}\Device Parameters", port_info)
            if self.usb_port_dic.get(key_id) is None:
                self.usb_port_dic[key_id] = []
            self.usb_port_dic[key_id].append(port_info)

    def __regedit_get_adb_device_id_fun2(self, key_id):
        """ 通过方法1找不到device id 的情况下使用"""
        path_key = self.__open_regedit_file(rf"SYSTEM\ControlSet001\Services\qcusbser\Enum")
        if path_key is None:
            return False, ""
        sub_key_num, val_num, _ = self.__query_info_key(path_key)
        for i in range(val_num):
            value, data, _ = self.__read_regedit_items(path_key, i)
            if "2CB7" in str(data) or "05C6" in str(data):
                if key_id != re.findall(r"&(.*?)&", data)[-1]:
                    continue
                son_file_path = rf"SYSTEM\ControlSet001\Enum\{data}"
                path_key_son = self.__open_regedit_file(son_file_path)
                description = self.__get_target_items_value(path_key_son, "FriendlyName")
                if "modem" in description.lower():
                    dev_instance_path = self.__get_target_items_value(path_key_son, "Driver")
                    tmp_path = fr"SYSTEM\ControlSet001\Control\Class\{dev_instance_path}"
                    tmp_key = self.__open_regedit_file(tmp_path)
                    device_id = self.__get_target_items_value(tmp_key, "QCDeviceSerialNumber")
                    return True, device_id
        return False, ""

    def __regedit_get_adb_devices_info(self):
        """ 通过 windows 注册表获取 adb 端口信息"""
        adb_dic = {}
        path_key = self.__open_regedit_file(rf"SYSTEM\ControlSet001\Services\usbccgp\Enum")
        if path_key is None:
            return False, adb_dic
        sub_key_num, val_num, _ = self.__query_info_key(path_key)
        for i in range(val_num):
            value, data, _ = self.__read_regedit_items(path_key, i)
            if "2CB7" in str(data) or "05C6" in str(data):
                son_file_path = rf"SYSTEM\ControlSet001\Enum\{data}"
                path_key_son = self.__open_regedit_file(son_file_path)
                value = self.__get_target_items_value(path_key_son, "ParentIdPrefix")
                key_id = re.findall(r"&(.*?)&", value)[-1]
                _, id_info, _ = self.__read_regedit_items(path_key, i)
                device_id = id_info.split("\\")[-1]
                if "&" in device_id:
                    ret, device_id = self.__regedit_get_adb_device_id_fun2(key_id)
                adb_dic[key_id] = device_id
        return True, adb_dic

    @trace_action
    def regedit_get_module_usb_devices(self) -> Dict[str, List[Dict[str, str]]]:
        """
        获取模块 USB 所有端口枚举信息
        Returns:
            Dict[str, List[Dict[str, str]]]: 设备ID和端口信息
        """
        self.usb_port_dic = {}
        self.all_path = {}
        ret, adb_dic = self.__regedit_get_adb_devices_info()
        dev_enum_dic = {}
        for key_id, device_id in adb_dic.items():
            self.__get_all_regedit_path(rf"SYSTEM\ControlSet001\Enum\USB", key_id)
        for key_id, device_id in adb_dic.items():
            self.__regedit_get_usb_serial_port(key_id)
            dev_enum_dic[device_id] = self.usb_port_dic[key_id]
        return dev_enum_dic


register = _Registry()

# -*- coding:utf-8 -*-
"""
Created on 2022年3月2日
@author: 杜阿勇
"""
import time

from gtycwifi import PyWiFi, Profile, const
from poseidon_module.core.decorators import TraceActionMeta
from poseidon_module.core.logger import sys_log


class UtilWlan(PyWiFi, metaclass=TraceActionMeta):

    def __init__(self):
        super().__init__()
        if len(self.interfaces()) == 0:
            raise Exception("未找到wifi网卡")
        self._interface = self.interfaces()[0]

    def __enter__(self):
        self._interface.disconnect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._interface.disconnect()

    @property
    def interface_name(self):
        """ PC 获取网卡名称 """
        return self._interface.name()

    @property
    def interface_num(self):
        """ PC 获取网卡名称 """
        return len(self.interfaces())

    @property
    def interface_status(self):
        """ PC 获取网卡名称 """
        return self._interface.status()

    @property
    def scan_wifi(self):
        """ PC 扫描 wifi """
        self._interface.scan()
        time.sleep(3)
        base_wifi = self._interface.scan_results()
        ssids = list(set([i.ssid.encode('raw_unicode_escape').decode('utf-8') for i in base_wifi]))
        return ssids

    def scan_target_wifi(self, target_ssid: str) -> bool:
        """
        pc 扫描目标 wifi
        Args:
            target_ssid: 目标热点名称
        Returns:
            bool True - 找到目标热点 False - 未找到目标热点
        """
        start_time = time.time()
        while time.time() - start_time <= 30:
            ssid_lst = self.scan_wifi
            if target_ssid in ssid_lst:
                return True
            time.sleep(1)
        return False

    def connect_wifi(self, ssid: str, pwd: str = "", auth: int = 4, timeout: int = 30) -> bool:
        """
        PC 连接 目标热点 扫描热点列表，选择目标热点，连接目标热点
        Args:
            ssid: 热点名称
            pwd: 密码
            auth: 加密方式 0 - 无加密 1 - WPA 2 - WPAPSK 3 - WPA2 4 - WPA2PSK 5 - 未知
            timeout: 连接超时时间
        Returns:
            bool,  True - 连接成功 False - 连接失败
        """
        try:
            assert self.scan_target_wifi(ssid), f"未找到目标热点: {ssid}"
            profile = Profile()
            profile.ssid = ssid
            profile.auth = const.AUTH_ALG_OPEN
            profile.akm = [auth]
            profile.cipher = const.CIPHER_TYPE_NONE if auth == 0 else const.CIPHER_TYPE_CCMP
            if pwd:
                profile.key = pwd
            self._interface.remove_all_network_profiles()
            cur_profile = self._interface.add_network_profile(profile)
            self._interface.connect(cur_profile)
            start_time = time.time()
            while time.time() - start_time < timeout:
                status = self._interface.status()
                if status == const.IFACE_CONNECTED:
                    sys_log.info(f"成功连接到 {ssid}")
                    return True
                time.sleep(1)
            sys_log.warning(f"连接超时: {ssid}")
            return False
        except Exception as e:
            sys_log.error(e)
            return False

    def disconnect_wifi(self) -> bool:
        """ PC 断开 wifi 连接 """
        if self._interface.status() == const.IFACE_CONNECTED:
            self._interface.disconnect()
            start_time = time.time()
            while time.time() - start_time < 10:
                status = self._interface.status()
                if status == const.IFACE_DISCONNECTED:
                    sys_log.info("断开wifi连接成功")
                    return True
                time.sleep(1)
            sys_log.warning("断开wifi连接超时")
            return False
        return True

# -*- coding:utf-8 -*-
"""
Created on 2022年3月2日
@author: 杜阿勇
"""
import re
import urllib
import urllib.request
from poseidon_module.core.const import *
from poseidon_module.core.logger import sys_log
import gtycwifi, time
from gtycwifi import const

from poseidon_module.core.shell import Shell

from poseidon_module.core.decorators import TraceActionMeta



class UtilModuleWlan(Shell, metaclass=TraceActionMeta):

    def __init__(self):
        super().__init__()

    def lc_get_wifi_channel_lst(self, dev_index=1):
        """ 查看信道列表 """
        try:
            ret, info = self.execute_adb_shell("iw list", dev_index=dev_index)
            assert ret, "下发 iw list 指令失败"
            result = re.findall(r"\[(\d+)] \(\d+\.\d dBm\)", info, re.S)
            result = [int(i) for i in result]
            channel_lst1 = [i for i in result if i < 15]
            channel_lst2 = [i for i in result if i > 14]
            return True, channel_lst1, channel_lst2
        except Exception as e:
            sys_log.error(e)
            return False, None, None

    def lc_check_wifi_mac(self, iface_name, dev_index):
        """ 检查 wifi mac 地址 """
        try:
            ret, info = self.execute_adb_shell(f"ifconfig {iface_name}", dev_index=dev_index)
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

    def lc_check_wifi_hostapd_or_wap_proc(self, tag, dev_index=1):
        cmd = f"pgrep {tag}"
        ret, info = self.execute_adb_shell(cmd, dev_index=dev_index)
        if ret:
            if len(info.split("\n")) == 2:
                return True
        return False

    def lc_check_wifi_hostapd_and_wap_recovery(self, tag, timeout, dev_index):
        """
        检查hostapd 和 wap 恢复机制
        :param tag: 0 —— wpa 1——hostapd 2 ——wap & hostapd
        :param timeout: 检查超时时间
        :param dev_index: 设备序号
        :return: True / False
        """
        start_time = time.time()
        while time.time() - start_time <= timeout:
            ret1 = self.lc_check_wifi_hostapd_or_wap_proc("wpa", dev_index)
            ret2 = self.lc_check_wifi_hostapd_or_wap_proc("hostapd", dev_index)
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


class UtilPcWlan(Shell,metaclass=TraceActionMeta):

    def __init__(self):
        super().__init__()
        self.wifi = gtycwifi.PyWiFi()
        self.interfaces = None
        # self.ln = UtilNet()

    def _interfaces(self):
        self.interfaces = self.wifi.interfaces()

    def lc_get_interfaces_name(self):
        """ PC 获取网卡名称 """
        num = self.lc_get_interfaces()
        assert num > 0, "该电脑没有无线网卡！"
        return self.interfaces[0].name()

    def lc_get_interfaces(self):
        """ PC 获取网卡数目 """
        if self.interfaces is None:
            self._interfaces()
        return len(self.interfaces)

    def lc_get_interfaces_status(self):
        """ PC 获取当前 wifi 网卡状态 """
        if self.interfaces is None:
            self._interfaces()
        interface = self.interfaces[0]
        return interface.status()

    def lc_scan_wifi(self):
        """ PC 扫描 wifi """
        if self.interfaces is None:
            self._interfaces()
        interface = self.interfaces[0]
        interface.scan()
        time.sleep(3)
        base_wifi = interface.scan_results()
        ssids = list(set([i.ssid for i in base_wifi]))
        return ssids

    def lc_connect_wifi(self, ssid, pwd, auth=4):
        """
        :param ssid: wifi 名称
        :param pwd: wifi 密码
        :param auth:
                NONE = 0 | WPA = 1 | WPAPSK = 2 | WPA2 = 3 | WPA2PSK = 4 | UNKNOWN = 5
        :return: 连接结果
        """
        if self.interfaces is None:
            self._interfaces()
        interface = self.interfaces[0]
        interface.disconnect()
        time.sleep(2)
        profile = gtycwifi.Profile()

        profile.ssid = ssid
        profile.auth = const.AUTH_ALG_OPEN
        profile.akm.append(auth)
        profile.cipher = const.CIPHER_TYPE_CCMP
        profile.key = pwd

        interface.remove_all_network_profiles()
        tmp_profile = interface.add_network_profile(profile)
        interface.connect(tmp_profile)
        for i in range(10):
            ret = self.lc_get_interfaces_status()
            if ret == 4:
                return True
            time.sleep(2)
        else:
            return False

    def lc_connect_wifi_without_pwd(self, ssid):
        """ PC 连接开放 wifi """
        if self.interfaces is None:
            self._interfaces()
        interface = self.interfaces[0]
        interface.disconnect()
        time.sleep(2)
        profile = gtycwifi.Profile()

        profile.ssid = ssid
        profile.auth = const.AUTH_ALG_OPEN
        profile.akm.append(0)
        profile.cipher = const.CIPHER_TYPE_NONE

        interface.remove_all_network_profiles()
        tmp_profile = interface.add_network_profile(profile)
        interface.connect(tmp_profile)
        for i in range(10):
            ret = self.lc_get_interfaces_status()
            if ret == 4:
                return True
            time.sleep(2)
        else:
            return False

    def lc_disconnect_wifi(self):
        """ PC 断开 wifi 连接 """
        if self.interfaces is None:
            self._interfaces()
        interface = self.interfaces[0]
        if interface.status() == const.IFACE_CONNECTED:
            interface.disconnect()
            for i in range(10):
                ret = self.lc_get_interfaces_status()
                if ret == 0:
                    return True
                time.sleep(1)
            else:
                return False
        return True

    def lc_wifi_connect_to_hotspot(self, ssid, pwd, auth=4):
        """ 扫描并连接到目标热点 """
        try:
            num = self.lc_get_interfaces()
            assert num > 0, "该电脑没有无线网卡！"
            for i in range(10):
                ssid_lst = self.lc_scan_wifi()
                if ssid_lst:
                    if ssid in ssid_lst:
                        break
            else:
                sys_log.error("30 秒未扫描到目标热点")
                return False
            ret = self.lc_connect_wifi(ssid, pwd, auth)
            return ret
        except Exception as e:
            sys_log.error(e)
            return False

    def lc_wifi_check_link_speed(self, standard):
        """ 检查 wifi 协商速率 """
        try:
            char_list = ["(", ")"]
            name = self.lc_get_interfaces_name()
            ret, info = self.execute_common_shell("wmic NIC where NetEnabled=true get Name, Speed")
            assert ret, "获取网卡速率信息失败"
            for char in char_list:
                name = name.replace(char, "")
                info = info.replace(char, "")
            ret = re.findall(rf"{name}.*?(\d+)", info)
            assert ret, f"未匹配到{name}正确的速率数据"
            link_speed = ret[0]
            sys_log.debug(f"获取到的wifi连接速率为: {link_speed}")
            value1 = round(float(link_speed) / (10 ** 6))
            value2 = round(float(link_speed) / (1.5 * 10 ** 6))
            assert standard in [value1, value2], f"测试值 {[value1, value2]} 与标准值{standard}不符"
            return True
        except Exception as e:
            sys_log.error(e)
            return False

    @staticmethod
    def lc_get_wifi_channel_list(country_code, ap_index, mode=1):
        """
        获取各个国家码支持的信道列表和不支持的信道列表
        :param country_code: 国家码
        :param ap_index: 热点类型
        :param mode: 是否包含 STA
        :return: [支持],[不支持]
        """
        map_dic_5 = {'LB ': LB, 'BR ': BR, 'PE ': PE, 'CN ': CN, 'RS ': RS, 'TN ': TN, 'GB ': GB, 'DE ': DE, 'NL ': NL,
                     'CH ': CH, 'NO ': NO, 'FR ': FR, 'BE ': BE, 'ES ': ES, 'SE ': SE, 'IT ': IT, 'LU ': LU, 'DK ': DK,
                     'FI ': FI, 'GE ': GE, 'MM ': MM, 'IN ': IN, 'QA ': QA, 'IL ': IL, 'CO ': CO, 'UZ ': UZ, 'JO ': JO,
                     'MA ': MA, 'JP ': JP, 'BO ': BO, 'KW ': KW, 'SA ': SA, 'AZ ': AZ, 'KZ ': KZ, 'MD ': MD, 'PR ': PR,
                     'PA ': PA, 'CL ': CL, 'EG ': EG, 'BH ': BH, 'UY ': UY, 'OM ': OM, 'AE ': AE, 'ZA ': ZA, 'AO ': AO,
                     'PH ': PH, 'LA ': LA, 'UA ': UA, 'KH ': KH, 'GT ': GT, 'TJ ': TJ, 'VN ': VN, 'US ': US, 'KR ': KR,
                     'HK ': HK, 'MO ': MO, 'PY ': PY, 'CR ': CR, 'EC ': EC, 'DO ': DO, 'TW ': TW, 'TH ': TH, 'NZ ': NZ,
                     'SG ': SG, 'MY ': MY, 'CA ': CA, 'AU ': AU, 'MX ': MX, 'AR ': AR, 'LC ': LC, }
        if ap_index == 0:
            return HT1 if country_code in ["US", "CA"] else HT2, [14]
        if mode == 0:
            if country_code in ["GB", "DE", "NL", "CH", "NO", "FR", "BE", "ES", "SE", "IT", "LU", "DK", "FI", "GE",
                                "MM"]:
                return map_dic_5[country_code] + B3, list(set(B1 + B2 + B3_3 + B4) - set(map_dic_5[country_code]))
        return map_dic_5[country_code], list(set(B1 + B2 + B3_3 + B4) - set(map_dic_5[country_code]))

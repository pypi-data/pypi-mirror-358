# -*- coding:utf-8 -*-
import re
import time
from typing import Union, List, Optional, Dict

from poseidon_module.core.const import change_ip_content
from poseidon_module.core.globals import Globals
from poseidon_module.core.logger import sys_log
from poseidon_module.utils._registry import register
from poseidon_module.utils._shell import Shell


class _Device(Shell):
    def __init__(self, dev_index: Union[int, str] = 1, pwd: Optional[str] = None):
        super().__init__(dev_index=dev_index, pwd=pwd)

    def __ipconfig_all(self) -> List[Dict[str, any]]:
        """
        获取 PC 所有网卡信息，以列表形式返回
        Returns:
             列表，包含所有网卡信息
        """
        adapters = []
        ret, ipconfig_info = self.execute_common_shell("ipconfig /all", log_output=False)
        adapter_blocks = re.split(r"(\n.*?(?:适配器|adapter) .+):", ipconfig_info, flags=re.IGNORECASE)[1:]
        for name_block, info_block in zip(*[iter(adapter_blocks)] * 2):
            adapter_name = re.search(r"(?:适配器|adapter)\s+(.+)", name_block.strip()).group(1) if name_block else ""
            patterns = {
                "description": r"(?:描述|Description).*?: (.*?)\n",
                "ipv4": r"IPv4.*?: (\d+\.\d+\.\d+\.\d+)",
                "ipv6": r"IPv6.*?: (.*?)\(",
                "mask": r"(?:子网掩码|Subnet Mask).*?: (\d+\.\d+\.\d+\.\d+)",
                "gw": r"(?:默认网关|Default Gateway).*?: (\d+\.\d+\.\d+\.\d+)",
                "dns": r"DNS.*?: (\d+\.\d+\.\d+\.\d+)",
                "mac": r"(?:物理地址|Physical Address).*?: (.+-.+-.+-.+-.+-.+)\n",
                "dhcp": r"DHCP.*?: (.*?)\n",
                "get_lease_time": r"获得租约的时间.*?: (.*?)\n",
                "lease_expire_time": r"租约过期的时间.*?: (.*?)\n"
            }
            info = {k: (re.search(p, info_block).group(1) if re.search(p, info_block) else "")
                    for k, p in patterns.items()}
            info["dhcp"] = 1 if info["dhcp"] in ("是", "Yes") else 0
            info["name"] = adapter_name
            adapters.append(info)
        return adapters

    def __check_device_status(self, status: bool, interval: int = 1, timeout: int = 60 * 3, dev_type: str = "adb",
                              ) -> bool:
        """检查设备状态"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            time.sleep(interval)
            ret, info = self.execute_common_shell(f"{dev_type} devices")
            if not ret:
                continue
            state = bool(
                re.search(rf"{self.device_id}.*?{dev_type if dev_type == 'fastboot' else 'device'}", info, re.S))
            if state == status:
                return True
        sys_log.debug(f"设备 {self.device_id} 未在 {timeout} 秒内{'连接' if status else '断开'}")
        return False

    def __get_modem_usb_device(self) -> List[Dict[str, str]]:
        """
        获取指定模块的 USB 信息
        Returns:
            列表，包含指定模块的 USB 信息
        """
        info_dic = register.regedit_get_module_usb_devices()
        if info_dic.get(self.device_id) is not None:
            return info_dic.get(self.device_id)
        return []

    def __check_rndis(self):
        """ 检查设备是否有RNDIS """
        port_list = self.__get_modem_usb_device()
        assert port_list, "未检测到USB设备端口信息！"
        for port in port_list:
            if "NDIS" in port["description"]:
                return True
        return False

    def __remount_app_dir(self):
        """ 重新挂载App目录 """
        try:
            app_dir = Globals.get("APP_DIR")
            ret, info = self.execute_adb_shell(f"mount | grep 'on /{app_dir} '")
            assert ret, f"设备【{self.device_id}】查询挂载信息失败!"
            sys_log.info(f"设备【{self.device_id}】当前挂载情况为 {info}")
            if "noexec" in info:
                sys_log.info(f"设备【{self.device_id}】重新挂载 {app_dir} 分区")
                ret, info = self.execute_adb_shell(f"mount -o remount rw, /{app_dir}")
                assert ret, f"设备【{self.device_id}】重新挂载 {app_dir} 目录失败！"
                time.sleep(2)
        except Exception as e:
            sys_log.error(e)
            return False
        return True

    def __rndis_ips(self) -> List[str]:
        """
        获取模块的 NDIS 网卡 IP 地址
        Returns:
            列表，包含所有模块的 NDIS 网卡 IP 地址
        """
        ip_list = []
        for adapter in self.__ipconfig_all():
            if "NDIS" in adapter.get("description").upper():
                cur_ip = adapter.get("ipv4")
                ip_list.append(cur_ip)
        return ip_list

    @staticmethod
    def __build_change_ip_bat():
        file = f"D:/change_ip_auto.bat"
        with open(file, "w") as fd:
            fd.write(change_ip_content)
        sys_log.debug(f"change_ip_auto.bat path: {file}")
        return file

    def set_static_ip_addr(self, iface_name: str, ip: str, mask: str, gw: str) -> bool:
        """
        设置指定网卡的静态 IP 地址
        Args:
            iface_name: 网卡名称 eg: 以太网 2
            ip: 静态 IP
            mask: 子网掩码
            gw: 默认网关
        Returns:
            bool，True 表示设置成功，False 表示设置失败
        """
        bat_path = self.__build_change_ip_bat()
        net_lst = self.__ipconfig_all()
        for net in net_lst:
            if iface_name == net.get("name"):
                dhcp = net.get("dhcp")
                cur_ip = net.get("ipv4")
                if dhcp == 1 or ip != cur_ip:
                    cmd1 = f'start {bat_path} 1 \"{iface_name}\" {ip} {mask} {gw}'
                    ret, info = self.execute_common_shell(cmd1)
                    return ret
                return True
        return False

    def set_dhcp_ip_addr(self, iface_name: str) -> bool:
        """
        设置指定网卡的动态 IP 地址
        Args:
            iface_name: 网卡名称 eg: 以太网 2
        Returns:
            bool，True 表示设置成功，False 表示设置失败
        """
        bat_path = self.__build_change_ip_bat()
        net_lst = self.__ipconfig_all()
        for net in net_lst:
            if iface_name == net.get("name"):
                dhcp = net.get("dhcp")
                if dhcp == 0:
                    cmd1 = f'start {bat_path} 2 \"{iface_name}\" 192.168.101.10 255.255.255.0 192.168.101.1'
                    ret, info = self.execute_common_shell(cmd1)
                    return ret
                return True
        return False

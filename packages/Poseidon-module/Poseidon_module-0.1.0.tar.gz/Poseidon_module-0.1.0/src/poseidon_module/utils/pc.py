# -*- coding:utf-8 -*-
import os
import re
import time
import zipfile
from typing import Dict, List, Union, Tuple

import serial.tools.list_ports

from poseidon_module.core.const import change_ip_content
from poseidon_module.core.decorators import TraceActionMeta
from poseidon_module.core.globals import Globals
from poseidon_module.core.logger import sys_log
from poseidon_module.core.shell import Shell
from poseidon_module.utils.registry import UtilRegistry


class UtilPC(UtilRegistry, metaclass=TraceActionMeta):
    def __init__(self):
        super().__init__()
        self.shell = Shell()

    def ipconfig_all(self) -> List[Dict[str, any]]:
        """
        获取 PC 所有网卡信息，以列表形式返回
        Returns:
             列表，包含所有网卡信息
        """
        adapters = []
        ret, ipconfig_info = self.shell.execute_common_shell("ipconfig /all", log_output=False)
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

    def rndis_ips(self) -> List[str]:
        """
        获取模块的 NDIS 网卡 IP 地址
        Returns:
            列表，包含所有模块的 NDIS 网卡 IP 地址
        """
        ip_list = []
        for adapter in self.ipconfig_all():
            if "NDIS" in adapter.get("description").upper():
                cur_ip = adapter.get("ipv4")
                ip_list.append(cur_ip)
        return ip_list

    def get_target_adapter_info(self, adapter_name: str) -> Dict[str, any]:
        """
        获取指定网卡信息
        Args:
            adapter_name: 网卡名称 eg: 以太网
        Returns:
            字典，包含指定网卡信息
        """
        for net in self.ipconfig_all():
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

    def rndis_name(self, dev_index: Union[str, int] = 1) -> Tuple[bool, str]:
        """
        获取指定模块的 RNDIS 网卡名称
        Args:
            dev_index: device id(设备ID) or device index(设备绑定编号)
        Returns:
             元组，第一个元素为 bool，True 表示获取成功，False 表示获取失败；第二个元素为 str，获取到的 RNDIS 网卡名称
        """
        device_id = Globals.dev_id(dev_index)
        info_dic = self.regedit_get_module_usb_devices()
        for k, v in info_dic.items():
            if k != device_id:
                continue
            rndis_name = [i["description"] for i in v if "NDIS" in i["description"]]
            if not rndis_name:
                sys_log.info(f"注册表中未找到 {device_id} 的 rndis 网卡！")
                return False, ""
            rndis_name = rndis_name[0]
            net_dic_lst = self.ipconfig_all()
            for net in net_dic_lst:
                if net.get("description") == rndis_name:
                    iface_name = net.get("name")
                    return True, iface_name
        sys_log.info(f"未找到 {device_id} 的 rndis 网卡！")
        return False, ""

    def regedit_get_modem_usb_device(self, dev_index: Union[str, int] = 1) -> List[Dict[str, str]]:
        """
        获取指定模块的 USB 信息
        Args:
            dev_index: device id(设备ID) or device index(设备绑定编号)
        Returns:
            列表，包含指定模块的 USB 信息
        """
        device_id = Globals.dev_id(dev_index)
        info_dic = self.regedit_get_module_usb_devices()
        if info_dic.get(device_id) is not None:
            return info_dic.get(device_id)
        return []

    def check_device_all_usb_alive(self, ports, dev_index=1):
        """ 通过注册表检查指定的端口组合存在与否 """
        info_list = self.regedit_get_modem_usb_device(dev_index)
        if len(info_list) != len(ports):
            return False
        info_list = [i["description"] for i in info_list]
        for port in ports:
            tmp_list = [i for i in info_list if port.upper() in i.upper()]
            if not tmp_list:
                sys_log.error(f"未发现{port}端口！")
                return False
        return True

    @staticmethod
    def check_9008_port(times=30):
        for i in range(times):
            ports = list(serial.tools.list_ports.comports())
            for p in ports:
                if "9008" in p.description.upper() or "900E" in p.description.upper():
                    return True, p.device
            time.sleep(1.5)
        return False, None

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
        net_lst = self.ipconfig_all()
        for net in net_lst:
            if iface_name == net.get("name"):
                dhcp = net.get("dhcp")
                cur_ip = net.get("ipv4")
                if dhcp == 1 or ip != cur_ip:
                    cmd1 = f'start {bat_path} 1 \"{iface_name}\" {ip} {mask} {gw}'
                    ret, info = self.shell.execute_common_shell(cmd1)
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
        net_lst = self.ipconfig_all()
        for net in net_lst:
            if iface_name == net.get("name"):
                dhcp = net.get("dhcp")
                if dhcp == 0:
                    cmd1 = f'start {bat_path} 2 \"{iface_name}\" 192.168.101.10 255.255.255.0 192.168.101.1'
                    ret, info = self.shell.execute_common_shell(cmd1)
                    return ret
                return True
        return False

    @staticmethod
    def create_win_file(size: int, form: str) -> Tuple[str, str]:
        """
        在指定路径生成随机内容的测试文件
        Args:
            size: 文件大小数值字符串
            form: 大小单位(b/k/m/g/t)
        Returns:
            tuple: (文件名, 完整文件路径)
        Raises:
            ValueError: 当参数格式无效时
        """
        if form.lower() not in ('b', 'k', 'm', 'g', 't'):
            raise ValueError("Invalid size unit, use b/k/m/g/t")
        unit_map = {
            'b': 1,
            'k': 1024,
            'm': 1024 ** 2,
            'g': 1024 ** 3,
            't': 1024 ** 4
        }
        file_name = f"test{size}{form.lower()}"
        full_path = os.path.join(Globals.log_path(), file_name)
        byte_size = int(size) * unit_map[form.lower()]
        with open(full_path, 'wb') as f:
            f.write(os.urandom(byte_size))
        return file_name, full_path

    @staticmethod
    def unzip_file(file_path: str, file_name: str) -> List[str]:
        """
        解压文件包并输出解压文件列表
        Args:
            file_path: 待解压文件路径
            file_name: 待解压文件名称
        Returns:
            解压文件列表
        Raises:
            FileNotFoundError: 当ZIP文件不存在时
            zipfile.BadZipFile: 当ZIP文件损坏时
        """
        zip_path = os.path.join(file_path, file_name)
        unzip_path = os.path.join(file_path, "tmp_pkg")
        if not os.path.exists(zip_path):
            raise FileNotFoundError(f"ZIP文件不存在: {zip_path}")
        os.makedirs(unzip_path, exist_ok=True)
        file_list = []
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(unzip_path)
            for i, j, k in os.walk(unzip_path):
                for file in k:
                    file_list.append(file)
        except zipfile.BadZipFile as e:
            raise zipfile.BadZipFile(f"ZIP文件损坏: {zip_path}") from e
        return file_list

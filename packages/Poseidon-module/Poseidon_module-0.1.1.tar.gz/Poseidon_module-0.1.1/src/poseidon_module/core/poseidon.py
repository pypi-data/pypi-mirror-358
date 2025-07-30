# -*- coding:utf-8 -*-
from dataclasses import dataclass
import inspect
import json
import socket
import threading
import time
from typing import Union, Tuple, Optional, Dict, Any

from poseidon_module.core.const import *
from poseidon_module.core.decorators import TraceActionMeta
from poseidon_module.core.globals import Globals
from poseidon_module.core.logger import sys_log


class _Socket:
    def __init__(self):
        self.lock = threading.RLock()  # 改用可重入锁
        self.port_range = (40000, 50000)  # 端口范围常量

    def _get_unique_bind_port(self):
        """线程安全地获取唯一绑定端口"""
        with self.lock:  # 使用with语句自动管理锁
            bind_port = Globals.get("UDP_INIT_PORT")
            if bind_port > self.port_range[1]:
                bind_port = self.port_range[0]
            Globals.set("UDP_INIT_PORT", bind_port + 1)
            return bind_port

    @staticmethod
    def _create_socket(timeout: Optional[str] = None):
        """创建预配置的UDP套接字"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(timeout or Globals.get("SOCKET_TIMEOUT"))
        return sock

    @staticmethod
    def _decode_response(data):
        """尝试多种编码解码响应数据"""
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data.decode("ISO-8859-1")

    def send_package_by_socket(self, content_dic: Dict[str, Any], need_back: bool = True, dev_gw: str = "",
                               dev_ip: str = "", timeout: Optional[int] = None, try_connect_times: int = 1):
        """
        发送UDP数据包并可选接收响应
        Args:
            content_dic: 数据包内容字典
            need_back: 是否需要接收响应
            dev_gw: 模组网关IP
            dev_ip: 模组IP
            timeout: 超时时间
            try_connect_times: 尝试重试次数
        Returns:
            成功返回响应数据，失败返回错误信息
        """
        addr = (dev_gw, Globals.get("CENTRE_PORT"))
        send_data = json.dumps(content_dic).encode("utf-8")
        count = 0
        err_num = 0
        while count < try_connect_times:
            with self._create_socket(timeout) as sock:  # 使用with管理套接字资源
                try:
                    if dev_ip:
                        sock.bind((dev_ip, self._get_unique_bind_port()))
                    sock.sendto(send_data, addr)
                    if not need_back:
                        return True
                    start_time = time.time()
                    data, _ = sock.recvfrom(1024 * 60)
                    decoded_data = self._decode_response(data)
                    exec_time = time.time() - start_time
                    if timeout and exec_time > Globals.get("SOCKET_TIMEOUT"):
                        sys_log.warning(f"接口执行时间 {exec_time:.2f}s")
                    return decoded_data
                except socket.error as ex:
                    if ex.errno == 10049 or ex.errno == 10013:  # 超时
                        err_num = ex.errno
                        time.sleep(2)
        if err_num != 0:
            sys_log.warning("网络通信失败,请检查网络连接或模组状态！")
        sys_log.critical(f"{try_connect_times}次尝试后连接失败")
        return '{"result": 1, "ret_list": [{"ret":-444}]}'


class Poseidon(_Socket, metaclass=TraceActionMeta):
    def __init__(self):
        super().__init__()

    @staticmethod
    def __build_action_package(
            server_id: int,
            act_type: int,
            act_id: int,
            para: Optional[Dict[str, Any]] = None,
            expect: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        构造 action请求包，包含动作类型、动作ID、动作参数、预期结果、线程ID等信息。
        Args:
            server_id: 目标服务器ID
            act_type: 动作类型
            act_id: 动作ID
            para: 动作参数(默认None)
            expect: 预期结果(默认None)
        Returns:
            构造好的 action 请求包字典
        """
        action = {
            "server_id": str(server_id),
            "act_type": str(act_type),
            "act_id": str(act_id),
            "para": para if para is not None else '',
            "ext": expect if expect is not None else ''
        }
        package = {"actions": [action], "thread_id": threading.get_ident()}
        return package

    def __send_action_package(
            self,
            act_pkg: dict,
            dev_index: int = 1,
            need_back: bool = True,
            socket_timeout: Optional[float] = None,
            try_times: int = 1
    ) -> Tuple[Optional[int], Union[None, dict, list]]:
        """
        发送 action 请求包并处理响应
        Args:
            act_pkg: action 包字典
            dev_index: 设备索引(从1开始)
            need_back: 是否需要返回响应
            socket_timeout: 套接字超时时间
            try_times: socket连接尝试次数
        Returns:
            tuple: (result_code, response_data)
        Raises:
            ValueError: 设备索引无效
            ConnectionError: 网络通信失败
            JSONDecodeError: 响应数据解析失败
        """
        app_list = Globals.get("PoseidonList")
        dev_idx = dev_index - 1
        if not 0 <= dev_idx < len(app_list):
            raise ValueError(f'设备索引{dev_index}超出范围(1-{len(app_list)})')
        app_info = app_list[dev_idx]
        if app_info.get('communication') != COMMUNICATION_WITH_WLAN:
            raise ConnectionError('仅支持WLAN通信模式')
        pkg = None
        try:
            pkg = super().send_package_by_socket(
                act_pkg,
                need_back,
                app_info.get('dev_gw', ''),
                app_info.get('dev_ip', ''),
                socket_timeout,
                try_times
            )
            if not need_back:
                return None, None
            result_json = json.loads(pkg)
            ret_list = result_json.get('ret_list', [])
            if not ret_list:
                return result_json.get('result', -1), []
            return result_json.get('result', -1), ret_list[0]
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"响应数据解析失败: {str(e)}", pkg, 0)
        except Exception as e:
            raise ConnectionError(f"网络通信失败: {str(e)}")

    def handshake_to_poseidon(self, try_time: int = 10, dev_index: int = 1) -> bool:
        """
        握手检测方法，支持TCP连接状态检查
        Args:
            dev_index: 设备索引(1-based)
            try_time: 最大尝试次数
        Returns:
            bool: 握手成功返回True，失败返回False
        Raises:
            ConnectionError: 网络通信失败
        """
        cmd_dic = self.__build_action_package(SYSTEM_SERVER_ID, ActionType.SYSTEM_ACTION, UtilFun.SYSTEM_HANDSHAKE_ID)
        for attempt in range(1, try_time + 1):
            try:
                result, _ = self.__send_action_package(cmd_dic, dev_index, try_times=3)
                if result == 0:
                    sys_log.info(f"设备{dev_index}握手成功(尝试{attempt}次)")
                    Globals.set("ServerState", True)
                    return True
                sys_log.debug(f"设备{dev_index}握手失败(尝试{attempt}/{try_time})")
                if attempt < try_time:
                    time.sleep(2)
            except Exception as e:
                sys_log.error(f"设备{dev_index}握手异常: {str(e)}")
                if attempt == try_time:
                    raise ConnectionError(f"最终握手失败: {str(e)}")
                time.sleep(2)
        return False

    def module_shell(self, cmd: str, dev_index: int = 1, socket_timeout: float = 60) -> str:
        """
        发送shell指令
        Args:
            cmd: shell指令
            dev_index: 设备索引(1-based)
            socket_timeout: 套接字超时时间
        Returns:
            str: shell指令返回结果
        """
        para = {"cmd": cmd}
        cmd_dic = self.__build_action_package(SYSTEM_SERVER_ID, ActionType.SYSTEM_ACTION, UtilFun.SHELL_ID, para)
        result, lt = self.__send_action_package(cmd_dic, dev_index, socket_timeout=socket_timeout)
        return lt.get("cmd_rsp", "") if result == 0 else ""

    def module_ping(self, target_ip: str, source_ip: str, ip_family: int = 4, n: int = 10, pkg_loss: int = 90,
                    dev_index: int = 1) -> bool:
        """
        模组内部ping检查
        Args:
            target_ip: 目的地址或域名或default
            source_ip: 源地址或网卡名
            ip_family: 4/6
            n: ping网次数
            pkg_loss: 丢包率
            dev_index: 设备索引(1-based)
        Returns:
            bool: 成功返回True，失败返回False
        """
        ip_family = ip_family if ip_family != 10 else 4
        para = {
            "target_ip": target_ip,
            "source_ip": source_ip,
            "ip_family": ip_family,
            "ping_count": n,
            "pkg_loss": pkg_loss
        }
        sys_log.debug("module start ping test")
        cmd_dic = self.__build_action_package(SYSTEM_SERVER_ID, ActionType.SYSTEM_ACTION, UtilFun.PING_ID, para)
        result, lt = self.__send_action_package(cmd_dic, dev_index, socket_timeout=n + 60)
        if result == 0:
            return lt.get("result", 1) == 0
        sys_log.error(f"PING测试失败(错误码: {result})")
        return False

    def module_socket_init(self, socket_type: int, iface_name: str, target_ip: str, target_port: int,
                           dev_index: int = 1) -> Tuple[bool, int]:
        """
        模组内初始化socket
        Args:
            socket_type: 0 -- TCP 1 -- UDP
            iface_name: 网卡名称
            target_ip: tcp/udp服务端目标地址
            target_port: 服务端端口号 (1-65535)
            dev_index: 设备索引(1-based)
        Returns:
            Tuple[bool, int]: (连接状态, socket文件描述符)
        """
        para = {
            "socket_type": socket_type,
            "iface_name": iface_name,
            "target_ip": target_ip,
            "target_port": target_port
        }
        protocol = "TCP" if socket_type == 0 else "UDP"
        sys_log.debug(f"{protocol} connecting")
        cmd_dic = self.__build_action_package(SYSTEM_SERVER_ID, ActionType.SYSTEM_ACTION, UtilFun.SOCKET_INIT, para)
        result, lt = self.__send_action_package(cmd_dic, dev_index, socket_timeout=200)
        if lt.get("sockfd", -1) > 0:
            sys_log.debug(f"{protocol} connected")
            return True, lt["sockfd"]
        sys_log.error(f"{protocol} connect failed!")
        return False, lt.get("sockfd", -1)

    def data_wakeup_socket(self, socket_type: int, iface_name: str, target_ip: str, target_port: int,
                           dev_index: int = 1) -> Tuple[bool, str]:
        """
        模组内
        Args:
            socket_type: 0 -- TCP 1 -- UDP
            iface_name: 网卡名称
            target_ip: tcp/udp服务端目标地址
            target_port: 服务端端口号 (1-65535)
            dev_index: 设备索引(1-based)
        Returns:
            Tuple[bool, str]: (连接状态, 客户端句柄信息)
        """
        para = {
            "socket_type": socket_type,
            "iface_name": iface_name,
            "target_ip": target_ip,
            "target_port": target_port
        }
        protocol = "TCP" if socket_type == 0 else "UDP"
        sys_log.debug(f"{protocol} connecting to wakeup socket……")
        cmd_dic = self.__build_action_package(SYSTEM_SERVER_ID, ActionType.SYSTEM_ACTION, UtilFun.DATA_WAKE, para)
        result, lt = self.__send_action_package(cmd_dic, dev_index, socket_timeout=200)
        if lt.get("client_id", ""):
            sys_log.debug(f"{protocol} connected from wakeup socket")
            return True, lt["client_id"]
        sys_log.error(f"{protocol} connect wakeup socket failed!")
        return False, lt.get("client_id", "")

    def module_socket_exit(self, sock_fd: int, dev_index: int = 1) -> bool:
        """
        模组内关闭socket
        Args:
            sock_fd: socket文件描述符
            dev_index: 设备索引(1-based)
        Returns:
            bool: 成功返回True，失败返回False
        """
        para = {"sockfd": sock_fd}
        sys_log.debug(f"socket {sock_fd} disconnecting")
        cmd_dic = self.__build_action_package(SYSTEM_SERVER_ID, ActionType.SYSTEM_ACTION, UtilFun.SOCKET_EXIT, para)
        result, lt = self.__send_action_package(cmd_dic, dev_index)
        if lt.get("ret", -1) == 0:
            sys_log.debug(f"socket {sock_fd} disconnected")
            return True
        sys_log.error(f"socket {sock_fd} disconnect failed!")
        return False

    def module_socket_rx_tx(self, sock_fd: int, socket_type: int, target_ip: str, target_port: int,
                            packet_size: int = 1024, timeout: int = 10, dev_index: int = 1) -> bool:
        """
        模组内socket发送接收数据
        Args:
            sock_fd: socket文件描述符
            socket_type: socket类型 0 -- TCP 1 -- UDP
            target_ip: tcp/udp服务端目标地址
            target_port: 服务端端口号 (1-65535)
            packet_size: 包大小
            timeout: 超时时间
            dev_index: 设备索引(1-based)
        Returns:
            bool: 成功返回True，失败返回False
        Examples:
            module_socket_rx_tx(sock_fd=1, socket_type=0, target_ip="192.168.1.1", target_port=80, packet_size=1024, timeout=10)
        """
        para = {
            "sockfd": sock_fd,
            "socket_type": socket_type,
            "target_ip": target_ip,
            "target_port": target_port,
            "packet_size": packet_size,
            "timeout": timeout
        }
        protocol = "TCP" if socket_type == 0 else "UDP"
        sys_log.debug(f"socket {sock_fd} {protocol} tx rx data")
        cmd_dic = self.__build_action_package(SYSTEM_SERVER_ID, ActionType.SYSTEM_ACTION, UtilFun.SOCKET_TX_RX, para)
        result, lt = self.__send_action_package(cmd_dic, dev_index)
        if lt.get("ret", -1) == 0:
            sys_log.debug(f"socket {sock_fd} {protocol} rx data success.")
            return True
        sys_log.error(f"socket {sock_fd} {protocol} rx data failed!")
        return False

    def module_socket_test(self, socket_type: int, iface_name: str, target_ip: str, target_port: int,
                           packet_size: int = 1024, timeout: int = 10, dev_index: int = 1) -> bool:
        """
        模组内socket测试
        Args:
            socket_type: socket类型 0 -- TCP 1 -- UDP
            iface_name: 网卡名称
            target_ip: tcp/udp服务端目标地址
            target_port: 服务端端口号 (1-65535)
            packet_size: 包大小
            timeout: 超时时间
            dev_index: 设备索引(1-based)
        Returns:
            bool: 成功返回True，失败返回False
        """
        para = {
            "socket_type": socket_type,
            "iface_name": iface_name,
            "target_ip": target_ip,
            "target_port": target_port,
            "packet_size": packet_size,
            "timeout": timeout
        }
        protocol = "TCP" if socket_type == 0 else "UDP"
        sys_log.debug(f"socket {protocol} test start")
        cmd_dic = self.__build_action_package(SYSTEM_SERVER_ID, ActionType.SYSTEM_ACTION, UtilFun.SOCKET_TEST, para)
        result, lt = self.__send_action_package(cmd_dic, dev_index)
        if lt.get("ret", -1) == 0:
            sys_log.debug(f"socket {protocol} test success.")
            return True
        sys_log.error(f"socket {protocol} test failed!")
        return False

    def module_write_file(self, file_path: str, hex_str: str, size: float, dev_index: int = 1) -> bool:
        """
        模组内写文件
        Args:
            file_path: 模组内文件路径
            hex_str: 十六进制字符串
            size: 包大小
            dev_index: 设备索引(1-based)
        Returns:
            bool: 成功返回True，失败返回False
        """
        para = {"file_path": file_path, "hex_str": hex_str, "size": size}
        cmd_dic = self.__build_action_package(SYSTEM_SERVER_ID, ActionType.SYSTEM_ACTION, UtilFun.WRITE_FILE, para)
        result, lt = self.__send_action_package(cmd_dic, dev_index)
        return True if lt.get("ret", -1) == 0 else False

    def module_read_file(self, file_path: str, size: int, dev_index: int = 1) -> str:
        """
        模组内读文件
        Args:
            file_path: 模组内文件路径
            size: 读取缓存大小
            dev_index: 设备索引(1-based)
        Returns:
            str: 十六进制字符串
        """
        para = {"file_path": file_path, "size": size}
        cmd_dic = self.__build_action_package(SYSTEM_SERVER_ID, ActionType.SYSTEM_ACTION, UtilFun.READ_FILE, para)
        result, lt = self.__send_action_package(cmd_dic, dev_index)
        return lt.get("hex_data", "")

    def get_module_time(self, mode: int = 0, dev_index: int = 1) -> Union[int, float]:
        """
        获取模组时间
        Args:
            mode: 0 -- 系统时间； 1 -- 系统运行时间
            dev_index: 设备索引(1-based)
        Returns:
            -1: 失败 其他：时间戳
        """
        fun_id = UtilFun.GET_TIME_ID if mode == 0 else UtilFun.GET_TIME_ID2
        cmd_dic = self.__build_action_package(SYSTEM_SERVER_ID, ActionType.SYSTEM_ACTION, fun_id)
        result, lt = self.__send_action_package(cmd_dic, dev_index)
        if result != 0:
            return -1
        time_data = lt["cur_time"] if mode == 0 else lt["mono_time"]
        divisor = 1e6 if mode == 0 else 1e9
        return time_data["time_sec"] + time_data[f"time_{'usec' if mode == 0 else 'nsec'}"] / divisor

    def pkg_module_logs(self, case_name: str, dev_index: int = 1) -> bool:
        """
        打包模块日志
        Args:
            case_name: 测试用例编号
            dev_index: 设备索引(1-based)
        Returns:
            bool: 成功返回True，失败返回False
        """
        para = {"case_name": case_name}
        cmd_dic = self.__build_action_package(SYSTEM_SERVER_ID, ActionType.SYSTEM_ACTION, UtilFun.GET_LOGS, para)
        result, lt = self.__send_action_package(cmd_dic, dev_index, socket_timeout=60)
        return True if result == 0 else False

    def send_case_num_to_module(self, case_name: str, dev_index: int = 1) -> bool:
        """
        发送测试用例编号到模块
        Args:
            case_name: 测试用例编号
            dev_index: 设备索引(1-based)
        Returns:
            bool: 成功返回True，失败返回False
        """
        para = {"case_name": case_name}
        cmd_dic = self.__build_action_package(SYSTEM_SERVER_ID, ActionType.SYSTEM_ACTION, UtilFun.CASE_START, para)
        result, lt = self.__send_action_package(cmd_dic, dev_index, socket_timeout=10)
        return True if result == 0 else False

    def write_append_file(self, file_path: str, hex_str: str, size: int, dev_index: int = 1) -> bool:
        """
        模组内写文件,追加
        Args:
            file_path: 模组内文件路径
            hex_str: 16进制字符串
            size: 字符串长度
            dev_index: 设备索引(1-based)
        Returns:
            bool: 成功返回True，失败返回False
        """
        para = {"file_path": file_path, "hex_str": hex_str, "size": size}
        cmd_dic = self.__build_action_package(SYSTEM_SERVER_ID, ActionType.SYSTEM_ACTION, UtilFun.WRITE_APPEND_FILE,
                                              para)
        result, lt = self.__send_action_package(cmd_dic, dev_index)
        return True if lt.get("ret", -1) == 0 else False


poseidon = Poseidon()


@dataclass
class PoseidonExecute(Poseidon):
    server_id: int
    action_type: int
    action_id: Dict[str, int]

    def execute_action(
            self,
            para: Optional[Dict[str, any]],
            expect: int,
            dev_index: int = 1,
            socket_timeout: int = 60
    ) -> Optional[Union[str, Dict[str, any]]]:
        """
        执行 action 请求
        Args:
            para: 请求参数字典
            expect: 预期结果
            dev_index: 设备索引(1-based)
            socket_timeout: socket超时时间
        Returns:
            批量执行返回 None，否则返回执行结果
        """
        action_name = inspect.getouterframes(inspect.currentframe(), 2)[1].function
        act_id = self.action_id[action_name]
        act_pack = self.__build_action_package(self.server_id, self.action_type, act_id, para, expect)
        ret, output = self.__send_action_package(act_pack, dev_index, socket_timeout=socket_timeout)
        if ret == ActionResult.ACTION_PASS:
            sys_log.info(f'RX {dev_index} {action_name} --- PASS')
            if output:
                sys_log.info(output)
            return output
        sys_log.error(f'{action_name} --- FAIL (Expt:{expect}, Return:{output.get("reason")})')
        raise Exception(f'ACTION FAIL:{action_name},para:{para}')

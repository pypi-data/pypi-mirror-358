# -*- coding:utf-8 -*-
"""
Created on 2022年8月23日
@author: 黄泽鹏
"""
import http.client
import json
import socket

from poseidon_module.core.decorators import TraceActionMeta
from poseidon_module.core.logger import sys_log


class _Http:
    def __init__(self):
        self.http_header = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

    def send_post(self, server_ip: str, server_port: int, data: dict):
        """发送HTTP POST请求并返回响应
        Args:
            server_ip: 服务器IP地址
            server_port: 服务器端口
            data: 要发送的数据(dict)
        Returns:
            tuple: (status_code, response_data)
        Raises:
            ConnectionError: 连接相关错误
            TimeoutError: 请求超时
            ValueError: JSON解析错误
        """
        url = f"{server_ip}:{server_port}"
        sys_log.info(f"Connecting to HTTP server: {url}")
        ht = None
        try:
            ht = http.client.HTTPConnection(url, timeout=10)
            send_data = json.dumps(data).encode("utf-8")
            sys_log.debug(f"Sending data: {data}")
            ht.request("POST", "", body=send_data, headers=self.http_header)
            rt = ht.getresponse()
            response_data = rt.read().decode("utf-8")
            if rt.status >= 400:
                sys_log.error(f"HTTP error: {rt.status} - {rt.reason}")
                raise ConnectionError(f"Server returned {rt.status}")
            recv_data = json.loads(response_data)
            sys_log.debug(f"Received response: {recv_data}")
            return rt.status, recv_data
        except http.client.HTTPException as e:
            sys_log.error(f"HTTP error: {str(e)}")
            raise ConnectionError(f"HTTP error: {str(e)}")
        except json.JSONDecodeError as e:
            sys_log.error(f"JSON decode error: {str(e)}")
            raise ValueError(f"Invalid JSON response: {str(e)}")
        except socket.timeout:
            sys_log.error("Request timeout")
            raise TimeoutError("Request timeout")
        finally:
            ht.close() if ht is not None else None


class Http(_Http, metaclass=TraceActionMeta):
    def __init__(self):
        super().__init__()

    def http_handshake_to_server(self, server_ip="47.110.136.146", port=4991):
        status, data = super().send_post(server_ip, port, {"command": "handshake"})
        if status == 200:
            return True, data
        else:
            return False, "与服务器握手失败！"

    def http_send_wakeup_data(self, client_id, server_ip="47.110.136.146", port=4991):
        status, data = super().send_post(server_ip, port, {"command": "tcp_send_data", "client_id": client_id})
        if status == 200:
            return True, data
        else:
            return False, data

    def http_close_client_socket(self, client_id, server_ip="47.110.136.146", port=4991):
        status, data = super().send_post(server_ip, port, {"command": "close_tcp_connect", "client_id": client_id})
        if status == 200:
            return True, data
        else:
            return False, data

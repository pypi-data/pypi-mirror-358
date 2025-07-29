import socket
import time
import json
from datetime import datetime
from enum import IntEnum
from poseidon_module.core.decorators import PoseidonError


# | 0xAA | 0xFF | Length | FUNC | Data... | Checksum |

class HeadID(IntEnum):
    HEAD_1 = 0xAA
    HEAD_2 = 0xFF


class FuncID(IntEnum):
    AUTH = 0x01
    HEART_BEAT = 0x02
    TEST_INFO = 0x03
    TEST_FAIL = 0x04
    TEST_END = 0x05


def calculate_checksum(data):
    return sum(data) & 0xFF


def build_packet(data):
    header = bytes([HeadID.HEAD_1, HeadID.HEAD_2])
    length = bytes([len(data)])
    checksum = calculate_checksum(header + length + data)
    return header + length + data + bytes([checksum])


def parse_packet(buffer):
    packets = []
    while len(buffer) >= 4:
        if buffer[0] != HeadID.HEAD_1 or buffer[1] != HeadID.HEAD_2:
            print("Invalid packet header")
            buffer = buffer[1:]
            continue

        data_length = buffer[2]
        packet_length = 3 + data_length + 1

        if len(buffer) < packet_length:
            break

        packet = buffer[:packet_length]
        buffer = buffer[packet_length:]

        received_checksum = packet[-1]
        calculated_checksum = calculate_checksum(packet[:-1])

        if received_checksum != calculated_checksum:
            print("Checksum mismatch")
            continue

        payload = packet[3:-1]
        packets.append(payload)

    return packets, buffer


RECONNECT_COUNT = 10


def update_lt_pr_report(g_args, target_total, reruns, num, err_info="", status=0):
    g_args.gl["lt_pr_report"]["target_total"] = target_total
    g_args.gl["lt_pr_report"]["reruns"] = reruns
    g_args.gl["lt_pr_report"]["round"] = num
    if status == 0:
        g_args.gl["lt_pr_report"]["grand_total"] += 1
        g_args.gl["lt_pr_report"]["cur_total"] += 1
        if g_args.gl["lt_pr_report"]["cur_total"] > g_args.gl["lt_pr_report"]["highest_total"]:
            g_args.gl["lt_pr_report"]["highest_total"] = g_args.gl["lt_pr_report"]["cur_total"]
        if g_args.gl["G_MONITOR_FLAG"]:
            g_args.gl["monitor_cli"].set_test_info(g_args.gl["lt_pr_report"])
            if g_args.gl["lt_pr_report"]["cur_total"] == g_args.gl["lt_pr_report"]["target_total"]:
                g_args.gl["monitor_cli"].test_end_notify_server(0)
    if status == 1:
        g_args.gl["lt_pr_report"]["grand_total"] += 1
        test_round = g_args.gl["lt_pr_report"]["cur_total"]
        g_args.gl["lt_pr_report"]["cur_total"] = 0
        g_args.gl["lt_pr_report"]["fail_time"] = datetime.now().strftime('%m%d%H%M%S')
        if g_args.gl["G_MONITOR_FLAG"]:
            if g_args.gl["lt_pr_report"]["reruns"] + 1 == g_args.gl["lt_pr_report"]["round"]:
                g_args.gl["monitor_cli"].test_end_notify_server(1)
            else:
                g_args.gl["monitor_cli"].test_fail_notify_server()
        raise PoseidonError(f"目标次数{target_total}，重试轮数{reruns}，第{num}轮测试，第{test_round}次循环，{err_info}")


class TCPClient:
    def __init__(self, client_id, project_name, remote_info):
        print(f'ENV_DI:{client_id}, TEST_PROJECT:{project_name}, REMOTE:{remote_info}')
        self.client_id = client_id
        self.client_info = {'name': project_name, 'remote': remote_info}
        self.test_info = {'target_total': 0, 'grand_total': 0, 'highest_total': 0, 'fail_time': ''}
        self.client_socket = None
        self.reconnect_count = RECONNECT_COUNT

    def handle_recv_data(self, func_id, data):
        if func_id == FuncID.AUTH:
            auth_response = build_packet(
                bytes([FuncID.AUTH, self.client_id]) + json.dumps(self.client_info).encode("utf-8"))
            self.client_socket.send(auth_response)
        elif func_id == FuncID.HEART_BEAT:
            self.reconnect_count = RECONNECT_COUNT
            self.client_socket.send(build_packet(bytes([FuncID.HEART_BEAT])))
        elif func_id == FuncID.TEST_INFO:
            # print("Get TEST_INFO")
            self.client_socket.send(
                build_packet(bytes([FuncID.TEST_INFO]) + json.dumps(self.test_info).encode("utf-8")))
        else:
            print("Server response:", data.decode())

    def test_fail_notify_server(self):
        if self.client_socket is not None:
            self.client_socket.send(build_packet(bytes([FuncID.TEST_FAIL])))
            return True
        return False

    def test_end_notify_server(self, result):
        if self.client_socket is not None:
            self.client_socket.send(
                build_packet(bytes([FuncID.TEST_END, result]) + json.dumps(self.test_info).encode("utf-8")))
            return True
        return False

    def set_test_info(self, test_info):
        self.test_info['target_total'] = test_info["target_total"]
        self.test_info['grand_total'] = test_info["grand_total"]
        self.test_info['highest_total'] = test_info["highest_total"]
        self.test_info['fail_time'] = test_info["fail_time"]

    def connect_tcp_server(self, server_ip, server_port):
        authenticated = False
        keyboard = False
        while self.reconnect_count:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((server_ip, server_port))
                print("Connected to server")
                buffer = bytes()
                while True:
                    data = self.client_socket.recv(1024)
                    if not data:
                        print("Server closed connection")
                        break

                    buffer += data
                    packets, buffer = parse_packet(buffer)

                    for payload in packets:
                        if not authenticated:
                            if len(payload) == 1 and payload[0] == FuncID.AUTH:
                                print("Received authentication request")
                                self.handle_recv_data(payload[0], payload)
                                print("Sent authentication response")
                            elif b"successful" in payload:
                                authenticated = True
                                print("Authentication successful")
                        else:
                            self.handle_recv_data(payload[0], payload)

            except KeyboardInterrupt:
                print("\nClient shutting down...")
                keyboard = True
            except Exception as e:
                print(e)
            finally:
                self.client_socket.close()
                self.client_socket = None
                print("Disconnected from server")
                if keyboard:
                    return
                self.reconnect_count -= 1
                if authenticated is False:
                    return
            print('try reconnect server...')
            time.sleep(10)
        print('connect server fail!')



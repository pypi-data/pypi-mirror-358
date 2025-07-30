# -*- coding:utf-8 -*-
import binascii
import ctypes
import math
import os
import random
import time
import tkinter as tk
import zipfile
from datetime import datetime
from tkinter import messagebox
from typing import Any, Set, Optional
from typing import Dict, List, Union, Tuple

import serial
import serial.tools.list_ports
from poseidon_module.core.const import *
from poseidon_module.core.decorators import trace_action, PoseidonError
from poseidon_module.core.globals import Globals
from poseidon_module.core.logger import sys_log
from poseidon_module.utils._codec import codec
from poseidon_module.utils._registry import register
from poseidon_module.utils._relay import relay
from poseidon_module.utils._reorder import reorder, get_operator_by_phone_num
from poseidon_module.utils.uart import Uart


@trace_action
def bind_devices_info(communication: int = COMMUNICATION_WITH_WLAN):
    """
    绑定设备信息 （调用前必须先加载配置信息）
    Args:
        communication: 通信方式
        Raises:
            PoseidonError: 配置信息未加载
            Exception: 通信方式错误
    Returns:
    """
    config = Globals.get("Config")
    if not config:
        raise PoseidonError("配置信息未加载!!!!")
    baud_rate = Globals.get("BAUD_RATE")
    app_list = []
    if communication == COMMUNICATION_WITH_UART:
        raise Exception("暂不支持")
    assert config.get("G_DEV_IDS") is not None, "设备ID不能为空"
    for i, dev_id in enumerate(config.get("G_DEV_IDS")):
        debug_port = config.get("G_DEBUGS")[i]
        debug_ser = Uart(debug_port, baud_rate) if debug_port != "COM0" else None
        app_info = {
            "dev_id": dev_id,
            "communication": communication,
            "pwd": config.get("G_DEV_PWD")[i],
            "phone_num": config.get("G_PHONE_NUM")[i],
            "relay_info": config.get("G_RES")[i],
            "debug_port": config.get("G_DEBUGS")[i],
            "debug_obj": debug_ser,
            "module_info": config.get("G_MODULE_INFO")[i],
            "dev_gw": Globals.get("DEV_GW"),
            "dev_ip": ""
        }
        app_list.append(app_info)
    Globals.set("PoseidonList", app_list)


def reorder_devices_info():
    marks = Globals.get("Config").get("marks", [])
    return reorder.reorder_device_info_lst_by_tag(marks)


def restore_devices_info():
    reorder.restore_device_info_lst()


def get_operator(phone_num):
    return get_operator_by_phone_num(phone_num)


@trace_action
def check_9008_port(times: int = 30) -> Tuple[bool, Optional[str]]:
    """
    检查9008端口是否存在
    Args:
        times: 检查次数
    Returns:
        Tuple[bool, Optional[str]]: 端口是否存在，端口号
    """
    for i in range(times):
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            if "9008" in p.description.upper() or "900E" in p.description.upper():
                return True, p.device
        time.sleep(1.5)
    return False, None


def get_module_usb_devices():
    """
    获取模块 USB 所有端口枚举信息
    Returns:
        Dict[str, List[Dict[str, str]]]: 设备ID和端口信息
    """
    return register.regedit_get_module_usb_devices()


@trace_action
def update_dict(set_info: Optional[Union[Dict[str, Any], str]], default: Optional[Dict[str, Any]] = None
                ) -> Optional[Dict[str, Any]]:
    """
    安全更新字典数据
    Args:
        set_info: 要合并的字典/字符串(自动转空字典)/None
        default: 基础字典(默认新建空字典)
    Returns:
        合并后的新字典或None
    Raises:
        TypeError: 当set_info不是dict/str/None时
    """
    if set_info is None:
        return None
    if isinstance(set_info, str):
        set_info = {}
    if not isinstance(set_info, dict):
        raise TypeError(f"需要dict/str/None，得到{type(set_info)}")
    result = {} if default is None else default.copy()  # 确保不影响原字典
    result.update(set_info)
    return result


@trace_action
def get_dict_keys(dict_obj: Any, key_list: List[str], visited: Set[int] = None) -> None:
    """
    递归获取嵌套字典/列表中的所有键名
    Args:
        dict_obj: 输入字典/列表对象
        key_list: 存储键名的结果列表
        visited: 用于检测循环引用的对象ID集合
    """
    if visited is None:
        visited = set()
    obj_id = id(dict_obj)
    if obj_id in visited:  # 防止循环引用
        return
    visited.add(obj_id)
    if isinstance(dict_obj, dict):
        for key in dict_obj:
            key_list.append(key)
            get_dict_keys(dict_obj[key], key_list, visited)
    elif isinstance(dict_obj, list):
        for item in dict_obj:
            get_dict_keys(item, key_list, visited)


@trace_action
def manual_step(msg: str, title: str = "确认") -> bool:
    """
    弹出确认框，手动输入
    :param msg:
    :param title:
    :return:
    """
    try:
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes("-topmost", 1)
        result = messagebox.askyesno(title, msg)
    except Exception as e:
        raise Exception(f"无法创建Tk实例: {str(e)}") from e
    if root:
        root.destroy()
    return result


@trace_action
def manual_input_msg(msg: str) -> Optional[str]:
    """
    弹出输入框，手动输入并获取输入内容
    Args:
        msg: 提示信息文本
    Returns:
        用户输入的文本内容
    """
    result = None
    root = tk.Tk()
    root.title("文本输入框")
    root.wm_attributes("-topmost", 1)
    root.resizable(False, False)
    tk.Label(root, text=msg).grid(row=0, column=0, columnspan=2, pady=5)
    tk.Label(root, text="输入内容:").grid(row=1, column=0, sticky="e")
    entry = tk.Entry(root, width=30)
    entry.grid(row=1, column=1, padx=5, pady=5)
    # 焦点管理
    entry.focus_set()
    root.after(100, lambda e: entry.focus_force(), None)

    def on_confirm():
        nonlocal result
        result = entry.get()
        root.destroy()

    def on_cancel():
        nonlocal result
        result = None
        root.destroy()

    # 按钮布局
    btn_frame = tk.Frame(root)
    btn_frame.grid(row=2, column=0, columnspan=2, pady=5)
    tk.Button(btn_frame, text="取消", command=on_cancel, width=8).pack(side="right", padx=5)
    tk.Button(btn_frame, text="确认", command=on_confirm, width=8).pack(side="right")
    root.bind("<Return>", lambda e: on_confirm())  # 绑定回车键
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"+{x}+{y}")
    root.mainloop()
    return result


@trace_action
def stop_thread(tid: int) -> Tuple[bool, int]:
    """
    强制停止线程
    Args:
        tid: 线程ID
    Returns:
        成功停止返回(True, 0)，失败返回(False, 1/2)
    """
    sys_log.info(f"强制停止线程ID:{tid}")
    tid = ctypes.c_long(tid)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(SystemExit))
    if res == 0:
        return False, 1
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        return False, 2
    return True, 0


@trace_action
def content_create(min_Len: int, max_Len: int, char_type: int = 0) -> Tuple[int, str, str]:
    """
    生成随机长度随机ira普通字符串
    Args:
        min_Len: 字符串最小长度
        max_Len: 字符串最大长度
        char_type:
            0 -- 普通字符 只包含数字和字母  数字 大写26个字母 小写26个字母
            1 -- gsm 默认字符
            3 -- 中文字符
            4 -- 空字符
            5 -- ascii 标点符号
            6 -- gsm 默认字符 和 ascii 标点符号 的交集
            7 -- gsm 默认字符 和 普通字符 的差集
    Returns:
        3个元素的tuple: (长度, 随机字符串, 随机字符串编码)
    """
    min_val, max_val = sorted((int(min_Len), int(max_Len)))
    length = random.randint(min_val, max_val)
    char_type = int(char_type)
    if char_type == 0:
        charset = set(range(0x30, 0x3A)) | set(range(0x41, 0x5B)) | set(range(0x61, 0x7B))
    elif char_type == 1:
        charset = set([ord(i) for i in gsm7_base.values()])
    elif char_type == 3:
        charset = set(range(0x4E00, 0x9FFF))
    elif char_type == 4:
        return 0, '', ''
    elif char_type == 5:
        charset = set(range(0x3A, 0x41)) | set(range(0x20, 0x30)) | set(range(0x5B, 0x61)) | set(
            range(0x7B, 0x7F))
    elif char_type == 6:
        spec_str = set(range(0x3A, 0x41)) | set(range(0x20, 0x30)) | set(range(0x5B, 0x61)) | set(
            range(0x7B, 0x7F))
        charset = spec_str & set([ord(i) for i in gsm7_base.values()])
    elif char_type == 7:
        set0 = set(range(0x30, 0x3A)) | set(range(0x41, 0x5B)) | set(range(0x61, 0x7B))
        set1 = set([ord(i) for i in gsm7_base.values()])
        charset = set1 - set0
    else:
        raise Exception("输入参数错误！")

    if length > len(charset) > 0:
        charset = list(charset) * math.ceil(length / len(charset))
    random_str_num = random.sample(list(charset), length)
    random_str = "".join([chr(i) for i in random_str_num])
    random_str_code = "".join(["{0:04X}".format(n) for n in random_str_num])
    return length, random_str, random_str_code


@trace_action
def array2string(content_array: list, formats: int) -> str:
    """
    将数值数组转换为字符串，支持多种编码格式
    Args:
        content_array: 输入数组(包含有符号/无符号整数)
        formats: 转换模式(0/1:单字节模式, 2:双字节模式)
    Returns:
        转换后的字符串
    Raises:
        ValueError: 当输入格式无效时
    """
    processed = []
    for item in content_array:
        if not isinstance(item, (int, float)):
            raise ValueError("数组元素必须是数字类型")
        processed.append(item + 256 if item < 0 else item)
    if formats in (0, 1):
        try:
            return "".join(chr(item) for item in processed)
        except ValueError as e:
            raise ValueError(f"无效的字符编码: {e}")
    if formats == 2:
        if len(processed) % 2 != 0 and processed[-1] == 0:
            processed = processed[:-1]
        if len(processed) % 2 != 0:
            raise ValueError("双字节模式需要偶数长度数组")
        result = []
        for i in range(0, len(processed), 2):
            try:
                char_code = processed[i] * 256 + processed[i + 1]
                result.append(chr(char_code))
            except ValueError as e:
                raise ValueError(f"无效的双字节编码: {e}")
        return "".join(result)
    raise ValueError("不支持的格式模式")


@trace_action
def string2hex(input_str: str, encoding: str = 'utf-8') -> Optional[str]:
    """将字符串转换为十六进制表示
    Args:
        input_str: 要转换的字符串
        encoding: 编码格式(默认为utf-8)
    Returns:
        十六进制表示的字符串，如果输入无效则返回None
    Raises:
        UnicodeEncodeError: 当编码失败时
    """
    if not isinstance(input_str, str):
        return None
    try:
        bytes_string = input_str.encode(encoding)
        return binascii.hexlify(bytes_string).decode('ascii')
    except (UnicodeEncodeError, binascii.Error) as e:
        print(f"转换失败: {str(e)}")
        return None


@trace_action
def split_timestamp(timestamp: Union[float, str, int]) -> Tuple[int, int]:
    """
    将浮点型时间戳拆分为整数秒和小数微秒部分
    Args:
        timestamp: float/str类型的时间戳（如1633047123.456789）
    Returns:
        tuple: (秒, 微秒) 微秒部分固定6位补零
    Raises:
        ValueError: 输入格式错误时抛出异常
    """
    if not isinstance(timestamp, (float, str, int)):
        raise TypeError("Input must be float or string")
    str_ts = str(timestamp).strip()
    if '.' not in str_ts:
        return int(str_ts), 0
    try:
        sec_part, usec_part = str_ts.split('.')
        usec = f"{usec_part[:6]:<06}"  # 截断并右对齐补零
        return int(sec_part), int(usec)
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid timestamp format: {str_ts}") from e


@trace_action
def convert_to_bj_timestamp(utc_time: str, time_format: str, is_utc: bool = True) -> float:
    """
    将UTC/本地时间字符串转换为北京时间戳（UTC+8）
    Args:
        utc_time: UTC时间字符串 (格式: YYYY-MM-DD HH:MM:SS)
        time_format: UTC时间字符串格式
        is_utc: 是否是UTC时间
    Returns:
        对应的北京时间戳（秒级精度）
    Raises:
        ValueError: 当输入时间格式无效时
    """
    try:
        utc_dt = datetime.strptime(utc_time, time_format)
        timestamp = time.mktime(utc_dt.timetuple())
        return timestamp + 28800 if is_utc else timestamp
    except ValueError as e:
        raise ValueError(f"Invalid UTC time format: {utc_time}") from e


def pdu_encode(
        phone_num: str = '',
        data: str = '',
        cs_num: str = "",
        format_type: int = 0,
        class_valid: int = 1,
        message_class: int = 0,
        expect_segments: int = 1,
        current_no: int = 1) -> Tuple[str, int]:
    """
    PDU编码函数
    Args:
        phone_num: 目标手机号
        data: pdu 短信内容
        cs_num: 短信中心号码
        format_type: 编码类型(0=7BIT,1=8BIT,2=UCS2)
        class_valid: 消息类别是否有效
        message_class: 消息类别(0-4)
        expect_segments: 预期分包数
        current_no: 当前分包序号
    Returns:
        Tuple[str, int]: (pdu编码字符串, 编码长度)
    """
    return codec.pdu_encode(phone_num, data, cs_num, format_type, class_valid, message_class, expect_segments,
                            current_no)


def control_relay(port: str, action: str, re_type: int = 0, num: Union[int, List[int]] = 1) -> bool:
    """
    串口控制继电器方法
    Args:
        port: 串口号 (如 "COM44")
        action: 控制状态 (0: COM-NO, 1: COM-NC)
        re_type: 继电器类型 (0-5)
        num: 继电器编号或ID列表(仅re_type=5时使用列表)
    Returns:
        bool: 操作是否成功
    """
    return relay.serial_control_relay(port, action, re_type, num)


def send_at_cmd(cmd: str, port: str, baudrate: int = 921600, timeout: int = 60) -> Tuple[bool, Optional[str]]:
    """
    AT指令发送
    Args:
        cmd: 待发送指令(自动追加\r\n)
        port: 串口号(如COM3)
        baudrate: 波特率(默认921600)
        timeout: 总超时秒数(默认60)
    Returns:
        tuple: (是否成功, 响应内容/None)
    """
    end_flags = {
        "OK": True,
        "ERROR": False,
        "CONNECT": True,
        "NO CARRIER": False,
        "BUSY": False
    }
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            ser.write(f"{cmd}\r\n".encode('utf-8'))
            ser.flush()
            buffer = []
            start_time = time.time()
            while time.time() - start_time <= timeout:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if not line:
                    continue
                buffer.append(line)
                if line in end_flags:
                    return end_flags[line], '\n'.join(buffer)
                if "ERROR" in line:
                    return False, None
            return False, None
    except serial.SerialException as e:
        sys_log.error(f"串口异常: {e}")
        return False, None
    except Exception as e:
        sys_log.error(f"系统异常: {e}")
        return False, None


def control_shielding_box(port: str, action: int) -> bool:
    """串口控制屏蔽箱
    Args:
        port: 串口号(如COM44)
        action: 继电器状态(1:关闭 0:打开)
    Returns:
        bool: 操作是否成功
    """
    valid_actions = {0, 1}
    cmd_map = {1: b"close\r\n", 0: b"open\r\n"}
    resp_tags = {0: "OK", 1: "READY"}
    if action not in valid_actions:
        sys_log.error(f"无效操作:{action}")
        return False
    try:
        with serial.Serial(port=port, baudrate=9600, timeout=1) as client:
            time.sleep(2)  # 等待串口稳定
            cmd = cmd_map[action]
            expected_tag = resp_tags[action]
            for attempt in range(3):
                sys_log.info(f"尝试#{attempt + 1} 操作屏蔽箱")
                client.write(cmd)
                client.flush()
                start_time = time.time()
                while time.time() - start_time < 10:  # 总超时10秒
                    ret_info = client.readline().decode('utf-8').strip()
                    if ret_info:
                        sys_log.debug(f"收到响应:{ret_info}")
                        if expected_tag in ret_info:
                            return True
                    time.sleep(0.5)  # 降低CPU占用
                time.sleep(1)  # 重试间隔
            return False
    except serial.SerialException as e:
        sys_log.error(f"串口异常:{str(e)}")
    except Exception as e:
        sys_log.error(f"未知错误:{str(e)}")
    return False


def get_wifi_channel_list(country_code: str, ap_index: int, mode: int = 1) -> Tuple[list, list]:
    """
    获取各个国家码支持的信道列表和不支持的信道列表
    Args:
        country_code: 国家码
        ap_index: 热点类型
        mode: 是否包含 STA
    Returns:
        [支持],[不支持]
    """
    map_dic_5 = {'LB': LB, 'BR': BR, 'PE': PE, 'CN': CN, 'RS': RS, 'TN': TN, 'GB': GB, 'DE': DE, 'NL': NL,
                 'CH': CH, 'NO': NO, 'FR': FR, 'BE': BE, 'ES': ES, 'SE': SE, 'IT': IT, 'LU': LU, 'DK': DK,
                 'FI': FI, 'GE': GE, 'MM': MM, 'IN': IN, 'QA': QA, 'IL': IL, 'CO': CO, 'UZ': UZ, 'JO': JO,
                 'MA': MA, 'JP': JP, 'BO': BO, 'KW': KW, 'SA': SA, 'AZ': AZ, 'KZ': KZ, 'MD': MD, 'PR': PR,
                 'PA': PA, 'CL': CL, 'EG': EG, 'BH': BH, 'UY': UY, 'OM': OM, 'AE': AE, 'ZA': ZA, 'AO': AO,
                 'PH': PH, 'LA': LA, 'UA': UA, 'KH': KH, 'GT': GT, 'TJ': TJ, 'VN': VN, 'US': US, 'KR': KR,
                 'HK': HK, 'MO': MO, 'PY': PY, 'CR': CR, 'EC': EC, 'DO': DO, 'TW': TW, 'TH': TH, 'NZ': NZ,
                 'SG': SG, 'MY': MY, 'CA': CA, 'AU': AU, 'MX': MX, 'AR': AR, 'LC': LC, }
    if ap_index == 0:
        return HT1 if country_code in ["US", "CA"] else HT2, [14]
    if mode == 0:
        if country_code in ["GB", "DE", "NL", "CH", "NO", "FR", "BE", "ES", "SE", "IT", "LU", "DK", "FI", "GE",
                            "MM"]:
            return map_dic_5[country_code] + B3, list(set(B1 + B2 + B3_3 + B4) - set(map_dic_5[country_code]))
    return map_dic_5[country_code], list(set(B1 + B2 + B3_3 + B4) - set(map_dic_5[country_code]))


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

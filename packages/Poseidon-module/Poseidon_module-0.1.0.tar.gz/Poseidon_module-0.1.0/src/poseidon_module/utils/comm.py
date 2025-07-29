# -*- coding:utf-8 -*-
import binascii
import ctypes
import math
import random
import time
import tkinter as tk
from datetime import datetime
from tkinter import messagebox
from typing import Any, Dict, List, Set, Optional, Union, Tuple
from poseidon_module.core.decorators import trace_action
from poseidon_module.core.const import gsm7_base
from poseidon_module.core.logger import sys_log


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

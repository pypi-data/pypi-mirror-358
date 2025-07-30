# -*- coding:utf-8 -*-
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class Globals:
    """
    全局配置管理类，支持JSON持久化
    可使用 JSON 文件配置全局变量
    Args:
        _DEFAULTS: 与平台和测试框架相关的默认配置
        BaseLogPath: 日志路径
        CheckDebug: 调试串口检查开关
        ServerState: poseidon_server 服务状态
        PoseidonList: 设备列表
        ActionBuffer: 动作缓存
        CaseName: 当前测试的用例名称
        TestResult: 测试结果
        Tmp: 临时变量
        Config: 全局配置
    """

    # 默认配置值
    _DEFAULTS = {
        "USBMode": 25,
        "START_PROCESS": ["umdp_server", "fb_modemServices"],
        "SLEEP_FLAG": "Suspending console(s)",
        "WAKEUP_FLAG": "suspend exit",
        "DEV_GW": "192.168.101.1",
        "CENTRE_PORT": 30000,
        "SOCKET_TIMEOUT": 60,
        "UDP_INIT_PORT": 40000,
        "APP_DIR": "oemdata",
        "BAUD_RATE": 921600,
        "LOG_CHINESE": True,
        "PLATFORM": "MT2735",
    }

    # 动态属性
    BaseLogPath: str = ""
    CheckDebug: bool = False
    ServerState: bool = False
    PoseidonList: List[Dict[str, Any]] = []
    ActionBuffer: Dict[str, Any] = {}
    CaseName: Optional[str] = None
    TestResult: Dict[str, Any] = {}
    Tmp: Dict[str, Any] = {}
    Config: Dict[str, Any] = {}

    @classmethod
    def initialize(cls, config_path: str = "config.json") -> None:
        """从文件加载配置或使用默认值初始化"""
        try:
            if Path(config_path).exists():
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if key in cls._DEFAULTS:
                            cls._DEFAULTS[key] = value
                        elif hasattr(cls, key):
                            setattr(cls, key, value)
                        else:
                            raise KeyError(f"配置项 {key} 不存在")
        except Exception as e:
            print(f"加载配置失败: {e}, 使用默认配置")

    @classmethod
    def save_json(cls, config_path: str = "config.json") -> bool:
        """保存当前配置到文件"""
        try:
            with open(config_path, 'w') as f:
                json.dump(cls._DEFAULTS, f, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    @classmethod
    def set(cls, key: str, value: Any, auto_save: bool = True) -> bool:
        """设置配置值"""
        if key in cls._DEFAULTS:
            cls._DEFAULTS[key] = value
            if auto_save:
                cls.save_json()
            return True
        if hasattr(cls, key):
            setattr(cls, key, value)
        return False

    @classmethod
    def get(cls, key: str) -> Any:
        """获取配置值"""
        if key in cls._DEFAULTS:
            if getattr(cls, "_DEFAULTS").get(key) is not None:
                return getattr(cls, "_DEFAULTS")[key]
        if hasattr(cls, key):
            return getattr(cls, key)
        raise AttributeError(f"配置项 {key} 不存在")

    @classmethod
    def set_module(cls, key: str, value: Any, dev_index: int) -> None:
        """设置模块信息"""
        if 0 < dev_index <= len(cls.PoseidonList):
            cls.PoseidonList[dev_index - 1][key] = value
        else:
            raise IndexError(f"设备索引 {dev_index} 无效")

    @classmethod
    def get_module(cls, key: str, dev_index: int) -> Any:
        """获取模块配置"""
        if 0 < dev_index <= len(cls.PoseidonList):
            if key in cls.PoseidonList[dev_index - 1].keys() is not None:
                return cls.PoseidonList[dev_index - 1][key]
            raise KeyError(f"设备{dev_index}没有{key}信息！")
        raise IndexError(f"设备索引 {dev_index} 无效")

    @classmethod
    def log_path(cls):
        if cls.BaseLogPath:
            return cls.BaseLogPath
        drives = ["D:", "E:", "F:", "G:", "C:"]
        base_dir = f"/00TestLogs/{cls._DEFAULTS['PLATFORM']}Logs"  # 日志存储根目录, 根据实际情况修改
        for drive in drives:
            try:
                if Path(drive).exists():
                    root_path = Path(drive) / base_dir
                    system_log_path = root_path / "SystemLog"
                    system_log_path.mkdir(parents=True, exist_ok=True)
                    print(f"✅ 日志存储路径已设置: {system_log_path}")
                    setattr(cls, "BaseLogPath", str(root_path))
                    return str(root_path)
            except PermissionError:
                print(f"⚠️ 无权限访问磁盘 {drive}")
            except OSError:
                print(f"⚠️ 磁盘 {drive} 访问错误")
        else:
            print("❌ 未找到可用磁盘，请检查电脑磁盘配置")
            sys.exit(1)

    @classmethod
    def dev_id(cls, dev_index=1):
        return dev_index if isinstance(dev_index, str) else cls.get_module(key='dev_id', dev_index=dev_index)

    @classmethod
    def pwd(cls, dev_index=1):
        return None if isinstance(dev_index, str) else cls.get_module(key='pwd', dev_index=dev_index)

    @classmethod
    def phone_num(cls, slot=1, dev_index=1):
        return cls.get_module(key='phone_num', dev_index=dev_index)[slot - 1]

    @classmethod
    def debug_port(cls, dev_index=1):
        return cls.get_module(key='debug_port', dev_index=dev_index)

    @classmethod
    def debug_obj(cls, dev_index=1):
        return cls.get_module(key='debug_obj', dev_index=dev_index)

    @classmethod
    def debug_queue(cls, dev_index=1):
        return cls.get_module(key='debug_queue', dev_index=dev_index)

    @classmethod
    def module_info(cls, dev_index=1):
        return cls.get_module(key='module_info', dev_index=dev_index)

    @classmethod
    def relay_info(cls, index, dev_index=1):
        relay_info = cls.get_module(key='relay_info', dev_index=dev_index)
        port = relay_info[0][index]
        if cls.get("Config").get("G_ATB", False):
            re_type = 5
            num = [[1, 5], [1, 2], [4, 0], [1, 1], [1, 0]][index]
            return port, re_type, num
        return port, relay_info[2][index], relay_info[1][index]

    @classmethod
    def module_num(cls):
        marks = cls.get("Config").get("marks", [])
        for mark in marks:
            result = re.findall(r"^M(\d+)$", mark)
            if result:
                return int(result[0])
        return 0

    @classmethod
    def slot_list(cls):
        marks = cls.get("Config").get("marks", ["SIM1_SIM12"])
        for mark in marks:
            result = re.findall(r"SIM(\d+)", mark)
            if result:
                return [re.findall(r"\d", i) for i in result]
        return 0

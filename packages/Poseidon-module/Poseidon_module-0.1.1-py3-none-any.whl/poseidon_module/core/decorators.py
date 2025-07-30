# -*- coding:utf-8 -*-
import functools
import inspect
import threading
from datetime import datetime
from typing import Any, Callable, Dict, Type, TypeVar

import pytest
from poseidon_module.core.logger import sys_log

T = TypeVar('T', bound=Callable[..., Any])


def marks(*multi_mark: str) -> Callable[[T], T]:
    """
    安全设置多个pytest标签的装饰器工厂
    Args:
        *multi_mark: 要添加的标签名称(自动转为大写)
    Returns:
        装饰器函数
    Raises:
        ValueError: 当标签包含非法字符时
    Example:
        @setTags('smoke', 'regression')
        def test_example(): ...
    """

    def decorator(func: T) -> T:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        for mark in multi_mark:
            if not mark.isidentifier():
                raise ValueError(f"Invalid mark name: {mark}")
            marker = getattr(pytest.mark, mark.upper())
            wrapper = marker(wrapper)

        return wrapper  # type: ignore

    return decorator


def trace_action(func: T) -> T:
    """装饰器函数，记录方法调用日志及参数信息"""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        param_str = ", ".join(f"{k}={v!r}" for k, v in bound_args.arguments.items() if k != "self")
        sys_log.debug(f"TX [{func.__code__.co_firstlineno:>3}] {func.__qualname__}({param_str})")
        return func(*args, **kwargs)

    return wrapper  # type: ignore


class BaseError(Exception):
    """远驰测试异常基类"""

    def __init__(self, message="未知错误", err_time=""):
        self.err_time = err_time
        self.message = message
        super().__init__(f"[{err_time}]: {message}")


# 子类化
class PoseidonError(BaseError):
    def __init__(self, message):
        start_time = datetime.now().strftime('%m%d%H%M%S')
        super().__init__(message=message, err_time=start_time)


def catch_exceptions(func: T) -> T:
    """增强型异常捕获装饰器，提供分类错误处理和上下文日志"""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except PoseidonError as e:
            sys_log.error(f"测试框架函数失败，可能为环境不兼容问题 | 函数 {func.__qualname__} | 错误: {str(e)}")
            raise PoseidonError("CASE FAIL: 业务规则违反") from e
        except AssertionError as e:
            sys_log.error(f"断言失败 | 函数 {func.__qualname__} | 错误: {str(e)}", exc_info=True)
            raise AssertionError("CASE FAIL: 预期结果不匹配") from e
        except Exception as e:
            sys_log.critical(f"系统异常 | 函数 {func.__qualname__} | 类型: {type(e).__name__} | 错误: {str(e)}",
                             exc_info=True, stack_info=True)
            raise Exception("SYSTEM FAIL: 未处理的运行时异常") from e

    return wrapper  # type: ignore


class TraceActionMeta(type):
    """元类，自动为所有非魔术方法添加日志装饰器"""

    def __new__(cls, name: str, bases: tuple, dct: Dict[str, Any]) -> Type:
        for attr_name, attr in dct.items():
            if callable(attr) and not attr_name.startswith('_') and not isinstance(attr, (staticmethod, classmethod)):
                dct[attr_name] = trace_action(attr)
        return super().__new__(cls, name, bases, dct)


class CatchExceptionsMeta(type):
    """ 元类，给类中函数增加捕获异常装饰器 """

    def __new__(cls, name: str, bases: tuple, dct: Dict[str, Any]) -> Type:
        for attr_name, attr in dct.items():
            if callable(attr) and not attr_name.startswith('__'):  # 假设非魔法方法是实例方法
                dct[attr_name] = catch_exceptions(attr)
        return super().__new__(cls, name, bases, dct)


class SingletonMeta(type):
    """线程安全的单例模式元类优化版"""
    _instances = {}
    _lock = threading.Lock()  # 添加线程锁

    def __call__(cls, *args, **kwargs):
        # 双重检查锁定模式
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

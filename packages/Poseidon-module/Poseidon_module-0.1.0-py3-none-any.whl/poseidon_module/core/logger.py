# -*- coding:utf-8 -*-
import glob
import logging
import logging.handlers
from datetime import timedelta
from threading import RLock
from typing import Optional
from poseidon_module.core.globals import Globals
import colorlog

SYSTEM_LOG_NAME = "SystemLog"
FILE_FORMAT = "[%(asctime)s][%(thread)5d][%(levelname)5s]: %(message)s"
DEFAULT_FORMAT = "%(log_color)s[%(asctime)s][%(thread)5d][%(levelname)5s]: %(message)s"

COLOR_SCHEME = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red'
}
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

import os
import gzip
import time
from logging.handlers import BaseRotatingHandler
from datetime import datetime


class AdvancedRotatingHandler(BaseRotatingHandler):
    def __init__(self, filename, mode='a', max_bytes=0, backup_count=0,
                 when=None, interval=1, encoding=None, delay=False,
                 compress=False, utc=False):
        """
        :param when: 时间单位('S','M','H','D','midnight')
        :param interval: 时间间隔
        :param compress: 是否压缩旧日志
        :param utc: 是否使用UTC时间
        """
        if max_bytes > 0:
            mode = 'a'
        super().__init__(filename, mode, encoding, delay)
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.compress = compress
        self.utc = utc
        self.when = when.upper() if when else None
        self.interval = interval
        self.rollover_at = self._calculate_rollover() if when else None

    def _calculate_rollover(self):
        now = time.time()
        if self.when == 'MIDNIGHT':
            t = self._get_next_midnight(now)
        else:
            t = now + self._get_interval_seconds()
        return t

    @staticmethod
    def _get_next_midnight(current_time):
        dt = datetime.fromtimestamp(current_time)
        midnight = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        midnight += timedelta(days=1)
        return midnight.timestamp()

    def _get_interval_seconds(self):
        if self.when == 'S':
            return 1 * self.interval
        elif self.when == 'M':
            return 60 * self.interval
        elif self.when == 'H':
            return 3600 * self.interval
        elif self.when == 'D':
            return 86400 * self.interval
        return 86400  # 默认1天

    def shouldRollover(self, record):
        if self.stream is None:
            self.stream = self._open()
        # 检查大小轮转
        if self.max_bytes > 0:
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)
            if self.stream.tell() + len(msg) >= self.max_bytes:
                return True
        # 检查时间轮转
        if self.when and time.time() >= self.rollover_at:
            return True
        return False

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None

        # 生成带时间戳的新文件名
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base, ext = os.path.splitext(self.baseFilename)
        base = base.replace("_current", "")
        new_name = f"{base}_{timestamp}{ext}"
        # 执行文件轮转
        if os.path.exists(self.baseFilename):
            os.rename(self.baseFilename, new_name)
            if self.compress:
                self._compress_log(new_name)
        # 清理旧日志
        self._clean_old_logs(base, ext)
        # 更新时间轮转点
        if self.when:
            self.rollover_at = self._calculate_rollover()
        if not self.delay:
            self.stream = self._open()

    @staticmethod
    def _compress_log(filename):
        with open(filename, 'rb') as f_in:
            with gzip.open(filename + '.gz', 'wb') as f_out:
                f_out.writelines(f_in)
        os.remove(filename)

    def _clean_old_logs(self, base, ext):
        pattern = f"{base}_*{ext}"
        if self.compress:
            pattern += '.gz'
        logs = sorted((f for f in glob.glob(pattern) if os.path.isfile(f)), key=os.path.getmtime, reverse=True)
        for old_log in logs[self.backup_count:]:
            try:
                os.remove(old_log)
            except OSError:
                pass


class LogManager:
    """线程安全的日志管理器，支持多日志器和文件日志"""

    _instance = None
    _lock = RLock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._loggers = {}
        return cls._instance

    def register_logger(
            self, name: str = "SystemLog", file_path: Optional[str] = None, level: str = "DEBUG",
            log_to_console: bool = True, log_to_file: bool = True, max_bytes: int = 10 * 1024 * 1024,
            backup_count: int = 10, when: str = "D", interval: int = 1
    ) -> logging.Logger:
        """
        获取或创建配置好的日志器，日志轮转处理同时根据大小和时间两种方式进行，任一条件达到，则进行分包。
        Args:
            name: 日志器名称，默认为SystemLog
            file_path: 日志文件路径，默认为 D:/00TestLogs/MTKLogs + name
            level: 日志级别，默认为DEBUG
            log_to_console: 是否输出到控制台，默认为True
            log_to_file: 是否输出到文件，默认为False
            max_bytes: 文件大小，默认为10M
            backup_count: 备份数量，默认为10
            when: 分包时间单位('S','M','H','D','midnight')，默认为D
            interval: 分包间隔，默认为1
        Returns:
             logging.Logger: 日志器实例
        """
        if name in self._loggers:
            return self._loggers[name]
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)  # 设置总日志级别
        # 避免重复添加handler
        if not logger.handlers:
            if log_to_console:
                self._add_console_handler(logger, level)
            if log_to_file:
                file_path = file_path or Globals.log_path()
                self._add_file_handler(logger, name, file_path, max_bytes, backup_count, when, interval)
        self._loggers[name] = logger
        return logger

    @staticmethod
    def _add_console_handler(logger: logging.Logger, level: str):
        """添加彩色控制台处理器"""
        handler = logging.StreamHandler()
        handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        formatter = colorlog.ColoredFormatter(DEFAULT_FORMAT, log_colors=COLOR_SCHEME)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    def _add_file_handler(self, logger: logging.Logger, name: str, file_path: str, max_bytes: int, backup_count: int,
                          when: str = "D", interval: int = 1):
        """添加带时间戳的文件轮转处理器"""
        with self._lock:
            log_dir = os.path.join(file_path, name)
            os.makedirs(log_dir, exist_ok=True)
            log_path = os.path.join(log_dir, f"{name}_current.log")

        handler = AdvancedRotatingHandler(
            filename=log_path,
            mode="a",
            max_bytes=max_bytes,
            backup_count=backup_count,
            when=when,
            interval=interval,
            encoding='utf-8',
            delay=True,
            compress=True,
            utc=False
        )
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(FILE_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)


# 获取日志管理器实例
log_manager = LogManager()
sys_log = log_manager.register_logger()

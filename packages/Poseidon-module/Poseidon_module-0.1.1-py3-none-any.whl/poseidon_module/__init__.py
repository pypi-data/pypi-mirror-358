import sys

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "Poseidon_module"
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

# 通用工具包
from .utils.comm import *

from .core.decorators import (
    marks,
    trace_action,
    TraceActionMeta,
    PoseidonError,
    catch_exceptions,
    CatchExceptionsMeta,
    SingletonMeta
)

from .core.globals import Globals
from .core.logger import log_manager, sys_log
from .core.poseidon import poseidon, PoseidonExecute

from .utils.device import Device
# wlan 类，支持上下文管理
from .utils.wlan import UtilWlan
# uart 类，支持上下文管理
from .utils.uart import Uart, debug_ser

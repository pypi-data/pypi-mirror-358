# -*- coding:utf-8 -*-
from enum import IntEnum, auto

change_ip_content = '''
@echo off
color B0
::: 获取管理员权限
if exist "%SystemRoot%\SysWOW64" path %path%;%windir%\SysNative;%SystemRoot%\SysWOW64;%~dp0
bcdedit >nul
if '%errorlevel%' NEQ '0' (goto UACPrompt) else (goto UACAdmin)
:UACPrompt
%1 start "" mshta vbscript:createobject("shell.application").shellexecute("""%~0""","::",,"runas",1)(window.close)&exit
exit /B
:UACAdmin
cd /d "%~dp0"
echo;
echo 当前运行路径是：%CD%
echo 已获取管理员权限
echo %0
echo %1
echo %2
echo %3
echo %4
echo %5

echo;
if %1==1 goto ip1
if %1==2 goto dhcp

:ip1
echo 静态IP设置开始……
echo;
echo 正在设置IP及子网掩码
cmd /c netsh interface ip set address name=%2 source=static addr=%3 mask=%4 gateway=%5 gwmetric=3
echo 正在设置DNS服务器……
echo;
cmd /c netsh interface ip ad dnsserver name=%2 address=114.114.114.114 index=1
echo 设置完成！
REM pause
exit

:dhcp
echo 自动设置IP开始....

echo;
echo 自动获取IP地址
echo;
cmd /c netsh interface ip set address name = %2 source = dhcp
cmd /c netsh interface ip set dns name = %2 source = dhcp

echo 设置完成
REM pause
exit
'''
# UART通信方式
COMMUNICATION_WITH_UART = 0x00
# IP通信方式
COMMUNICATION_WITH_WLAN = 0x01
# 系统服务ID
SYSTEM_SERVER_ID = 0x00


# ACTION类型
class ActionType(IntEnum):
    SYSTEM_ACTION = 0x00
    SINGLE_ACTION = auto()
    SCENE_ACTION = auto()


# 动作执行结果
class ActionResult(IntEnum):
    ACTION_FAIL = -1
    ACTION_PASS = 0


# 系统方法ID
class UtilFun(IntEnum):
    SYSTEM_HANDSHAKE_ID = 0x00
    GET_TIME_ID = 0x01
    SHELL_ID = 0X02
    PING_ID = 0X03
    # SOCKET 相关方法
    SOCKET_INIT = 0X04
    SOCKET_EXIT = 0X05
    SOCKET_TX_RX = 0X06
    SOCKET_TEST = 0X07
    WRITE_FILE = 0X08
    READ_FILE = 0X09
    GET_TIME_ID2 = 0X10
    DATA_WAKE = 0x11
    GET_LOGS = 0X12  # 获取模组日志
    CASE_START = 0X13
    WRITE_APPEND_FILE = 0x14


# 运营商号段映射表(2025年最新数据)
OPERATOR_PREFIX_MAP = {
    "CT": {133, 141, 149, 153, 173, 177, 180, 181, 189, 190, 191, 193, 199},
    "CMCC": {134, 135, 136, 137, 138, 139, 144, 147, 148, 150, 151, 152,
             157, 158, 159, 172, 178, 182, 183, 184, 187, 188, 195, 197, 198},
    "CU": {130, 131, 132, 145, 146, 155, 156, 166, 175, 176, 185, 186, 196}
}

# 运营商服务号码映射
SERVICE_NUMBER_MAP = {
    "CT": "10000",
    "CMCC": "10086",
    "CU": "10010"
}

# wifi 信道
B1 = [36, 40, 44, 48]
B2 = [52, 56, 60, 64]
B3 = [100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140]
B3_2 = [100, 104, 108, 112, 116, 132, 136, 140]
B3_3 = [100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144]
B3_4 = [100, 104, 108, 112, 116, 120, 124, 128]
B4 = [149, 153, 157, 161, 165]
B4_2 = [149, 153, 157, 161]
HT1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
HT2 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

LB = B4
BR = B4
PE = B4
CN = B4

RS = B3
TN = B3
# 欧盟
GB = B1 + B4
DE = B1 + B4
NL = B1 + B4
CH = B1 + B4
NO = B1 + B4
FR = B1 + B4
BE = B1 + B4
ES = B1 + B4
SE = B1 + B4
IT = B1 + B4
LU = B1 + B4
DK = B1 + B4
FI = B1 + B4
GE = B1 + B4
MM = B1 + B4

IN = B1 + B4
QA = B1 + B4
IL = B1 + B4
CO = B1 + B4

UZ = B1 + B2
JO = B1 + B2
MA = B1 + B2
JP = B1 + B3_3
BO = B2 + B4

KW = B3 + B4
SA = B3 + B4_2

AZ = B1 + B2 + B3_3
KZ = B1 + B2 + B3
MD = B1 + B2 + B3
PR = B1 + B2 + B3_3
PA = B1 + B2 + B3_3
CL = B1 + B2 + B3_3
EG = B1 + B2 + B4
BH = B1 + B2 + B4
UY = B2 + B3_3 + B4

OM = B1 + B2 + B3 + B4
AE = B1 + B2 + B3 + B4
ZA = B1 + B2 + B3 + B4

AO = B1 + B2 + B3 + B4
PH = B1 + B2 + B3 + B4

LA = B1 + B2 + B3 + B4
UA = B1 + B2 + B3 + B4
KH = B1 + B2 + B3 + B4
GT = B1 + B2 + B3 + B4
TJ = B1 + B2 + B3 + B4

VN = B1 + B2 + B3_3 + B4
US = B1 + B2 + B3_3 + B4
KR = B1 + B2 + B3_3 + B4
HK = B1 + B2 + B3_3 + B4
MO = B1 + B2 + B3_3 + B4
PY = B1 + B2 + B3_3 + B4
CR = B1 + B2 + B3_3 + B4
EC = B1 + B2 + B3_3 + B4
DO = B1 + B2 + B3_3 + B4
TW = B1 + B2 + B3_3 + B4
TH = B1 + B2 + B3_3 + B4
NZ = B1 + B2 + B3_3 + B4
SG = B1 + B2 + B3_3 + B4

MY = B1 + B2 + B3_4 + B4
CA = B1 + B2 + B3_2 + B4
AU = B1 + B2 + B3_2 + B4
MX = B1 + B2 + B3_2 + B4
AR = B1 + B2 + B3_2 + B4
LC = B1 + B2 + B3 + B4_2

# GSM 7-bit 字符集
gsm7_base = {
    0x00: '@', 0x01: '£', 0x02: '$', 0x03: '¥', 0x04: 'è', 0x05: 'é',
    0x06: 'ù', 0x07: 'ì', 0x08: 'ò', 0x09: 'Ç', 0x0A: '\n', 0x0B: 'Ø',
    0x0C: 'ø', 0x0D: '\r', 0x0E: 'Å', 0x0F: 'å', 0x10: 'Δ', 0x11: '_',
    0x12: 'Φ', 0x13: 'Γ', 0x14: 'Λ', 0x15: 'Ω', 0x16: 'Π', 0x17: 'Ψ',
    0x18: 'Σ', 0x19: 'Θ', 0x1A: 'Ξ', 0x1C: 'Æ', 0x1D: 'æ', 0x1E: 'ß',
    0x1F: 'É', 0x20: ' ', 0x21: '!', 0x22: '"', 0x23: '#', 0x24: '¤',
    0x25: '%', 0x26: '&', 0x27: "'", 0x28: '(', 0x29: ')', 0x2A: '*',
    0x2B: '+', 0x2C: ',', 0x2D: '-', 0x2E: '.', 0x2F: '/', 0x30: '0',
    0x31: '1', 0x32: '2', 0x33: '3', 0x34: '4', 0x35: '5', 0x36: '6',
    0x37: '7', 0x38: '8', 0x39: '9', 0x3A: ':', 0x3B: ';', 0x3C: '<',
    0x3D: '=', 0x3E: '>', 0x3F: '?', 0x40: '¡', 0x41: 'A', 0x42: 'B',
    0x43: 'C', 0x44: 'D', 0x45: 'E', 0x46: 'F', 0x47: 'G', 0x48: 'H',
    0x49: 'I', 0x4A: 'J', 0x4B: 'K', 0x4C: 'L', 0x4D: 'M', 0x4E: 'N',
    0x4F: 'O', 0x50: 'P', 0x51: 'Q', 0x52: 'R', 0x53: 'S', 0x54: 'T',
    0x55: 'U', 0x56: 'V', 0x57: 'W', 0x58: 'X', 0x59: 'Y', 0x5A: 'Z',
    0x5B: 'Ä', 0x5C: 'Ö', 0x5D: 'Ñ', 0x5E: 'Ü', 0x5F: '§', 0x60: '¿',
    0x61: 'a', 0x62: 'b', 0x63: 'c', 0x64: 'd', 0x65: 'e', 0x66: 'f',
    0x67: 'g', 0x68: 'h', 0x69: 'i', 0x6A: 'j', 0x6B: 'k', 0x6C: 'l',
    0x6D: 'm', 0x6E: 'n', 0x6F: 'o', 0x70: 'p', 0x71: 'q', 0x72: 'r',
    0x73: 's', 0x74: 't', 0x75: 'u', 0x76: 'v', 0x77: 'w', 0x78: 'x',
    0x79: 'y', 0x7A: 'z', 0x7B: 'ä', 0x7C: 'ö', 0x7D: 'ñ', 0x7E: 'ü',
    0x7F: 'à'
}
# GSM 7-bit 扩展字符集
gsm7_ext = {
    0x0A: '\f', 0x14: '^', 0x28: '{', 0x29: '}', 0x2F: '\\', 0x3C: '[',
    0x3D: '~', 0x3E: ']', 0x40: '|', 0x65: '€'
}

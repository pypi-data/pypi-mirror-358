# -*- coding:utf-8 -*-
from enum import IntEnum, auto


class ServerID(IntEnum):
    NW_SERVER = 0x01
    WIFI_SERVER = auto()
    AUDIO_SERVER = auto()
    I2C_SPI_UART_GPIO_SERVER = auto()
    VOICE_RTP_RTC_SERVER = auto()
    SMS_SERVER = auto()
    GNSS_SERVER = auto()
    DEVICE_UPDATE_SERVER = auto()
    AT_DM_LOG_SERVER = auto()
    SIM_SERVER = auto()
    DATA_DHCP_SERVER = auto()
    WAKELOCK_WAKEUP_TIMER_SERVER = auto()
    TZONE_SERVER = auto()

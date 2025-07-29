# -*- coding:utf-8 -*-
import poseidon_module.core.logger as log
from poseidon_module.core.decorators import LogActionMeta, PoseidonExecute, ActionType, split_timestamp, update_dic
from poseidon_module.action.server_id import ServerID
from poseidon_module.action.scene.scene_id import SceneGnssID


class SceneGnss(metaclass=LogActionMeta):
    def __init__(self):
        self.log = log.get_system_logger()
        self.poseidon_execute = PoseidonExecute(ServerID.GNSS_SERVER, ActionType.SCENE_ACTION, SceneGnssID)

    def action_scene_gps_setup(self, dev_index=1):
        self.poseidon_execute.execute_action(None, 0, dev_index)

    def action_scene_gps_teardown(self, dev_index=1):
        self.poseidon_execute.execute_action(None, 0, dev_index)

    def action_scene_gps_config(self, min_interval=100, bitmask="1111", source_mode=5, dev_index=1):
        """gnss配置
        :param min_interval:最小频率, NMEA report frequency, 1000 means 1Hz, 100 means 10Hz
        :param bitmask: default "1111",打开LOCATION,STATUS, SV, NMEA
        :param source_mode，全系统组合模式 默认为5
        :param dev_index:
        """
        bitmask = int("0b" + bitmask[::-1], 2)
        para = {"min_interval": int(min_interval), "bit_mask": int(bitmask), "source_mode": int(source_mode)}
        self.poseidon_execute.execute_action(para, 0, dev_index)

    def action_scene_gps_start_normal(self, timeout=60, dev_index=1):
        """
        开启gnss定位
        :param timeout: 超时时间
        :param dev_index:
        :return:
        """
        para = {"timeout": int(timeout)}
        self.poseidon_execute.execute_action(para, 0, dev_index, socket_timeout=timeout + 10)

    def action_scene_gps_detail_start(self, mode, timeout=60, dev_index=1):
        """
        开启gnss定位
        :param mode:1:FUSED, 2:SPE, 4:PPE
        :param timeout: 超时时间
        :param dev_index:
        :return:
        """
        para = {"mode": int(mode), "timeout": int(timeout)}
        self.poseidon_execute.execute_action(para, 0, dev_index, socket_timeout=timeout + 10)

    def action_scene_gps_start_cold(self, timeout=60, dev_index=1):
        """ gnss 冷启动"""
        para = {"timeout": int(timeout)}
        self.poseidon_execute.execute_action(para, 0, dev_index, socket_timeout=timeout + 10)

    def action_scene_gps_start_rtk(self, rtk_account, product_info="", timeout=60, dev_index=1):
        """
        开启RTK定位
        :param rtk_account:{"username": "123", "password": "321"}
        :param product_info:{"dev_id": "1","dev_type": "2"}
        :param timeout: 超时时间
        :param dev_index:
        :return:
        """
        default_account = {"username": "ceya033", "password": "ess0mpxu"}
        default_product = {"dev_id": "test dev_id", "dev_type": "test dev_type"}
        para = {"account_info": update_dic(rtk_account, default_account),
                "product_info": update_dic(product_info, default_product), "timeout": timeout}
        self.poseidon_execute.execute_action(para, 0, dev_index, socket_timeout=timeout + 10)

    def action_scene_gps_stop(self, dev_index=1):
        """关闭gnss定位"""
        self.poseidon_execute.execute_action(None, 0, dev_index)

    def action_scene_gps_check_gga(self, start_time, gga_state, timeout=60, dev_index=1):
        """
        检查上报GGA定位类型信息
        :param start_time:
        :param gga_state: e.g.[4,5]
        :param timeout: 超时时间
        :param dev_index:
        :return:
        """
        sec, usec = split_timestamp(start_time)
        para = {"gga_state": gga_state, "time_sec": sec, "time_usec": usec, "timeout": int(timeout)}
        self.poseidon_execute.execute_action(para, 0, dev_index, socket_timeout=timeout + 10)

    def action_scene_gps_check_freq(self, ind_type, min_interval, timeout=10, dev_index=1):
        """
        检查上报频率信息
        :param ind_type
        :param min_interval
        :param timeout: 超时时间
        :param dev_index:
        :return:
        """
        para = {"ind_type": ind_type, "min_interval": min_interval, "timeout": int(timeout)}
        self.poseidon_execute.execute_action(para, 0, dev_index, socket_timeout=timeout + 60)

    def action_scene_gps_check_fun(self, min_interval, timeout=10, dev_index=1):
        para = {"min_interval": int(min_interval), "bit_mask": 0b1111, "source_mode": 6, "timeout": int(timeout)}
        self.poseidon_execute.execute_action(para, 0, dev_index, socket_timeout=timeout + 60)

    def action_scene_gps_check_nmea(self, start_time, dev_index=1):
        """
        检查nmea语句字段
        """
        sec, usec = split_timestamp(start_time)
        para = {"time_sec": sec, "time_usec": usec}
        output = self.poseidon_execute.execute_action(para, 0, dev_index)
        return output.get('nmea_tags'), output.get('gsv_band')

# _*_ coding :UTF-8 _*_
# 开发团队  : gtyc-测试设计部
# 开发人员  : 汪灵
import poseidon_module.core.logger as log
from poseidon_module.core.decorators import LogActionMeta, PoseidonExecute, ActionType, split_timestamp, update_dic
from poseidon_module.action.server_id import ServerID
from poseidon_module.action.single.single_action_id import SingleGnssID


class SingleGnss(metaclass=LogActionMeta):
    def __init__(self):
        self.log = log.get_system_logger()
        self.poseidon_execute = PoseidonExecute(ServerID.GNSS_SERVER, ActionType.SINGLE_ACTION, SingleGnssID)

    def action_fibo_loc_client_init(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_loc_client_deinit(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_loc_addrxindmsghandler(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_loc_set_indications(self, bitmask, expect=0, dev_index=1, batch=False):
        """
        LOC_IND_LOCATION_INFO_ON            (1 << 0)
        LOC_IND_STATUS_INFO_ON              (1 << 1)
        LOC_IND_SV_INFO_ON                  (1 << 2)
        LOC_IND_NMEA_INFO_ON                (1 << 3)
        LOC_IND_CAP_INFO_ON                 (1 << 4)
        LOC_IND_UTC_TIME_REQ_ON             (1 << 5)
        LOC_IND_XTRA_DATA_REQ_ON            (1 << 6)
        LOC_IND_AGPS_DATA_CONN_CMD_REQ_ON   (1 << 7)
        LOC_IND_NI_NFY_USER_RESP_REQ_ON     (1 << 8)
        LOC_IND_LOCATION_DETAIL_INFO_ON     (1 << 9)"""
        bitmask = int("0b" + bitmask[::-1], 2)
        para = {"bit_mask": int(bitmask)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_loc_set_position_mode(self, mode_info, expect=0, dev_index=1, batch=False):
        default_info = {
            "mode": 0,
            "recurrence": 0,
            "min_interval": 100,
            "preferred_accuracy": 0,
            "preferred_time": 0
        }
        para = {"mode_info": update_dic(mode_info, default_info)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_loc_start_navigation(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_loc_stop_navigation(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_loc_get_current_location(self, timeout_sec, expect=0, dev_index=1, batch=False):
        para = {"timeout_sec": int(timeout_sec)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('loc_info') if not batch else None

    def action_fibo_loc_delete_aiding_data(self, del_type, expect=0, dev_index=1, batch=False):
        data = int("0xFFFFFFFF", 16) if del_type == "all" else int(del_type[::-1], 2)
        para = {"flags": int(data)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_loc_get_location_information_source(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('source_mode') if not batch else None

    def action_fibo_loc_set_location_information_source(self, source_mode, expect=0, dev_index=1, batch=False):
        """
        :param source_mode:
                0:GPS_GLO,
                1:GPS_BDS,
                2:GPS_GLO_BDS,
                3:GPS,
                4:BDS,
                5:GLO
                6:GPS_GLO_BDS_GALI
                7:GPS_GALI ,
                8:GPS_GLO_GALI,
                9:GALI
                10:GPS_GLO_BDS_GALI_NAVIC
        :param expect:
        :param dev_index:
        :param batch:
        :return:
        """
        para = {"source_mode": int(source_mode)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_loc_set_rtk_service_status(self, status, expect=0, dev_index=1, batch=False):
        para = {"status": int(status)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_loc_get_rtk_service_status(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('status') if not batch else None

    def action_fibo_loc_get_rtk_service_account_info(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('account_info') if not batch else None

    def action_fibo_loc_set_rtk_service_account_info(self, account_info, expect=0, dev_index=1, batch=False):
        default_info = {
            "username": "ceya033",
            "password": "ess0mpxu"
        }
        para = {"account_info": update_dic(account_info, default_info)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_loc_get_rtk_product_id_conf_info(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('product_info') if not batch else None

    def action_fibo_loc_set_rtk_product_id_conf_info(self, product_info, expect=0, dev_index=1, batch=False):
        default_info = {
            "dev_id": "test dev_id",
            "dev_type": "test dev_type"
        }
        para = {"product_info": update_dic(product_info, default_info)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_loc_get_rtk_log_conf_info(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('rtk_log') if not batch else None

    def action_fibo_loc_set_rtk_log_conf_info(self, rtk_log, expect=0, dev_index=1, batch=False):
        default_info = {
            "log_level": 1,
            "log_mask": 2,
            "callback_log_mask": 3,
            "log_path": "/oemdata"
        }
        para = {"rtk_log": update_dic(rtk_log, default_info)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_loc_set_dr_service_status(self, status, expect=0, dev_index=1, batch=False):
        para = {"status": int(status)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_loc_get_dr_service_status(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('status') if not batch else None

    def action_fibo_loc_import_realtime_speed_info(self, value, time_stamp, expect=0, dev_index=1, batch=False):
        para = {"value": int(value), "timestamp": int(time_stamp)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_loc_import_realtime_gear_info(self, value, time_stamp, expect=0, dev_index=1, batch=False):
        para = {"value": int(value), "timestamp": int(time_stamp)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_loc_start_detail_navigation(self, mode, expect=0, dev_index=1, batch=False):
        para = {"mode": int(mode)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_loc_set_nmea_ind_mask(self, value, expect=0, dev_index=1, batch=False):
        para = {"mask": int(value)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_loc_set_frequency_band(self, frequency, expect=0, dev_index=1, batch=False):
        """frequency 0":L1_L5 ; 1:L1"""
        para = {"frequency": int(frequency)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_loc_set_epo_status(self, status, expect=0, dev_index=1, batch=False):
        para = {"status": int(status)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_loc_set_sbas_status(self, status, expect=0, dev_index=1, batch=False):
        para = {"status": int(status)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_loc_check_rtk_pem_exist(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('status') if not batch else None

    def action_fibo_loc_check_rtk_license_exist(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('status') if not batch else None

    def action_fibo_loc_set_nmea_fuse_status(self, status, expect=0, dev_index=1, batch=False):
        para = {"status": int(status)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_loc_get_nmea_fuse_status(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('status') if not batch else None

    def action_fibo_loc_ind_data(self, ind_id, start_time, timeout=60, expect=0, dev_index=1, batch=False):
        """
        ind_id:1:status  2:location  3:sv   4:nmea, 5:gsv
        """
        sec, usec = split_timestamp(start_time)
        para = {"ind_type": int(ind_id), "time_sec": sec, "time_usec": usec, "timeout": int(timeout)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch, socket_timeout=timeout + 10)
        return output.get('ind_msg') if not batch else None

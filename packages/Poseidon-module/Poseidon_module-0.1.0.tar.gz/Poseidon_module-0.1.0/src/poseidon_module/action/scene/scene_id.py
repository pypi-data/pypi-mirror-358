from enum import IntEnum, auto


class SceneWifiID(IntEnum):
    pass


class SceneDataID(IntEnum):
    action_scene_data_setup = 0x01
    action_scene_data_teardown = auto()
    action_scene_async_data_call_ping = auto()
    action_scene_data_call_ping = auto()
    action_scene_async_data_call = auto()
    action_scene_data_call = auto()
    action_scene_data_async_stop_call = auto()
    action_scene_data_stop_call = auto()
    action_scene_data_check_fun = auto()
    action_scene_data_multi_data_call = auto()
    action_scene_data_multi_data_call_stop = auto()
    action_scene_add_route_and_dns = auto()


class SceneNWID(IntEnum):
    action_scene_nw_setup = 0x01
    action_scene_nw_set_pref_mode = auto()
    action_scene_nw_check_target_rat = auto()
    action_scene_nw_teardown = auto()


class SceneVoiceID(IntEnum):
    action_scene_voice_setup = 0x01
    action_scene_voice_teardown = auto()
    action_scene_voice_start_call = auto()
    action_scene_voice_incoming_check = auto()
    action_scene_voice_answer_call = auto()
    action_scene_voice_end_call = auto()
    action_scene_voice_check_func = auto()
    action_scene_voice_end_all_call = auto()
    action_scene_voice_state_check = auto()


class SceneDeviceUpdateID(IntEnum):
    action_scene_ota_update = 0x01
    action_scene_ota_update_check = auto()

    action_scene_device_ab_sync = auto()
    action_scene_device_get_sync_status = auto()
    action_scene_device_get_current_partition = auto()
    action_scene_device_set_nextboot_partition = auto()
    action_scene_device_damage_partition = auto()
    action_scene_device_get_sync_cfg = auto()
    action_scene_device_set_sync_cfg = auto()


class SceneSmsID(IntEnum):
    action_scene_sms_setup = 0x01
    action_scene_sms_teardown = auto()
    action_scene_sms_send_msg = auto()
    action_scene_sms_send_msg_async = auto()
    action_scene_sms_send_pdu = auto()
    action_scene_sms_send_pdu_async = auto()
    action_scene_sms_receive_check = auto()
    action_scene_sms_check_fun = auto()


class SceneGnssID(IntEnum):
    action_scene_gps_setup = 0x01
    action_scene_gps_teardown = auto()
    action_scene_gps_config = auto()
    action_scene_gps_start_normal = auto()
    action_scene_gps_detail_start = auto()
    action_scene_gps_start_cold = auto()
    action_scene_gps_start_rtk = auto()
    action_scene_gps_stop = auto()
    action_scene_gps_check_gga = auto()
    action_scene_gps_check_freq = auto()
    action_scene_gps_check_nmea = auto()
    action_scene_gps_check_fun = auto()


class SceneSimID(IntEnum):
    action_scene_sim_setup = 0x01
    action_scene_sim_teardown = auto()
    action_scene_sim_switch_slot = auto()
    action_scene_sim_check_info = auto()


class SceneDmID(IntEnum):
    action_scene_dm_setup = 0x01
    action_scene_dm_teardown = auto()
    action_scene_flight_mode_on = auto()
    action_scene_flight_mode_off = auto()
    action_scene_flight_mode_on_off = auto()
    action_scene_get_flight_mode = auto()
    action_scene_dm_check_info = auto()
    action_scene_ims_enable = auto()
    action_scene_ims_disable = auto()
    action_scene_vonr_enable = auto()

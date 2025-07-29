# -*- coding:utf-8 -*-

from enum import IntEnum, auto


class SingleNWID(IntEnum):
    action_fibo_nw_client_init = 0x01
    action_fibo_nw_client_deinit = auto()
    action_fibo_nw_set_config = auto()
    action_fibo_nw_get_config = auto()
    action_fibo_nw_get_nitz_time_info = auto()
    action_fibo_nw_event_register = auto()
    action_fibo_nw_perform_scan = auto()
    action_fibo_nw_get_reg_status = auto()
    action_fibo_nw_set_selection = auto()
    action_fibo_nw_get_signal_strength = auto()
    action_fibo_nw_add_rx_msg_handler = auto()
    action_fibo_nw_set_centric = auto()
    action_fibo_nw_get_centric = auto()
    action_fibo_nw_get_cell_access_state = auto()
    action_fibo_nw_set_scan_time_interval = auto()  #
    action_fibo_nw_get_scan_time_interval = auto()  #
    action_fibo_nw_set_low_power_mode = auto()
    action_fibo_nw_get_csq = auto()
    action_fibo_nw_set_forbidden_networks = auto()
    action_fibo_nw_get_forbidden_networks = auto()
    action_fibo_nw_get_gtccinfo = auto()
    action_fibo_nw_get_operator_name = auto()
    action_fibo_nw_get_current_network_status = auto()
    action_fibo_nw_get_current_network_system = auto()
    action_fibo_nw_set_lte_band = auto()
    action_fibo_nw_get_lte_band = auto()
    action_fibo_nw_set_nr5g_band = auto()
    action_fibo_nw_get_nr5g_band = auto()
    action_fibo_nw_get_msg_ind = auto()
    action_fibo_nw_get_home_plmn = auto()
    action_fibo_nw_get_network_err_number = auto()
    action_fibo_nw_set_oos_config = auto()
    action_fibo_nw_set_oos_enable = auto()
    action_fibo_nw_get_gtccinfo_ext = auto()
    action_fibo_nw_bind_subscription = auto()
    action_fibo_nw_get_signal_strength_ext = auto()


class SingleDataDhcpID(IntEnum):
    action_fibo_data_client_init = 0x01
    action_fibo_data_client_deinit = auto()
    action_fibo_data_apn_set = auto()
    action_fibo_data_apn_get = auto()
    action_fibo_data_apn_del = auto()
    action_fibo_data_call_start = auto()
    action_fibo_data_call_stop = auto()
    action_fibo_data_call_async_start = auto()
    action_fibo_data_call_async_stop = auto()
    action_fibo_data_get_call_info = auto()
    action_fibo_data_get_pkt_statistic = auto()
    action_fibo_data_get_call_status = auto()
    action_fibo_data_apn_get_lists = auto()
    action_fibo_data_get_data_channel_rate = auto()
    action_fibo_data_get_data_call_bearer_tech = auto()
    action_fibo_data_get_msg_ind = auto()
    action_fibo_data_reset_pkt_statistic = auto()
    action_fibo_data_nslookup = auto()
    action_fibo_data_set_reconnect_param = auto()
    action_fibo_data_get_reconnect_param = auto()
    action_fibo_data_get_lan_pkt_statistic = auto()
    action_fibo_data_reset_lan_pkt_statistic = auto()
    action_fibo_data_bind_subscription = auto()


class SingleWakeTimerID(IntEnum):
    pass


class SingleGnssID(IntEnum):
    action_fibo_loc_client_init = 0x01
    action_fibo_loc_client_deinit = auto()
    action_fibo_loc_addrxindmsghandler = auto()
    action_fibo_loc_set_indications = auto()
    action_fibo_loc_set_position_mode = auto()
    action_fibo_loc_start_navigation = auto()
    action_fibo_loc_stop_navigation = auto()
    action_fibo_loc_get_current_location = auto()
    action_fibo_loc_delete_aiding_data = auto()
    action_fibo_loc_injecttime = auto()
    action_fibo_loc_injectlocation = auto()
    action_fibo_loc_get_location_information_source = auto()
    action_fibo_loc_set_location_information_source = auto()
    action_fibo_loc_start_detail_navigation = auto()
    action_fibo_loc_set_nmea_ind_mask = auto()
    action_fibo_loc_set_epo_status = auto()
    action_fibo_loc_set_sbas_status = auto()
    action_fibo_loc_set_nmea_output_status = auto()
    action_fibo_loc_set_frequency_band = auto()
    action_fibo_loc_set_xtra_status = auto()
    action_fibo_loc_get_nmea_fuse_status = auto()
    action_fibo_loc_set_nmea_fuse_status = auto()
    action_fibo_loc_ind_data = auto()
    action_fibo_loc_set_rtk_service_status = auto()
    action_fibo_loc_get_rtk_service_status = auto()
    action_fibo_loc_get_rtk_service_account_info = auto()
    action_fibo_loc_set_rtk_service_account_info = auto()
    action_fibo_loc_get_rtk_product_id_conf_info = auto()
    action_fibo_loc_set_rtk_product_id_conf_info = auto()
    action_fibo_loc_get_rtk_log_conf_info = auto()
    action_fibo_loc_set_rtk_log_conf_info = auto()
    action_fibo_loc_check_rtk_pem_exist = auto()
    action_fibo_loc_check_rtk_license_exist = auto()
    action_fibo_loc_set_qdr_service_status = auto()
    action_fibo_loc_get_qdr_service_status = auto()
    action_fibo_loc_inject_realtime_speed_info = auto()
    action_fibo_loc_inject_realtime_gear_info = auto()


class SingleSimID(IntEnum):
    action_fibo_sim_client_init = 0x01
    action_fibo_sim_client_deinit = auto()
    action_fibo_sim_get_imsi = auto()
    action_fibo_sim_get_iccid = auto()
    action_fibo_sim_get_phonenumber = auto()
    action_fibo_sim_verify_pin = auto()
    action_fibo_sim_change_pin = auto()
    action_fibo_sim_unblock_pin = auto()
    action_fibo_sim_enable_pin = auto()
    action_fibo_sim_disable_pin = auto()
    action_fibo_sim_get_card_status = auto()
    action_fibo_sim_register_event = auto()
    action_fibo_sim_add_rx_msg_handler = auto()
    action_fibo_sim_reset = auto()
    action_fibo_sim_open_channel = auto()
    action_fibo_sim_close_channel = auto()
    action_fibo_sim_send_apdu = auto()
    action_fibo_sim_get_status_ind = auto()
    action_fibo_sim_get_slot = auto()
    action_fibo_sim_switch_slot = auto()
    action_fibo_sim_only_switch_main_cards = auto()


class SingleSMSID(IntEnum):
    action_fibo_sms_client_init = 0x01
    action_fibo_sms_client_deinit = auto()
    action_fibo_sms_send_message = auto()
    action_fibo_sms_send_message_async = auto()
    action_fibo_sms_send_smspdu = auto()
    action_fibo_sms_send_smspdu_async = auto()
    action_fibo_sms_read_message = auto()
    action_fibo_sms_add_rx_msg_handler = auto()
    action_fibo_sms_delete_from_storage = auto()
    action_fibo_sms_get_sms_center_address = auto()
    action_fibo_sms_set_sms_center_address = auto()
    action_fibo_sms_get_msg_list = auto()
    action_fibo_sms_get_max_store_size = auto()
    action_fibo_sms_set_ims_status = auto()
    action_fibo_sms_bind_subscription = auto()
    action_fibo_sms_set_whitelist_status = auto()
    action_fibo_sms_get_whitelist_status = auto()
    action_fibo_sms_set_whitelist_number = auto()
    action_fibo_sms_get_whitelist_number = auto()
    action_fibo_sms_get_drop_message = auto()
    action_fibo_sms_receive_ind = auto()


class SingleVoiceRtpID(IntEnum):
    action_fibo_voice_client_init = 0x01
    action_fibo_voice_client_deinit = auto()
    action_fibo_voice_start_call = auto()
    action_fibo_voice_answer_call = auto()
    action_fibo_voice_end_call = auto()
    action_fibo_voice_hold_call = auto()
    action_fibo_voice_unhold_call = auto()
    action_fibo_voice_end_all_call = auto()
    action_fibo_voice_enable_auto_answer = auto()
    action_fibo_voice_disable_auto_answer = auto()
    action_fibo_voice_get_call_status = auto()
    action_fibo_voice_call_add_state_handle = auto()
    action_fibo_voice_get_msg_ind = auto()
    action_fibo_voice_ecall_start_call = auto()
    action_fibo_voice_ecall_end_call = auto()
    action_fibo_voice_ecall_update_msd = auto()
    action_fibo_voice_conference = auto()
    action_fibo_voice_end_conference = auto()
    action_fibo_voice_mute = auto()
    action_fibo_voice_unmute = auto()
    action_fibo_voice_dtmf = auto()
    action_fibo_voice_register_bitmask = auto()
    action_fibo_voice_call_remove_state_handler = auto()
    action_fibo_voice_ecall_start_call_ext = auto()
    action_fibo_voice_ecall_update_msd_ext = auto()
    action_fibo_voice_ecall_deregistration = auto()
    action_fibo_voice_ecall_set_config = auto()
    action_fibo_voice_ecall_get_config = auto()
    action_fibo_voice_set_volte = auto()
    action_fibo_voice_bind_subscription = auto()

    action_fibo_rtp_enable = auto()
    action_fibo_rtp_disable = auto()
    action_fibo_rtp_config = auto()
    action_fibo_rtp_get_config = auto()
    action_fibo_rtp_config_v2 = auto()
    action_fibo_rtp_get_config_v2 = auto()


class SingleDeviceUpdateID(IntEnum):
    action_fibo_device_setusb_composition = 0x01
    action_fibo_device_setusb_composition_ex = auto()

    action_fibo_device_watchdog_open = auto()
    action_fibo_device_watchdog_feed = auto()
    action_fibo_device_watchdog_close = auto()

    action_fibo_device_gptp_server_ctrl = auto()
    action_fibo_device_gptp_set = auto()
    action_fibo_device_gptp_get = auto()
    action_fibo_device_chrony_server_ctrl = auto()
    action_fibo_device_get_ntp_time = auto()
    action_fibo_device_get_adc = auto()

    action_fibo_device_get_pa_temperature = auto()
    action_fibo_device_get_modem_temperature = auto()
    action_fibo_device_get_temperature = auto()
    action_fibo_device_register_temperature_report = auto()
    action_fibo_device_register_temperature_threshold_report = auto()
    action_fibo_device_register_temperature_level_report = auto()
    action_fibo_get_temperature_protection_cfg = auto()
    action_fibo_set_temperature_protection_cfg = auto()

    action_fibo_device_start_update_firmware = auto()
    action_fibo_device_start_update_firmware_ext = auto()
    action_fibo_device_get_update_status = auto()
    action_fibo_device_get_sync_status = auto()
    action_fibo_device_get_sync_cfg = auto()
    action_fibo_device_set_sync_cfg = auto()
    action_fibo_device_start_sync = auto()
    action_fibo_device_get_current_partition = auto()
    action_fibo_device_set_nextboot_partition = auto()
    action_fibo_device_get_update_result = auto()
    action_fibo_device_get_update_progress = auto()

    action_fibo_device_write_phyreg = auto()
    action_fibo_device_read_phyreg = auto()
    action_fibo_device_register_imu_report = auto()
    action_fibo_device_register_imu_report_ext = auto()
    action_fibo_device_get_ethernet_state = auto()
    action_fibo_device_set_network_speed_limit = auto()
    action_fibo_device_get_network_speed_limit = auto()
    action_fibo_device_acl_mac_filter_enable = auto()
    action_fibo_device_acl_get_mac_filter_state = auto()
    action_fibo_device_acl_set_mac_filter = auto()
    action_fibo_device_acl_get_mac_filter_list = auto()
    action_fibo_device_acl_del_mac_filter = auto()
    action_fibo_device_get_mac = auto()
    action_fibo_device_set_mac = auto()
    action_fibo_device_reset_phy = auto()
    action_fibo_device_reset_mac = auto()
    action_fibo_device_set_linkdown_thershold = auto()
    action_fibo_device_get_linkdown_thershold = auto()
    action_fibo_device_get_linkdown_count = auto()
    action_fibo_device_set_forward_ethernet_type = auto()
    action_fibo_device_get_forward_ethernet_type = auto()
    action_fibo_device_create_vlan_config = auto()
    action_fibo_device_get_vlan_config = auto()
    action_fibo_device_del_vlan_config = auto()
    action_fibo_device_get_eth_fcs_error_count = auto()

    action_fibo_device_register_partition_ro_event = auto()
    action_fibo_device_unregister_partition_ro_event = auto()
    action_fibo_device_get_back_part_status = auto()
    action_fibo_device_get_secureboot_state = auto()

    action_fibo_dev_queue_init = auto()
    action_fibo_dev_queue_deinit = auto()
    action_fibo_dev_get_temp_ind = auto()


class SingleAtDmLogID(IntEnum):
    action_fibo_at_register_urc_callback = 0x01
    action_fibo_at_unregister_urc_callback = auto()
    action_fibo_send_at_cmd = auto()

    action_fibo_dm_client_init = auto()
    action_fibo_dm_client_deinit = auto()
    action_fibo_dm_get_manufacturer = auto()
    action_fibo_dm_get_imei = auto()
    action_fibo_dm_get_sn = auto()
    action_fibo_dm_get_sdk_version = auto()
    action_fibo_dm_get_model_id = auto()
    action_fibo_dm_get_ims = auto()
    action_fibo_dm_add_rx_msg_handler = auto()
    action_fibo_dm_get_msg_ind = auto()
    action_fibo_dm_get_operating_mode = auto()
    action_fibo_dm_set_operating_mode = auto()
    action_fibo_dm_get_sw_version = auto()
    action_fibo_dm_get_ntp_curr_clock_src = auto()
    action_fibo_dm_node_monitor_ind_register = auto()
    action_fibo_dm_get_partition_erase_status = auto()
    action_fibo_dm_get_all_partition_erase_status = auto()
    action_fibo_dm_clean_partition_erase_status = auto()
    action_fibo_dm_event_register = auto()
    action_fibo_dm_get_hw_version = auto()
    action_fibo_dm_get_revision_id = auto()
    action_fibo_dm_set_ims = auto()
    action_fibo_dm_get_ap_version = auto()
    action_fibo_dm_bind_subscription = auto()
    action_fibo_dm_get_imei_ext = auto()
    action_fibo_dm_modem_status_ind_register = auto()
    action_fibo_dm_get_modem_status = auto()

    action_fibo_log_init = auto()
    action_fibo_log_deinit = auto()
    action_fibo_log_set_level = auto()
    action_fibo_log_config_info_modify = auto()
    action_fibo_log_config_info_get = auto()
    action_fibo_write_Log = auto()


class SingleWifiID(IntEnum):
    pass


class SingleTZID(IntEnum):
    pass


class SingleI2cSpiUartGpioID(IntEnum):
    pass


class SingleAudioID(IntEnum):
    pass

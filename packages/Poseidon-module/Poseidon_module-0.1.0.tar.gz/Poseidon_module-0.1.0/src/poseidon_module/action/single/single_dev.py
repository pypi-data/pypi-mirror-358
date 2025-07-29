# -*- coding:utf-8 -*-
import poseidon_module.core.logger as log
from poseidon_module.core.decorators import PoseidonExecute, ActionType, LogActionMeta, split_timestamp
from poseidon_module.action.server_id import ServerID
from poseidon_module.action.single.single_action_id import SingleDeviceUpdateID


class SingleDev(metaclass=LogActionMeta):
    def __init__(self):
        self.log = log.get_system_logger()
        self.poseidon_execute = PoseidonExecute(ServerID.DEVICE_UPDATE_SERVER, ActionType.SINGLE_ACTION,
                                                SingleDeviceUpdateID)

    def action_fibo_device_setusb_composition(self, usb_type, expect=0, dev_index=1, batch=False):
        para = {"type": int(usb_type)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_device_setusb_composition_ex(self, usb_type, adb_enable, expect=0, dev_index=1, batch=False):
        para = {"type": int(usb_type), "adb_enable": int(adb_enable)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_device_watchdog_open(self, timeout, expect=0, dev_index=1, batch=False):
        para = {"timeout": int(timeout)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_device_watchdog_feed(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_device_watchdog_close(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_device_gptp_server_ctrl(self, action, expect=0, dev_index=1, batch=False):
        para = {"action": int(action)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_device_gptp_set(self, if_name, mode, action, expect=0, dev_index=1, batch=False):
        para = {"ifname": if_name, "mode": int(mode), "action": int(action)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_device_gptp_get(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('conf') if not batch else None

    def action_fibo_device_chrony_server_ctrl(self, action, expect=0, dev_index=1, batch=False):
        para = {"action": int(action)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_device_get_ntp_time(self, ntp_ip, expect=0, dev_index=1, batch=False):
        para = {"ntp_ip": ntp_ip}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('timestamp') if not batch else None

    def action_fibo_device_get_adc(self, channel, expect=0, dev_index=1, batch=False):
        para = {"channel": channel}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('data') if not batch else None

    def action_fibo_device_get_pa_temperature(self, pa_type, expect=0, dev_index=1, batch=False):
        para = {"pa_type": pa_type}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('pa_temp') if not batch else None

    def action_fibo_device_get_modem_temperature(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('modem_temp') if not batch else None

    def action_fibo_device_get_temperature(self, temp_type, expect=0, dev_index=1, batch=False):
        para = {"type": int(temp_type)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('temp') if not batch else None

    def action_fibo_device_register_temperature_report(self, mask, interval_time, expect=0, dev_index=1, batch=False):
        para = {"mask": int("0b" + mask, 2), "interval_time": int(interval_time)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_device_register_temperature_threshold_report(self, mask, expect=0, dev_index=1, batch=False):
        para = {"mask": int("0b" + mask, 2)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_device_register_temperature_level_report(self, mask, expect=0, dev_index=1, batch=False):
        para = {"mask": int("0b" + mask, 2)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_get_temperature_protection_cfg(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('protect_info') if not batch else None

    def action_fibo_set_temperature_protection_cfg(self, tp_type, valid, tp_num, tp_info, expect=0, dev_index=1,
                                                   batch=False):
        para = {"type": int(tp_type), "valid": int(valid), "tp_num": int(tp_num), "tp_info": tp_info}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_device_start_update_firmware(self, path, expect=0, dev_index=1, batch=False):
        para = {"path": path}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('error_code') if not batch else None

    def action_fibo_device_start_update_firmware_ext(self, package_path, log_path, tmp_image_path, timeout, expect=0,
                                                     dev_index=1, batch=False):
        para = {"package_path": package_path, "log_path": log_path, "tmp_image_path": tmp_image_path,
                "timeout": int(timeout)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('error_code') if not batch else None

    def action_fibo_device_get_update_status(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('status') if not batch else None

    def action_fibo_device_get_sync_status(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('status') if not batch else None

    def action_fibo_device_get_sync_cfg(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('sync_cfg') if not batch else None

    def action_fibo_device_set_sync_cfg(self, sync_cfg, expect=0, dev_index=1, batch=False):
        para = {"sync_cfg": int(sync_cfg)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_device_start_sync(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_device_get_current_partition(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('cur_partition') if not batch else None

    def action_fibo_device_set_nextboot_partition(self, next_partition, expect=0, dev_index=1, batch=False):
        para = {"next_partition": int(next_partition)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_device_get_update_result(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('update_result') if not batch else None

    def action_fibo_device_get_update_progress(self, progress_len, expect=0, dev_index=1, batch=False):
        para = {"progress_len": int(progress_len)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return (output.get('percent'), output.get('progress')) if not batch else None

    def action_fibo_device_write_phyreg(self, eth_name, phy_id, reg_addr, val_in, expect=0, dev_index=1, batch=False):
        para = {"eth_name": eth_name, "phy_id": int(phy_id), "reg_addr": int(reg_addr), "val_in": int(val_in)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_device_read_phyreg(self, eth_name, phy_id, reg_addr, expect=0, dev_index=1, batch=False):
        para = {"eth_name": eth_name, "phy_id": int(phy_id), "reg_addr": int(reg_addr)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('val_out') if not batch else None

    def action_fibo_device_register_imu_report(self, imu_switch, expect=0, dev_index=1, batch=False):
        para = {"imu_switch": int(imu_switch)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_device_register_imu_report_ext(self, imu_switch, accel_hz, gyro_hz, accel_fsr, gyro_fsr, convert,
                                                   expect=0, dev_index=1, batch=False):
        para = {"imu_switch": int(imu_switch), "accel_hz": int(accel_hz), "gyro_hz": int(gyro_hz),
                "accel_fsr": int(accel_fsr), "gyro_fsr": int(gyro_fsr), "convert": int(convert)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_device_get_ethernet_state(self, eth_name, expect=0, dev_index=1, batch=False):
        para = {"eth_name": eth_name}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('link_state') if not batch else None

    def action_fibo_device_set_network_speed_limit(self, dev_name, speed, expect=0, dev_index=1, batch=False):
        para = {"dev_name": dev_name, "speed": int(speed)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_device_get_network_speed_limit(self, dev_name, expect=0, dev_index=1, batch=False):
        para = {"dev_name": dev_name}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('speed') if not batch else None

    def action_fibo_device_acl_mac_filter_enable(self, enable, expect=0, dev_index=1, batch=False):
        para = {"enable": int(enable)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_device_acl_get_mac_filter_state(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('state') if not batch else None

    def action_fibo_device_acl_set_mac_filter(self, mac, drop, expect=0, dev_index=1, batch=False):
        para = {"mac": mac, "drop": int(drop)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_device_acl_get_mac_filter_list(self, numbers, drop, expect=0, dev_index=1, batch=False):
        para = {"numbers": numbers, "drop": int(drop)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('mac_list') if not batch else None

    def action_fibo_device_acl_del_mac_filter(self, mac, drop, expect=0, dev_index=1, batch=False):
        para = {"mac": mac, "drop": int(drop)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_device_get_mac(self, eth_name, expect=0, dev_index=1, batch=False):
        para = {"eth_name": eth_name}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('mac') if not batch else None

    def action_fibo_device_set_mac(self, eth_name, mac, expect=0, dev_index=1, batch=False):
        para = {"eth_name": eth_name, "mac": mac}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_device_reset_phy(self, phy_type, reset_type, expect=0, dev_index=1, batch=False):
        para = {"phy_type": int(phy_type), "reset_type": int(reset_type)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_device_reset_mac(self, eth_type, expect=0, dev_index=1, batch=False):
        para = {"eth_type": int(eth_type)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_device_set_linkdown_thershold(self, eth_type, threshold, expect=0, dev_index=1, batch=False):
        para = {"eth_type": int(eth_type), "threshold": int(threshold)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_device_get_linkdown_thershold(self, eth_type, expect=0, dev_index=1, batch=False):
        para = {"eth_type": int(eth_type)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('threshold') if not batch else None

    def action_fibo_device_get_linkdown_count(self, eth_type, expect=0, dev_index=1, batch=False):
        para = {"eth_type": int(eth_type)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('count') if not batch else None

    def action_fibo_device_set_forward_ethernet_type(self, ethernet_type, expect=0, dev_index=1, batch=False):
        para = {"ethernet_type": int(ethernet_type)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_device_get_forward_ethernet_type(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('ethernet_type') if not batch else None

    def action_fibo_device_create_vlan_config(self, vlan_id, netmask_length, vlan_qos, is_ipa, local_iface, ip_addr,
                                              expect=0, dev_index=1, batch=False):
        para = {"vlan_id": int(vlan_id), "netmask_length": int(netmask_length), "vlan_qos": int(vlan_qos),
                "is_ipa": int(is_ipa), "local_iface": local_iface, "ip_addr": ip_addr}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_device_get_vlan_config(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('vlan_config_info') if not batch else None

    def action_fibo_device_del_vlan_config(self, vlan_id, netmask_length, vlan_qos, is_ipa, local_iface, ip_addr,
                                           expect=0, dev_index=1, batch=False):
        para = {"vlan_id": int(vlan_id), "netmask_length": int(netmask_length), "vlan_qos": int(vlan_qos),
                "is_ipa": int(is_ipa), "local_iface": local_iface, "ip_addr": ip_addr}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_device_get_eth_fcs_error_count(self, eth_name, expect=0, dev_index=1, batch=False):
        para = {"eth_name": eth_name}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('count') if not batch else None

    def action_fibo_device_register_partition_ro_event(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_device_unregister_partition_ro_event(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_device_get_back_part_status(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('status') if not batch else None

    def action_fibo_device_get_secureboot_state(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('state') if not batch else None

    def action_fibo_dev_queue_init(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_dev_queue_deinit(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_dev_get_temp_ind(self, ind_type, start_time, timeout, expect=0, dev_index=1, batch=False):
        sec, usec = split_timestamp(start_time)
        para = {"ind_type": int(ind_type), "time_sec": sec, "time_usec": usec, "timeout": int(timeout)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('ind_msg') if not batch else None

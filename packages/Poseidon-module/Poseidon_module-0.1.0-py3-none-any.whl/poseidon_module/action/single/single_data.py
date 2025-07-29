# -*- coding:utf-8 -*-
import poseidon_module.core.logger as log
from poseidon_module.core.decorators import LogActionMeta, PoseidonExecute, ActionType, split_timestamp, update_dic
from poseidon_module.action.server_id import ServerID
from poseidon_module.action.single.single_action_id import SingleDataDhcpID

default_apn = {
    "profile_id": 1,
    "profile_valid": 1,
    "auth_pref": 0,
    "auth_pref_valid": 1,
    "tech_pref": 3,
    "tech_pref_valid": 1,
    "password": "111111",
    "password_valid": 1,
    "user_name": "gtyc",
    "user_name_valid": 1,
    "apn_name": "TestApn",
    "apn_name_valid": 1,
    "ip_family": 10,
    "ip_family_valid": 1,
    "reconnect": 0
}


class SingleData(metaclass=LogActionMeta):
    def __init__(self):
        self.log = log.get_system_logger()
        self.poseidon_execute = PoseidonExecute(ServerID.DATA_DHCP_SERVER, ActionType.SINGLE_ACTION, SingleDataDhcpID)

    def action_fibo_data_client_init(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_data_client_deinit(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_data_apn_set(self, apn_info, expect=0, dev_index=1, batch=False):
        default_info = default_apn.copy()
        para = {"apn_info": update_dic(apn_info, default_info)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_data_apn_get(self, profile_id, expect=0, dev_index=1, batch=False):
        para = {"profile_id": int(profile_id)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('apn_info') if not batch else None

    def action_fibo_data_apn_del(self, profile_id, expect=0, dev_index=1, batch=False):
        para = {"profile_id": int(profile_id)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_data_call_start(self, profile_id, expect=0, dev_index=1, batch=False):
        para = {"profile_id": int(profile_id)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('call_ret') if not batch else None

    def action_fibo_data_call_stop(self, call_id, expect=0, dev_index=1, batch=False):
        para = {"call_id": int(call_id)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_data_call_async_start(self, profile_id, expect=0, dev_index=1, batch=False):
        para = {"profile_id": int(profile_id)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('call_ret') if not batch else None

    def action_fibo_data_call_async_stop(self, call_id, expect=0, dev_index=1, batch=False):
        para = {"call_id": int(call_id)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_data_get_call_info(self, call_id, expect=0, dev_index=1, batch=False):
        para = {"call_id": int(call_id)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('call_info') if not batch else None

    def action_fibo_data_get_pkt_statistic(self, call_id, expect=0, dev_index=1, batch=False):
        para = {"call_id": int(call_id)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('info') if not batch else None

    def action_fibo_data_get_call_status(self, call_id, expect=0, dev_index=1, batch=False):
        para = {"call_id": int(call_id)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('call_status') if not batch else None

    def action_fibo_data_apn_get_lists(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return (output.get('cnt'), output.get('info')) if not batch else None

    def action_fibo_data_get_data_channel_rate(self, call_id, expect=0, dev_index=1, batch=False):
        para = {"call_id": int(call_id)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('info') if not batch else None

    def action_fibo_data_get_data_call_bearer_tech(self, call_id, expect=0, dev_index=1, batch=False):
        para = {"call_id": int(call_id)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('be_tech') if not batch else None

    def action_fibo_data_reset_pkt_statistic(self, call_id, expect=0, dev_index=1, batch=False):
        para = {"call_id": int(call_id)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_data_get_msg_ind(self, ind_type, start_time, timeout, expect=0, dev_index=1, batch=False):
        """
        获取指定上报类型的上报
        E_FIBO_DATA_NET_UP_EVENT   -- 1
        E_FIBO_DATA_NET_DOWN_EVENT -- 2
        """
        sec, usec = split_timestamp(start_time)
        para = {"ind_type": int(ind_type), "time_sec": sec, "time_usec": usec, "timeout": int(timeout)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('ind_msg') if not batch else None

    def action_fibo_data_nslookup(self, host, dns_server_ip, ip_type, expect=0, dev_index=1, batch=False):
        para = {"host": host, "dns_server_ip": dns_server_ip, "ip_type": ip_type}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('resolved_addr') if not batch else None

    def action_fibo_data_set_reconnect_param(self, profile_id, reconnect_param, expect=0, dev_index=1, batch=False):
        default_param = {"reconnect_count": 1, "reconnect_interval": 10}
        para = {"profile_id": int(profile_id), "reconnect_param": update_dic(reconnect_param, default_param)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_data_get_reconnect_param(self, profile_id, expect=0, dev_index=1, batch=False):
        para = {"profile_id": int(profile_id)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('reconnect_param') if not batch else None

    def action_fibo_data_get_lan_pkt_statistic(self, iface_name, expect=0, dev_index=1, batch=False):
        para = {"ifname": iface_name}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('lan_pkt_info') if not batch else None

    def action_fibo_data_reset_lan_pkt_statistic(self, iface_name, expect=0, dev_index=1, batch=False):
        para = {"ifname": iface_name}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_data_bind_subscription(self, slot_id, expect=0, dev_index=1, batch=False):
        para = {"slot_id": int(slot_id)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

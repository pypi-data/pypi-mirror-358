# -*- coding:utf-8 -*-
import poseidon_module.core.logger as log
from poseidon_module.core.decorators import PoseidonExecute, ActionType, LogActionMeta, split_timestamp
from poseidon_module.action.server_id import ServerID
from poseidon_module.action.single.single_action_id import SingleNWID


class SingleNW(metaclass=LogActionMeta):
    def __init__(self):
        self.log = log.get_system_logger()
        self.poseidon_execute = PoseidonExecute(ServerID.NW_SERVER, ActionType.SINGLE_ACTION, SingleNWID)

    def action_fibo_nw_client_init(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_nw_client_deinit(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_nw_set_config(self, preferred_mode, roaming_pref=0, expect=0, dev_index=1, batch=False):
        para = {"preferred_mode": int(preferred_mode), "roaming_pref": int(roaming_pref)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_nw_get_config(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return (output.get('preferred_nw_mode'), output.get('roaming_pref')) if not batch else None

    def action_fibo_nw_get_nitz_time_info(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('info') if not batch else None

    def action_fibo_nw_event_register(self, bitmask, expect=0, dev_index=1, batch=False):
        para = {"bitmask": int("0b" + bitmask, 2)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_nw_perform_scan(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('info') if not batch else None

    def action_fibo_nw_get_reg_status(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('info') if not batch else None

    def action_fibo_nw_set_selection(self, selection_type, rat, mcc, mnc, expect=0, dev_index=1, batch=False):
        para = {"nw_selection_type": int(selection_type), "rat": int(rat), "mcc": mcc, "mnc": mnc}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_nw_get_signal_strength(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('sig_info') if not batch else None

    def action_fibo_nw_add_rx_msg_handler(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_nw_set_centric(self, centric_type, expect=0, dev_index=1, batch=False):
        para = {"centric_type": int(centric_type)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_nw_get_centric(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('centric_type') if not batch else None

    def action_fibo_nw_get_cell_access_state(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('state') if not batch else None

    def action_fibo_nw_set_low_power_mode(self, mode, expect=0, dev_index=1, batch=False):
        para = {"mode": int(mode)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_nw_get_csq(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('csq_lvl') if not batch else None

    def action_fibo_nw_set_forbidden_networks(self, forbidden_networks_len, forbidden_networks, expect=0,
                                              dev_index=1, batch=False):
        para = {"forbidden_networks_len": int(forbidden_networks_len), "forbidden_networks": forbidden_networks}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_nw_get_forbidden_networks(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('forbidden_networks_info') if not batch else None

    def action_fibo_nw_get_gtccinfo(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('gtccinfo') if not batch else None

    def action_fibo_nw_get_operator_name(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('info') if not batch else None

    def action_fibo_nw_get_current_network_status(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('network_status') if not batch else None

    def action_fibo_nw_get_current_network_system(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('network_system') if not batch else None

    def action_fibo_nw_set_lte_band(self, band_list_len, band_list, expect=0, dev_index=1, batch=False):
        para = {"band_list_len": int(band_list_len), "band_list": band_list}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_nw_get_lte_band(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('lte_band_info') if not batch else None

    def action_fibo_nw_set_nr5g_band(self, band_list_len, band_list, expect=0, dev_index=1, batch=False):
        para = {"band_list_len": int(band_list_len), "band_list": band_list}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_nw_get_nr5g_band(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('nr5g_band_info') if not batch else None

    def action_fibo_nw_get_msg_ind(self, ind_type, start_time, timeout, expect=0, dev_index=1, batch=False):
        sec, usec = split_timestamp(start_time)
        para = {"ind_type": int(ind_type), "time_sec": sec, "time_usec": usec, "timeout": int(timeout)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('ind_msg') if not batch else None

    def action_fibo_nw_get_home_plmn(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('hplmn') if not batch else None

    def action_fibo_nw_get_network_err_number(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('err_num') if not batch else None

    def action_fibo_nw_set_oos_config(self, search_interval, expect=0, dev_index=1, batch=False):
        para = {"search_interval": int(search_interval)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_nw_set_oos_enable(self, enable, expect=0, dev_index=1, batch=False):
        para = {"enable": int(enable)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_nw_get_gtccinfo_ext(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('err_num') if not batch else None

    def action_fibo_nw_bind_subscription(self, slot_id, expect=0, dev_index=1, batch=False):
        para = {"slot_id": int(slot_id)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_nw_get_signal_strength_ext(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

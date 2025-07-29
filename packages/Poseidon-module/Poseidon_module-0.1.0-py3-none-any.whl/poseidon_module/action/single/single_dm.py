# -*- coding:utf-8 -*-
import poseidon_module.core.logger as log
from poseidon_module.core.decorators import PoseidonExecute, ActionType, LogActionMeta, split_timestamp
from poseidon_module.action.server_id import ServerID
from poseidon_module.action.single.single_action_id import SingleAtDmLogID


class SingleDm(metaclass=LogActionMeta):
    def __init__(self):
        self.log = log.get_system_logger()
        self.poseidon_execute = PoseidonExecute(ServerID.AT_DM_LOG_SERVER, ActionType.SINGLE_ACTION, SingleAtDmLogID)

    def action_fibo_dm_client_init(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_dm_client_deinit(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_dm_get_manufacturer(self, size, expect=0, dev_index=1, batch=False):
        para = {"size": int(size)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('mfc') if not batch else None

    def action_fibo_dm_get_imei(self, size, expect=0, dev_index=1, batch=False):
        para = {"size": int(size)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('imei') if not batch else None

    def action_fibo_dm_get_sn(self, size, expect=0, dev_index=1, batch=False):
        para = {"size": int(size)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('sn') if not batch else None

    def action_fibo_dm_get_sdk_version(self, size, expect=0, dev_index=1, batch=False):
        para = {"size": int(size)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('sdk_version') if not batch else None

    def action_fibo_dm_get_model_id(self, size, expect=0, dev_index=1, batch=False):
        para = {"size": int(size)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('model_id') if not batch else None

    def action_fibo_dm_get_ims(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('ims') if not batch else None

    def action_fibo_dm_add_rx_msg_handler(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_dm_get_msg_ind(self, ind_type, start_time, timeout, expect=0, dev_index=1, batch=False):
        sec, usec = split_timestamp(start_time)
        para = {"ind_type": int(ind_type), "time_sec": sec, "time_usec": usec, "timeout": int(timeout)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('ind_msg') if not batch else None

    def action_fibo_dm_get_operating_mode(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('op_mode') if not batch else None

    def action_fibo_dm_set_operating_mode(self, op_mode, expect=0, dev_index=1, batch=False):
        para = {"op_mode": int(op_mode)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_dm_get_sw_version(self, size, expect=0, dev_index=1, batch=False):
        para = {"size": int(size)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('sw_version') if not batch else None

    def action_fibo_dm_get_ntp_curr_clock_src(self, size, expect=0, dev_index=1, batch=False):
        para = {"size": int(size)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('clock_src') if not batch else None

    def action_fibo_dm_node_monitor_ind_register(self, bitmask, expect=0, dev_index=1, batch=False):
        para = {"bitmask": int("0b" + bitmask, 2)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_dm_get_partition_erase_status(self, name_flag, expect=0, dev_index=1, batch=False):
        para = {"name_flag": int(name_flag)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('erase_flag') if not batch else None

    def action_fibo_dm_get_all_partition_erase_status(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return (output.get('oem_critical_a_status'), output.get('oem_critical_b_status'),
                output.get('oemdata_status')) if not batch else None

    def action_fibo_dm_clean_partition_erase_status(self, name_flag, expect=0, dev_index=1, batch=False):
        para = {"name_flag": int(name_flag)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_dm_event_register(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_dm_get_hw_version(self, size, expect=0, dev_index=1, batch=False):
        para = {"size": int(size)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('hw_version') if not batch else None

    def action_fibo_dm_get_revision_id(self, size, expect=0, dev_index=1, batch=False):
        para = {"size": int(size)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('revision_id') if not batch else None

    def action_fibo_dm_set_ims(self, ims, expect=0, dev_index=1, batch=False):
        para = {"ims": int(ims)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_dm_get_ap_version(self, size, expect=0, dev_index=1, batch=False):
        para = {"size": int(size)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('ap_version') if not batch else None

    def action_fibo_dm_bind_subscription(self, slot_id, expect=0, dev_index=1, batch=False):
        para = {"slot_id": int(slot_id)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_dm_get_imei_ext(self, slot_id, size, expect=0, dev_index=1, batch=False):
        para = {"size": int(size), "slot_id": int(slot_id)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('imei') if not batch else None

    def action_fibo_dm_modem_status_ind_register(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_dm_get_modem_status(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('md_status') if not batch else None

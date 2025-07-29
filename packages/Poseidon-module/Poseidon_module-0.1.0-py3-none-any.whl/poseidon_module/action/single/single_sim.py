# _*_ coding :UTF-8 _*_
# 开发团队  : gtyc-测试设计部
# 开发人员  : 汪灵
# 开发时间  : 2024/3/22  15:55
# 文件名称  : single_sim.PY
# 开发工具  : Python
import poseidon_module.core.logger as log
from poseidon_module.core.decorators import LogActionMeta, PoseidonExecute, ActionType, split_timestamp
from poseidon_module.action.server_id import ServerID
from poseidon_module.action.single.single_action_id import SingleSimID


class SingleSim(metaclass=LogActionMeta):
    def __init__(self):
        self.log = log.get_system_logger()
        self.poseidon_execute = PoseidonExecute(ServerID.SIM_SERVER, ActionType.SINGLE_ACTION, SingleSimID)

    def action_fibo_sim_client_init(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_sim_client_deinit(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_sim_get_imsi(self, app_info, size=128, expect=0, dev_index=1, batch=False):
        para = {"size": size, "app_info": app_info}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('imsi') if not batch else None

    def action_fibo_sim_get_iccid(self, slot_id, size=128, expect=0, dev_index=1, batch=False):
        para = {"slot_id": int(slot_id), "size": size}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('iccid') if not batch else None

    def action_fibo_sim_get_phonenumber(self, app_info, size=128, expect=0, dev_index=1, batch=False):
        para = {"size": size, "app_info": app_info}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('phonenum') if not batch else None

    def action_fibo_sim_verify_pin(self, pin_info, expect=0, dev_index=1, batch=False):
        para = {"pin_info": pin_info}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_sim_change_pin(self, pin_info, expect=0, dev_index=1, batch=False):
        para = {"pin_info": pin_info}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_sim_unblock_pin(self, pin_info, expect=0, dev_index=1, batch=False):
        para = {"pin_info": pin_info}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_sim_enable_pin(self, pin_info, expect=0, dev_index=1, batch=False):
        para = {"pin_info": pin_info}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_sim_disable_pin(self, pin_info, expect=0, dev_index=1, batch=False):
        para = {"pin_info": pin_info}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_sim_get_card_status(self, slot_id, expect=0, dev_index=1, batch=False):
        para = {"slot_id": slot_id}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('card_status') if not batch else None

    def action_fibo_sim_register_event(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_sim_add_rx_msg_handler(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_sim_reset(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_sim_open_channel(self, req_info, expect=0, dev_index=1, batch=False):
        para = {"req_info": req_info}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return (output.get('channel_id'), output.get("channel_id_valid")) if not batch else None

    def action_fibo_sim_close_channel(self, channel_info, expect=0, dev_index=1, batch=False):
        para = {"channel_info": channel_info}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_sim_send_apdu(self, apdu_cmd, expect=0, dev_index=1, batch=False):
        para = {"apdu_cmd": apdu_cmd}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return (output.get('apdu_info'), output.get("apdu_len")) if not batch else None

    def action_fibo_sim_get_status_ind(self, ind_type, start_time, timeout, expect=0, dev_index=1, batch=False):
        """
        获取指定上报类型的上报
        E_FIBO_SIM_IND_SLOT_CHG_EVENT    2
        E_FIBO_SIM_IND_CARD_STATUS_EVENT   4
        SIM_IND_CURRENT_DDS_EVENT_IND_FLAG   8
        SIM_IND_MODEM_SSR                   (1 << 4)
        """
        sec, usec = split_timestamp(start_time)
        para = {"ind_type": int(ind_type), "time_sec": sec, "time_usec": usec, "timeout": int(timeout)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('ind_msg') if not batch else None

    def action_fibo_sim_get_slot(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('slot_id') if not batch else None

    def action_fibo_sim_switch_slot(self, slot_id, expect=0, dev_index=1, batch=False):
        para = {"slot_id": slot_id}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_sim_only_switch_main_cards(self, slot_id, expect=0, dev_index=1, batch=False):
        para = {"slot_id": slot_id}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

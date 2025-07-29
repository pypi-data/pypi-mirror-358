# _*_ coding :UTF-8 _*_
# 开发团队  : gtyc-测试设计部
# 开发人员  : 汪灵
# 开发时间  : 2025/5/25  15:55
# 文件名称  : single_sim.PY
# 开发工具  : Python
import poseidon_module.core.logger as log
from poseidon_module.core.decorators import LogActionMeta, PoseidonExecute, ActionType, split_timestamp, update_dic
from poseidon_module.action.server_id import ServerID
from poseidon_module.action.single.single_action_id import SingleSMSID

default_sms = {"format": 0, "mode": 0x06, "message_class_valid": 0, "message_class": 0,
               "mobile_number": "", "message_text": "test msg"}


class SingleSMS(metaclass=LogActionMeta):
    def __init__(self):
        self.log = log.get_system_logger()
        self.poseidon_execute = PoseidonExecute(ServerID.SMS_SERVER, ActionType.SINGLE_ACTION, SingleSMSID)

    def action_fibo_sms_client_init(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('handle') if not batch else None

    def action_fibo_sms_client_deinit(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_sms_send_message(self, sms_info, expect=0, dev_index=1, batch=False):
        default_info = default_sms.copy()
        para = {"sms_info": update_dic(sms_info, default_info)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_sms_send_message_async(self, sms_info, expect=0, dev_index=1, batch=False):
        default_info = default_sms.copy()
        para = {"sms_info": update_dic(sms_info, default_info)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_sms_send_smspdu(self, message, expect=0, dev_index=1, batch=False):
        para = {"message": message}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('raw_resp') if not batch else None

    def action_fibo_sms_send_smspdu_async(self, message, expect=0, dev_index=1, batch=False):
        para = {"message": message}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_sms_read_message(self, req_info, expect=0, dev_index=1, batch=False):
        default_info = {"storage_index": 1, "storage_type": False, "message_mode_valid": 1, "message_mode": 1, }
        para = {"req_info": update_dic(req_info, default_info)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('sms_info') if not batch else None

    def action_fibo_sms_add_rx_msg_handler(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_sms_delete_from_storage(self, del_info, expect=0, dev_index=1, batch=False):
        default_info = {"storage": False, "storage_idx_valid": 1, "storage_idx": 1, "mode_valid": 1, "mode": 1}
        para = {"del_info": update_dic(del_info, default_info)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_sms_get_sms_center_address(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('center_cfg') if not batch else None

    def action_fibo_sms_set_sms_center_address(self, center_cfg, expect=0, dev_index=1, batch=False):
        default_info = {"type_valid": 0, "addr_type": False, "addr": ""}
        para = {"center_cfg": update_dic(center_cfg, default_info)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_sms_get_msg_list(self, req_info="", expect=0, dev_index=1, batch=False):
        default_info = {"storage_type": False, "tag_type_valid": False, "tag_type": False, "message_mode_valid": 1,
                        "message_mode": 1, }
        para = {"req_info": update_dic(req_info, default_info)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('store_info') if not batch else None

    def action_fibo_sms_get_max_store_size(self, get_info="", expect=0, dev_index=1, batch=False):
        default_info = {"storage": False, "mode_valid": 1, "mode": 1}
        para = {"get_info": update_dic(get_info, default_info)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('store_info') if not batch else None

    def action_fibo_sms_set_ims_status(self, status, expect=0, dev_index=1, batch=False):
        para = {"status": status}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_sms_bind_subscription(self, slot_id, expect=0, dev_index=1, batch=False):
        para = {"slot_id": slot_id}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_sms_set_whitelist_status(self, whitelist_enable, gpp2_enable, expect=0, dev_index=1,
                                             batch=False):
        para = {"whitelist_enable": whitelist_enable, "gpp2_enable": gpp2_enable}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_sms_get_whitelist_status(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return (output.get('whitelist_enable'), output.get("gpp2_enable")) if not batch else None

    def action_fibo_sms_set_whitelist_number(self, whitelist, expect=0, dev_index=1, batch=False):
        para = {"whitelist": whitelist}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_sms_get_whitelist_number(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('whitelist') if not batch else None

    def action_fibo_sms_get_drop_message(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('drop_message') if not batch else None

    def action_fibo_sms_receive_ind(self, ind_type, start_time, timeout, expect=0, dev_index=1, batch=False):
        sec, usec = split_timestamp(start_time)
        para = {"ind_type": int(ind_type), "time_sec": sec, "time_usec": usec, "timeout": int(timeout)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('ind_msg') if not batch else None

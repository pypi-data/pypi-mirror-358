# _*_ coding :UTF-8 _*_
# 开发团队  : gtyc-测试设计部
# 开发人员  : 汪灵
# 开发时间  : 2025/5/27  17:07
# 文件名称  : single_voice.PY
# 开发工具  : Python
import poseidon_module.core.logger as log
from poseidon_module.core.decorators import LogActionMeta, PoseidonExecute, ActionType, split_timestamp, update_dic
from poseidon_module.action.server_id import ServerID
from poseidon_module.action.single.single_action_id import SingleVoiceRtpID


class SingleVoice(metaclass=LogActionMeta):
    def __init__(self):
        self.log = log.get_system_logger()
        server_id = ServerID.VOICE_RTP_RTC_SERVER
        self.poseidon_execute = PoseidonExecute(server_id, ActionType.SINGLE_ACTION, SingleVoiceRtpID)

    def action_fibo_voice_client_init(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('handle') if not batch else None

    def action_fibo_voice_client_deinit(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_voice_start_call(self, number, expect=0, dev_index=1, batch=False):
        para = {"phone_number": number}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('call_id') if not batch else None

    def action_fibo_voice_answer_call(self, call_id, expect=0, dev_index=1, batch=False):
        para = {"call_id": int(call_id)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_voice_end_call(self, call_id, expect=0, dev_index=1, batch=False):
        para = {"call_id": int(call_id)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_voice_hold_call(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_voice_unhold_call(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_voice_end_all_call(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_voice_enable_auto_answer(self, timesec=2, expect=0, dev_index=1, batch=False):
        para = {"time": timesec}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_voice_disable_auto_answer(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_voice_get_call_status(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('call_status') if not batch else None

    def action_fibo_voice_call_add_state_handle(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_voice_get_msg_ind(self, ind_type, start_time, timeout, expect=0, dev_index=1, batch=False):
        """
        获取指定上报类型的上报
        E_FIBO_VOICE_GET_CALL_STATUS   -- 1
        VOICE_GET_DTMF_IND_FLAG     -- 2
        VOICE_GET_ECALL_IND_FLAG  -- 3
        """
        sec, usec = split_timestamp(start_time)
        para = {"ind_type": int(ind_type), "time_sec": sec, "time_usec": usec, "timeout": int(timeout)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch, socket_timeout=timeout + 10)
        return output.get('ind_msg') if not batch else None

    def action_fibo_voice_ecall_start_call(self, ecall_info="", expect=0, dev_index=1, batch=False):
        default_info = {"ecall_type": 1, "ecall_mode": 1, "msd_type": 1, "msd_len": 2, "ecall_number": "",
                        "msd_content": ""}
        para = {"ecall_info": update_dic(ecall_info, default_info)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_voice_ecall_end_call(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_voice_ecall_update_msd(self, msd_type, msd_data, msd_len, expect=0, dev_index=1,
                                           batch=False):
        para = {"msd_type": int(msd_type), "msd_data": msd_data, "msd_len": int(msd_len)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_voice_conference(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_voice_end_conference(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_voice_mute(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_voice_unmute(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_voice_dtmf(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_voice_register_bitmask(self, bitmask, expect=0, dev_index=1, batch=False):
        """bitmask:0x01 call_event; 0x04:ecall; 0x08:mute"""
        para = {"bitmask": bitmask}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_voice_call_remove_state_handler(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_voice_ecall_start_call_ext(self, ecall_info="", expect=0, dev_index=1, batch=False):
        default_info = {"ecall_variant": 1, "ecall_type_ext": 1, "ecall_number": "", "msd_content": "", "msd_len": 20}
        para = {"ecall_info": update_dic(ecall_info, default_info)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_voice_ecall_update_msd_ext(self, msd_data, msd_len, expect=0, dev_index=1,
                                               batch=False):
        para = {"msd_data": msd_data, "msd_len": int(msd_len)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_voice_ecall_deregistration(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_voice_ecall_set_config(self, ecall_conf, expect=0, dev_index=1, batch=False):
        default_info = {"deregtime": 1, "deregtime_is_valid": 1, "duration": 1, "duration_is_valid": 2,
                        "ecall_oprt_mode": 1, "ecall_oprt_mode_is_valid": 1, "ecall_profile": 1,
                        "ecall_profile_is_valid": 1, "pause": 1, "pause_is_valid": 1}
        para = {"ecall_config": update_dic(ecall_conf, default_info)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_voice_ecall_get_config(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('ecall_config') if not batch else None

    def action_fibo_voice_set_volte(self, volte, expect=0, dev_index=1, batch=False):
        para = {"volte": volte}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_voice_bind_subscription(self, slot_id, expect=0, dev_index=1, batch=False):
        para = {"slot_id": slot_id}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

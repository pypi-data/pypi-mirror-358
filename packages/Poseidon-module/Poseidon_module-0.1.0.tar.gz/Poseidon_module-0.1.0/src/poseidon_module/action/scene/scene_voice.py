# -*- coding:utf-8 -*-
import poseidon_module.core.logger as log
from poseidon_module.core.decorators import LogActionMeta, PoseidonExecute, ActionType, split_timestamp
from poseidon_module.action.server_id import ServerID
from poseidon_module.action.scene.scene_id import SceneVoiceID


class SceneVoice(metaclass=LogActionMeta):
    def __init__(self):
        self.log = log.get_system_logger()
        self.poseidon_execute = PoseidonExecute(ServerID.VOICE_RTP_RTC_SERVER, ActionType.SCENE_ACTION, SceneVoiceID)

    def action_scene_voice_setup(self, dev_index=1):
        self.poseidon_execute.execute_action(None, 0, dev_index)

    def action_scene_voice_check_func(self, slot_id, phone_num, dev_index=1):
        """
        单模块呼叫运营商电话，保持通话10秒并挂断
        :param slot_id:
        :param phone_num:对方号码
        :param dev_index:
        :return:None
        """
        para = {"slot_id": int(slot_id), "phone_number": phone_num}
        self.poseidon_execute.execute_action(para, 0, dev_index, socket_timeout=100)

    def action_scene_voice_start_call(self, slot_id, phone_num, dev_index=1):
        para = {"slot_id": int(slot_id), "phone_number": phone_num}
        output = self.poseidon_execute.execute_action(para, 0, dev_index, socket_timeout=70)
        return output.get('call_id'), output.get('end_reason')

    def action_scene_voice_incoming_check(self, slot_id, phone_num, start_time, dev_index=1):
        sec, usec = split_timestamp(start_time)
        para = {"slot_id": int(slot_id), "phone_number": phone_num, "time_sec": sec, "time_usec": usec}
        output = self.poseidon_execute.execute_action(para, 0, dev_index, socket_timeout=70)
        return output.get('call_id'), output.get('end_reason')

    def action_scene_voice_answer_call(self, slot_id, phone_num, call_id, dev_index=1):
        para = {"slot_id": int(slot_id), "phone_number": phone_num, "call_id": call_id}
        output = self.poseidon_execute.execute_action(para, 0, dev_index, socket_timeout=70)
        return output.get('call_id'), output.get('end_reason')

    def action_scene_voice_end_call(self, slot_id, phone_num, call_id, dev_index=1):
        para = {"slot_id": int(slot_id), "phone_number": phone_num, "call_id": call_id}
        output = self.poseidon_execute.execute_action(para, 0, dev_index, socket_timeout=70)
        return output.get('call_id'), output.get('end_reason')

    def action_scene_voice_end_all_call(self, slot_id, phone_num, dev_index=1):
        para = {"slot_id": int(slot_id), "phone_number": phone_num}
        self.poseidon_execute.execute_action(para, 0, dev_index, socket_timeout=70)

    def action_scene_voice_state_check(self, slot_id, phone_num, state, start_time, dev_index=1):
        sec, usec = split_timestamp(start_time)
        para = {"slot_id": int(slot_id), "phone_number": phone_num, "state": int(state), "time_sec": sec,
                "time_usec": usec}
        socket_timeout = 310 if state == 5 else 70
        output = self.poseidon_execute.execute_action(para, 0, dev_index, socket_timeout=socket_timeout)
        return output.get('call_id'), output.get('end_reason')

    def action_scene_voice_teardown(self, dev_index=1):
        self.poseidon_execute.execute_action(None, 0, dev_index)

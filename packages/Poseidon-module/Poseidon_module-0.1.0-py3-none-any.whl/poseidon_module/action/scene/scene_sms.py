# -*- coding:utf-8 -*-
import poseidon_module.core.logger as log
from poseidon_module.core.decorators import LogActionMeta, PoseidonExecute, ActionType, update_dic, split_timestamp
from poseidon_module.action.server_id import ServerID
from poseidon_module.action.scene.scene_id import SceneSmsID
from poseidon_module.action.single.single_sms import default_sms
from poseidon_module.core.decorators import PoseidonUtil
from poseidon_module.utils.codec import UtilCodec
from poseidon_module.utils.comm import UtilComm


class SceneSms(metaclass=LogActionMeta):
    def __init__(self):
        self.log = log.get_system_logger()
        self.p_util = PoseidonUtil()
        self.u_codec = UtilCodec()
        self.u_comm = UtilComm()
        self.poseidon_execute = PoseidonExecute(ServerID.SMS_SERVER, ActionType.SCENE_ACTION, SceneSmsID)

    def action_scene_sms_setup(self, dev_index=1):
        self.poseidon_execute.execute_action(None, 0, dev_index)

    def action_scene_sms_teardown(self, dev_index=1):
        self.poseidon_execute.execute_action(None, 0, dev_index)

    def action_scene_sms_send_msg(self, slot_id, sms_info, dev_index=1):
        default_info = default_sms.copy()
        para = {"slot_id": slot_id, "sms_info": update_dic(sms_info, default_info)}
        self.poseidon_execute.execute_action(para, 0, dev_index)

    def action_scene_sms_send_msg_async(self, slot_id, sms_info, dev_index=1):
        default_info = default_sms.copy()
        para = {"slot_id": slot_id, "sms_info": update_dic(sms_info, default_info)}
        self.poseidon_execute.execute_action(para, 0, dev_index)

    def action_scene_sms_send_pdu(self, slot_id, message, dev_index=1):
        para = {"slot_id": slot_id, "message": message}
        self.poseidon_execute.execute_action(para, 0, dev_index)

    def action_scene_sms_send_pdu_async(self, slot_id, message, dev_index=1):
        para = {"slot_id": slot_id, "message": message}
        self.poseidon_execute.execute_action(para, 0, dev_index)

    def action_scene_sms_receive_check(self, slot_id, mobile_number, message_text, start_time,
                                       expect_segments=1, timeout=30, dev_index=1):
        sec, usec = split_timestamp(start_time)
        para = {"slot_id": slot_id, "mobile_number": mobile_number, "message_text": message_text,
                "time_sec": sec, "time_usec": usec, "expect_segments": int(expect_segments), "timeout": int(timeout)}
        self.poseidon_execute.execute_action(para, 0, dev_index)

    def action_scene_sms_check_fun(self, slot_id, mobile_number, message_text, timeout=60, dev_index=1):
        default_info = default_sms.copy()
        sms_info = {"mobile_number": mobile_number, "message_text": message_text}
        para = {"slot_id": slot_id, "mobile_number": mobile_number, "message_text": message_text,
                "timeout": int(timeout), "expect_segments": 1, "sms_info": update_dic(sms_info, default_info)}
        self.poseidon_execute.execute_action(para, 0, dev_index)

    def __send_pdu(self, sms_info, expect_segments, sms, slot_id, dev_index):
        for current_num in range(1, expect_segments + 1):
            args = (sms_info["mobile_number"], sms_info["message_text"], "", sms_info["format"],
                    sms_info["message_class_valid"], sms_info["message_class"], expect_segments, current_num)
            pdu_content, pdu_content_len = self.u_codec.lc_pdu_encode(*args)
            if sms == "async_pdu":
                self.action_scene_sms_send_pdu_async(slot_id, pdu_content, dev_index=dev_index)
            else:
                self.action_scene_sms_send_pdu(slot_id, pdu_content, dev_index=dev_index)

    def action_scene_dual_dev_sms(self, format_type, message_class, sms="text", segments=1, slot=1, prefix="",
                                  char_type=0, direction="MO"):
        """双模块短信收发测试 """
        segments_map = {
            "7BIT": [[1, 160], [161, 300], [301, 450]],
            "BINARY": [[1, 140], [141, 260], [261, 390]],
            "UCS2": [[1, 70], [71, 130], [131, 195]]
        }  # 短信分包映射表
        direction_map = {"MO": [1, 2], "MT": [2, 1], "SELF": [1, 1]}
        class_map = {"class0": 0, "class1": 1, "class2": 2, "class3": 3, "classNone": 4}
        assert segments_map[format_type] is not None, "短信格式错误!"
        msg_len = segments_map[format_type][segments - 1]  # 获取短信长度信息
        slot_list = slot if isinstance(slot, list) else [slot, slot]  # 构造短信收发卡槽号列表
        dev_list = direction_map.get(direction, [1, 1])  # 构造短信收发方向信息，以device 1 为主设备
        format_map = {"7BIT": 0, "BINARY": 1, "UCS2": 2}
        main_num = self.u_comm.lc_get_phone_num(slot=slot_list[0], dev_index=dev_list[0])
        second_num = prefix + self.u_comm.lc_get_phone_num(slot=slot_list[1], dev_index=dev_list[1])
        # 生成短信文本
        sms_len, content_text, sms_code = self.u_codec.lc_content_create(msg_len[0], msg_len[1], char_type)
        self.log.info(f"sms_len:{sms_len}, content_text:{content_text}, sms_code:{sms_code}")
        content = sms_code if format_map[format_type] == 2 else content_text
        start_time = self.p_util.get_modem_time(0, dev_index=dev_list[1])  # 收短信的时间
        # 构造短信信息
        sms_info = {
            "format": format_map[format_type],
            "mode": 0x06,
            "message_class_valid": (0, 1)[class_map.get(message_class) is not None],
            "message_class": class_map.get(message_class, 4),
            "mobile_number": second_num,
            "message_text": content_text if "pdu" in sms else content
        }
        # 发送短信
        if sms == "text":
            self.action_scene_sms_send_msg(slot_list[0], sms_info=sms_info, dev_index=dev_list[0])
        elif sms == "async_text":
            self.action_scene_sms_send_msg_async(slot_list[0], sms_info=sms_info, dev_index=dev_list[0])
        else:
            self.__send_pdu(sms_info, segments, sms, slot_list[0], dev_list[0])
        self.action_scene_sms_receive_check(slot_list[1], main_num, content, start_time, segments, 30, dev_list[1])

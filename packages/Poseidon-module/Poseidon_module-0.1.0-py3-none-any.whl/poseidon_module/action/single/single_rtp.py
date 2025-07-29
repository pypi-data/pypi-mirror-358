#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Team    ：GTYC Test Platform Development Dept.
@File    ：single_rtp.py
@IDE     ：PyCharm 
@Author  ：WangLing
@Date    ：2025/05/28 16:01
"""
import poseidon_module.core.logger as log
from poseidon_module.core.decorators import LogActionMeta, PoseidonExecute, ActionType, update_dic
from poseidon_module.action.server_id import ServerID
from poseidon_module.action.single.single_action_id import SingleVoiceRtpID


class SingleRtp(metaclass=LogActionMeta):
    def __init__(self):
        self.log = log.get_system_logger()
        server_id = ServerID.VOICE_RTP_RTC_SERVER
        self.poseidon_execute = PoseidonExecute(server_id, ActionType.SINGLE_ACTION, SingleVoiceRtpID)

    def action_fibo_rtp_enable(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_rtp_disable(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_rtp_config(self, rtp_config=None, expect=0, dev_index=1, batch=False):
        default_info = {"src_ip": "198.18.34.15", "dst_ip": "198.18.32.17", "src_port": 53248, "dst_port": 53248,
                        "audio_source": 1, "audio_type": 0, "rtp_type": 2, "audio_rate": 8000, "audio_ch": 1,
                        "socket_ttl": 20}
        para = {"rtp_config": update_dic(rtp_config, default_info)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_rtp_get_config(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('rtp_config') if not batch else None

    def action_fibo_rtp_config_v2(self, rtp_config=None, expect=0, dev_index=1, batch=False):
        default_info = {"src_ip": "198.18.34.15", "dst_ip": "198.18.32.17", "src_port": 53248, "dst_port": 53248,
                        "audio_source": 1, "audio_type": 0, "rtp_type": 2, "audio_rate": 8000, "audio_ch": 1,
                        "socket_ttl": 20, "ssrc": 0xffff0000, "eth_name": "eth0.4"}
        para = {"rtp_config": update_dic(rtp_config, default_info)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_rtp_get_config_v2(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('rtp_config') if not batch else None

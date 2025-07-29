# -*- coding:utf-8 -*-
import poseidon_module.core.logger as log
from poseidon_module.core.decorators import LogActionMeta, PoseidonExecute, ActionType, split_timestamp
from poseidon_module.action.server_id import ServerID
from poseidon_module.action.scene.scene_id import SceneNWID


class SceneNw(metaclass=LogActionMeta):
    def __init__(self):
        self.log = log.get_system_logger()
        self.poseidon_execute = PoseidonExecute(ServerID.NW_SERVER, ActionType.SCENE_ACTION, SceneNWID)
        self.mode_dic = {
            "NO": 0x00,
            "CDMA": 0x01,
            "GSM": 0x04,
            "WCDMA": 0x08,
            "LTE": 0x10,
            "SA5G": 0x40,
            "GSM_WCDMA": 0x0c,
            "GSM_LTE": 0x14,
            "WCDMA_LTE": 0x18,
            "AUTO4G": 0x1c,
            "GSM_SA5G": 0x44,
            "WCDMA_SA5G": 0x48,
            "NSA5G": 0x50,
            "GSM_NSA5G": 0x54,
            "WCDMA_NSA5G": 0x58,
            "AUTO": 0x80
        }

    def action_scene_nw_setup(self, dev_index=1):
        """
        nw 初始化, init all queue->nw_init->add call back
        :param 0:
        :param dev_index:
        :return:handle
        """
        self.poseidon_execute.execute_action(None, 0, dev_index)

    def action_scene_nw_set_pref_mode(self, slot_id, mode_pref, timeout=60, dev_index=1):
        """
        nw 锁网，set pref mode->get pref mode->check nw status ing msg
        :param slot_id:
        :param mode_pref: 注网制式 like self.mode_dic key
        :param timeout: 检查锁网注册超时时间
        :param 0:
        :param dev_index:
        :return: None
        """
        para = {"slot_id": int(slot_id), "preferred_mode": self.mode_dic[mode_pref], "timeout": int(timeout)}
        self.poseidon_execute.execute_action(para, 0, dev_index, socket_timeout=timeout + 30)

    def action_scene_nw_check_target_rat(self, slot_id, check_mode, start_time=0, timeout=60, ind=0, dev_index=1):
        """
        检查 目标网络制式
        :param slot_id:
        :param check_mode: 注网制式 like self.mode_dic key
        :param start_time: 时间触发时间，为时间戳
        :param timeout: 检查目标网络超时时间
        :param ind: 1-获取上报， 0- 主动查询
        :param dev_index:
        :return: None
        """
        sec, usec = split_timestamp(start_time)
        para = {"slot_id": int(slot_id), "preferred_mode": self.mode_dic[check_mode],
                "ind": int(ind), "time_sec": sec, "time_usec": usec, "timeout": int(timeout)}
        self.poseidon_execute.execute_action(para, 0, dev_index, socket_timeout=timeout + 30)

    def action_scene_nw_teardown(self, dev_index=1):
        """ nw teardown set pref mode to auto->register 0x00->deinit"""
        self.poseidon_execute.execute_action(None, 0, dev_index)

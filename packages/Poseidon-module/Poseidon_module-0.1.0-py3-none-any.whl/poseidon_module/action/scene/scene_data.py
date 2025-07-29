# -*- coding:utf-8 -*-
import poseidon_module.core.logger as log
from poseidon_module.core.decorators import LogActionMeta, PoseidonExecute, ActionType, update_dic
from poseidon_module.action.server_id import ServerID
from poseidon_module.action.scene.scene_id import SceneDataID
from poseidon_module.action.single.single_data import default_apn


class SceneData(metaclass=LogActionMeta):
    def __init__(self):
        self.log = log.get_system_logger()
        self.poseidon_execute = PoseidonExecute(ServerID.DATA_DHCP_SERVER, ActionType.SCENE_ACTION, SceneDataID)

    def action_scene_data_setup(self, dev_index=1):
        """ 数据拨号teardown, 删除所有APN 并断开数据拨号 """
        self.poseidon_execute.execute_action(None, 0, dev_index)

    def action_scene_data_teardown(self, dev_index=1):
        """ 数据拨号teardown, 删除所有APN 并断开数据拨号 """
        self.poseidon_execute.execute_action(None, 0, dev_index)

    def action_scene_async_data_call_ping(self, slot_id=1, apn_info="", route_ip="default", dev_index=1):
        """ 发起异步数据拨号并ping网，set apn-> get apn->async start call->check all status->get call info->add rule->ping """
        info = default_apn.copy()
        para = {"slot_id": slot_id, "apn_info": update_dic(apn_info, info), "route_ip": route_ip}
        output = self.poseidon_execute.execute_action(para, expect=0, dev_index=dev_index, socket_timeout=210)
        return output.get('call_ret'), output.get('call_info')

    def action_scene_data_call_ping(self, slot_id=1, apn_info="", route_ip="default", dev_index=1):
        """发起同步数据拨号并ping网，set apn-> get apn->start call->check all status->get call info->add rule->ping"""
        info = default_apn.copy()
        para = {"slot_id": slot_id, "apn_info": update_dic(apn_info, info), "route_ip": route_ip}
        output = self.poseidon_execute.execute_action(para, expect=0, dev_index=dev_index, socket_timeout=210)
        return output.get('call_ret'), output.get('call_info')

    def action_scene_async_data_call(self, slot_id=1, apn_info="", dev_index=1):
        """SIMx仅异步拨号，set apn-> get apn->start/async start call->check all status"""
        info = default_apn.copy()
        para = {"slot_id": slot_id, "apn_info": update_dic(apn_info, info)}
        output = self.poseidon_execute.execute_action(para, expect=0, dev_index=dev_index, socket_timeout=210)
        return output.get('call_ret')

    def action_scene_data_call(self, slot_id=1, apn_info="", dev_index=1):
        """SIMx仅同步拨号，set apn-> get apn->start/async start call->check all status"""
        info = default_apn.copy()
        para = {"slot_id": slot_id, "apn_info": update_dic(apn_info, info)}
        output = self.poseidon_execute.execute_action(para, expect=0, dev_index=dev_index, socket_timeout=210)
        return output.get('call_ret')

    def action_scene_data_async_stop_call(self, slot_id, call_id, dev_index=1):
        """断开异步数据拨号 , stop/stop async->get ing msg->check status->del apn"""
        para = {"slot_id": slot_id, "call_id": call_id}
        self.poseidon_execute.execute_action(para, expect=0, dev_index=dev_index)

    def action_scene_data_stop_call(self, slot_id, call_id, dev_index=1):
        """断开同步数据拨号 , stop/stop async->get ing msg->check status->del apn"""
        para = {"slot_id": slot_id, "call_id": call_id}
        self.poseidon_execute.execute_action(para, expect=0, dev_index=dev_index)

    def action_scene_data_check_fun(self, slot_id=1, apn_info="", route_ip="default", dev_index=1):
        """ 检查数据业务 """
        info = default_apn.copy()
        para = {"slot_id": slot_id, "apn_info": update_dic(apn_info, info), "route_ip": route_ip}
        self.poseidon_execute.execute_action(para, expect=0, dev_index=dev_index, socket_timeout=210)

    def action_scene_data_multi_data_call(self, slot_id, call_num, ip_list, dev_index=1):
        """建立多路数据业务"""
        server_list = ["default"] + ip_list
        para = {"slot_id": slot_id, "call_num": call_num, "ip_list": server_list}
        output = self.poseidon_execute.execute_action(para, expect=0, dev_index=dev_index, socket_timeout=210)
        return output.get("call_ids")

    def action_scene_data_multi_data_call_stop(self, slot_id, cid_list, dev_index=1):
        """断开多路数据拨号"""
        para = {"slot_id": slot_id, "cid_list": cid_list}
        self.poseidon_execute.execute_action(para, expect=0, dev_index=dev_index, socket_timeout=210)

    def action_scene_add_route_and_dns(self, slot_id, call_id=1, route_ip="default", dev_index=1):
        """ 添加DNS和路由 """
        para = {"slot_id": slot_id, "call_id": call_id, "route_ip": route_ip}
        output = self.poseidon_execute.execute_action(para, expect=0, dev_index=dev_index)
        return output.get('call_info')

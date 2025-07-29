# -*- coding:utf-8 -*-
import poseidon_module.core.logger as log
from poseidon_module.core.decorators import LogActionMeta, PoseidonExecute, ActionType
from poseidon_module.action.server_id import ServerID
from poseidon_module.action.scene.scene_id import SceneDeviceUpdateID


class SceneDevice(metaclass=LogActionMeta):
    def __init__(self):
        self.log = log.get_system_logger()
        self.poseidon_execute = PoseidonExecute(ServerID.DEVICE_UPDATE_SERVER, ActionType.SCENE_ACTION,
                                                SceneDeviceUpdateID)

    def action_scene_device_ab_sync(self, dev_index=1):
        """主备同步"""
        self.poseidon_execute.execute_action(None, expect=0, dev_index=dev_index, socket_timeout=300)

    def action_scene_device_get_sync_status(self, dev_index=1):
        """获取同步状态"""
        output = self.poseidon_execute.execute_action(None, expect=0, dev_index=dev_index)
        return output.get("status")

    def action_scene_device_get_current_partition(self, dev_index=1):
        """获取当前所在分区"""
        output = self.poseidon_execute.execute_action(None, expect=0, dev_index=dev_index)
        return output.get("cur_partition")

    def action_scene_device_set_nextboot_partition(self, next_partition=None, dev_index=1):
        """设置下一次启动的分区"""
        para = {"next_partition": int(next_partition)}
        self.poseidon_execute.execute_action(para, expect=0, dev_index=dev_index)

    def action_scene_device_damage_partition(self, partition_name=None, dev_index=1):
        para = {"partition_name": partition_name}
        self.poseidon_execute.execute_action(para, expect=0, dev_index=dev_index)

    def action_scene_device_get_sync_cfg(self, dev_index=1):
        """查询当前同步设置"""
        output = self.poseidon_execute.execute_action(None, expect=0, dev_index=dev_index)
        return output.get("sync_cfg")

    def action_scene_device_set_sync_cfg(self, sync_cfg=None, dev_index=1):
        """设置同步配置"""
        para = {"sync_cfg": int(sync_cfg)}
        self.poseidon_execute.execute_action(para, expect=0, dev_index=dev_index)

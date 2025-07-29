# -*- coding:utf-8 -*-
import poseidon_module.core.logger as log
from poseidon_module.core.decorators import LogActionMeta, PoseidonExecute, ActionType
from poseidon_module.action.server_id import ServerID
from poseidon_module.action.scene.scene_id import SceneDmID


class SceneDm(metaclass=LogActionMeta):
    def __init__(self):
        self.log = log.get_system_logger()
        self.poseidon_execute = PoseidonExecute(ServerID.AT_DM_LOG_SERVER, ActionType.SCENE_ACTION, SceneDmID)

    def action_scene_dm_setup(self, dev_index=1):
        self.poseidon_execute.execute_action(None, 0, dev_index)

    def action_scene_dm_teardown(self, dev_index=1):
        self.poseidon_execute.execute_action(None, 0, dev_index)

    def action_scene_flight_mode_on(self, dev_index=1):
        self.poseidon_execute.execute_action(None, 0, dev_index)

    def action_scene_flight_mode_off(self, dev_index=1):
        self.poseidon_execute.execute_action(None, 0, dev_index)

    def action_scene_flight_mode_on_off(self, dev_index=1):
        self.poseidon_execute.execute_action(None, 0, dev_index)

    def action_scene_get_flight_mode(self, dev_index=1):
        output = self.poseidon_execute.execute_action(None, 0, dev_index)
        return output.get('op_mode')

    def action_scene_dm_check_info(self, dev_index=1):
        self.poseidon_execute.execute_action(None, 0, dev_index)

    def action_scene_ims_enable(self, dev_index=1):
        self.poseidon_execute.execute_action(None, 0, dev_index)

    def action_scene_ims_disable(self, dev_index=1):
        self.poseidon_execute.execute_action(None, 0, dev_index)

    def action_scene_vonr_enable(self, dev_index=1):
        self.poseidon_execute.execute_action(None, 0, dev_index)

# -*- coding:utf-8 -*-
import poseidon_module.core.logger as log
from poseidon_module.core.decorators import LogActionMeta, PoseidonExecute, ActionType
from poseidon_module.action.server_id import ServerID
from poseidon_module.action.scene.scene_id import SceneSimID


class SceneSim(metaclass=LogActionMeta):
    def __init__(self):
        self.log = log.get_system_logger()
        self.poseidon_execute = PoseidonExecute(ServerID.SIM_SERVER, ActionType.SCENE_ACTION, SceneSimID)

    def action_scene_sim_setup(self, dev_index=1):
        self.poseidon_execute.execute_action(None, 0, dev_index)

    def action_scene_sim_teardown(self, dev_index=1):
        self.poseidon_execute.execute_action(None, 0, dev_index)

    def action_scene_sim_switch_slot(self, slot_id, dev_index=1):
        para = {"slot_id": slot_id}
        self.poseidon_execute.execute_action(para, 0, dev_index)

    def action_scene_sim_check_info(self, slot_id, dev_index=1):
        para = {"slot_id": slot_id}
        self.poseidon_execute.execute_action(para, 0, dev_index)

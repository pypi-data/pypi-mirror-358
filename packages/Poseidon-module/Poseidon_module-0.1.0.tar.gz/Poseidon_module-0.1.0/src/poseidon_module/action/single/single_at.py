# -*- coding:utf-8 -*-
import poseidon_module.core.logger as log
from poseidon_module.core.decorators import PoseidonExecute, ActionType, LogActionMeta
from poseidon_module.action.server_id import ServerID
from poseidon_module.action.single.single_action_id import SingleAtDmLogID


class SingleAt(metaclass=LogActionMeta):
    def __init__(self):
        self.log = log.get_system_logger()
        self.poseidon_execute = PoseidonExecute(ServerID.AT_DM_LOG_SERVER, ActionType.SINGLE_ACTION, SingleAtDmLogID)

    def action_fibo_at_register_urc_callback(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_at_unregister_urc_callback(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_send_at_cmd(self, cmd, resp_len, expect=0, dev_index=1, batch=False):
        para = {"cmd": cmd, "resp_len": int(resp_len)}
        output = self.poseidon_execute.execute_action(para, expect, dev_index, batch)
        return output.get('atRsp') if not batch else None

# -*- coding:utf-8 -*-
import poseidon_module.core.logger as log
from poseidon_module.core.decorators import PoseidonExecute, ActionType, LogActionMeta
from poseidon_module.action.server_id import ServerID
from poseidon_module.action.single.single_action_id import SingleAtDmLogID


class SingleLog(metaclass=LogActionMeta):
    def __init__(self):
        self.log = log.get_system_logger()
        self.poseidon_execute = PoseidonExecute(ServerID.AT_DM_LOG_SERVER, ActionType.SINGLE_ACTION, SingleAtDmLogID)

    def action_fibo_log_init(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_log_deinit(self, expect=0, dev_index=1, batch=False):
        self.poseidon_execute.execute_action(None, expect, dev_index, batch)

    def action_fibo_log_set_level(self, level, expect=0, dev_index=1, batch=False):
        para = {"level": int(level)}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_log_config_info_modify(self, log_config, expect=0, dev_index=1, batch=False):
        default_config = {"syslog_size": 1, "syslog_numbers": 1, "syslog_dir": "syslog_dir"}
        assert isinstance(log_config, dict) or log_config is None, "参数类型错误！"
        if log_config is not None:
            default_config.update(log_config)
        else:
            default_config = None
        para = {"log_config": default_config}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

    def action_fibo_log_config_info_get(self, expect=0, dev_index=1, batch=False):
        output = self.poseidon_execute.execute_action(None, expect, dev_index, batch)
        return output.get('handle') if not batch else None

    def action_fibo_write_Log(self, log_level, log_count, log_tag, expect=0, dev_index=1, batch=False):
        para = {"log_level": int(log_level), "log_count": int(log_count), "log_tag": log_tag}
        self.poseidon_execute.execute_action(para, expect, dev_index, batch)

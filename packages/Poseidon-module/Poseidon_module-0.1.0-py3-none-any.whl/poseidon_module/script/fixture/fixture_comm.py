# -*- coding: utf-8 -*-
from poseidon_module.__export__ import *


@pytest.fixture()
def cmw500_fixture(request):
    gl.gl["G_INSTR_NAME"] = 0
    u_inst.lc_inst_init(gl.gl)
    yield
    u_inst.lc_inst_deinit()


@pytest.fixture()
def uxm_fixture(request):
    gl.gl["G_INSTR_NAME"] = 1
    u_inst.lc_inst_init(gl.gl)
    yield
    u_inst.lc_inst_deinit()


@pytest.fixture()
def powersupply_fixture(request):
    gl.gl["G_INSTR_NAME"] = 4
    u_inst.lc_inst_init(gl.gl)
    yield
    u_inst.lc_inst_deinit()


@pytest.fixture()
def cpu_fixture(request):
    """ cpu 初始化和 teardown 动作 """
    cpu_params = request.param
    ret, pid = u_shell.lc_start_cpu_ocupy(cpu_params[0], cpu_params[1])
    assert ret, "开启cpu占用失败！"
    yield
    if pid != -1:
        u_shell.lc_stop_cpu_ocupy(pid)


@pytest.fixture()
def mem_fixture(request):
    """ mem 占用和还原 """
    mem_params = request.param
    ret, pid = u_shell.lc_start_mem_ocupy(mem_params[0])
    assert ret, "设置内存占用失败！"
    yield
    if pid != -1:
        u_shell.lc_stop_mem_ocupy(pid)


@pytest.fixture()
def reset_box(request):
    """ 测试完成后打开屏蔽箱 """
    logger.debug("屏蔽箱相关测试用例")
    yield
    assert u_serial.lc_serial_control_shielding_box(gl.gl["G_BOX_PORT"], 0), "开屏蔽箱失败！"
    time.sleep(5)

# -*- coding: utf-8 -*-
from poseidon_module.__export__ import *


@pytest.fixture()
def case_setup1(request):
    """打印包含用例编号的开始和结束信息，模块排序和还原"""
    marks = [i.name for i in request.node.own_markers]
    if not u_comm.lc_reorder_device_info_lst_by_tag(marks):
        pytest.skip("未匹配到可测试环境！")
    gl.test_result["setup_done"] = True  # 测试正式开始，会执行对应 teardown 动作
    yield
    u_comm.lc_restore_device_info_lst()
    if gl.gl["G_EVN_TYPE"] != 2:
        time.sleep(gl.gl["G_EXEC_INTERVAL"])  # 用例执行最小间隔
    if "VOICE" in marks or "SMS" in marks:
        time.sleep(30)  # 语音短信相关脚本均间隔 30 秒执行


def __case_end(mode=0):
    if mode == 0:
        logger.debug(
            f'============================== CASE {gl.cur_case_name} END ==============================')
    with open(f"{LogPath}/output/test_report_simple.json", "a", encoding="utf-8") as fd:
        fd.write(
            f'{{"case_num": "{gl.cur_case_name}", "result": "{gl.test_result["result"]}","info": "{gl.test_result["info"]}"}},\n')


@pytest.fixture()
def module_log_fix(request, case_setup1):
    """ 给日志打标志，并抓取日志 """
    marks = [i.name for i in request.node.own_markers]
    try:
        u_env.lc_log_setup(gl.cur_case_name)
        u_env.lc_send_log_tag(marks, f"START_{gl.cur_case_name}")
        yield
    except Exception as e:
        logger.error(e)
    __case_end()

    u_env.lc_check_poseidon_state(marks)
    u_env.lc_send_log_tag(marks, f"END_{gl.cur_case_name}")
    pkg_log = True if gl.test_result["result"] == "FAILED" else False
    u_env.lc_get_modem_logs(marks, gl.cur_case_name, pkg_log)


@pytest.fixture(autouse=True)
def case_setup2(request, module_log_fix):
    """特殊前置条件的执行和还原"""
    marks = [i.name for i in request.node.own_markers]
    pass

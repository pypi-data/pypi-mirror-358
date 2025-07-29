# -*- coding: utf-8 -*-
import os
import threading
from py.xml import html
from datetime import datetime
import shutil
from configparser import ConfigParser
from poseidon_module.__export__ import *
from poseidon_module.utils.dingtalk import UtilDd

start_time = datetime.now().strftime('%m%d%H%M%S')


# html 插件管理
def poseidon_html_report_title(report):
    report.title = "Poseidon Report"


def poseidon_html_results_table_html(report, data):
    if report.passed or report.skipped:
        del data[:]


def poseidon_html_results_table_header(cells):
    cells.insert(0, html.td("Case Num"))
    cells.pop()


def poseidon_html_results_table_row(report, cells):
    case_num = report.nodeid.split("::")[-1].replace('test_', '')
    del_index = case_num.find("[")
    if del_index > 0:
        case_num = case_num[:del_index]
    cells.insert(0, html.td(case_num))
    cells.pop()


def __compare_time(time1, time2):
    """ 比较日志时间和开始测试开始时间 """
    try:
        time_array1 = time.strptime(f"2024{time1}", '%Y%m%d%H%M%S')
        timestamp1 = time.mktime(time_array1)
        time_array2 = time.strptime(f"2024{time2}", '%Y%m%d%H%M%S')
        timestamp2 = time.mktime(time_array2)
        return timestamp1 <= timestamp2
    except Exception as e:
        print(e)
        return False


def allot_task(a_time, ini_path):
    """ 分发测试日志分析任务到个人 """
    config_ini = ConfigParser()
    config_ini.read(f"{ini_path}/auto_run.ini", encoding="utf-8")
    if os.path.exists(rf"{LogPath}/case_logs/FAIL"):
        for dir_name in os.listdir(rf"{LogPath}/case_logs/FAIL"):
            req_name = "_".join(dir_name.split("_")[3:-3])
            log_time = dir_name.split("_")[0]
            for p_name in ["WW", "WL", "WX", "HX", "JL"]:
                if req_name in config_ini.get("REQMAP", p_name):
                    if __compare_time(a_time, log_time):
                        target_path = f"{LogPath}/analyse_log/{a_time}/{p_name}/{dir_name}"
                        try:
                            shutil.copytree(f"{LogPath}/case_logs/FAIL/{dir_name}", target_path)
                        except Exception as e:
                            print(e)
    try:
        shutil.copytree(f"{LogPath}/output", f"{LogPath}/analyse_log/{a_time}/{a_time}_output")
    except Exception as e:
        print(e)
    try:
        shutil.copy(f"{ini_path}/pytest.ini", f"{LogPath}/analyse_log/{a_time}/{a_time}_pytest.ini")
    except Exception as e:
        print(e)
    try:
        shutil.copy(f"{ini_path}/config.py", f"{LogPath}/analyse_log/{a_time}/{a_time}_config.py")
    except Exception as e:
        print(e)


def poseidon_configure(config):
    """ 第一步，操作 pytest 框架配置 """
    # 修改 html 文件路径
    config.option.htmlpath = f"{LogPath}/output/test_report.html"
    # 修改json 文件路径
    config.option.json_path = f"{LogPath}/output/test_report.json"


def poseidon_collection_modifyitems(session, config, items):
    """ 第三步：收集测试用例，根据 ini 文件顺序执行用例 """
    gl.gl["total_case"] = len(items)
    gl.gl["passed"] = 0
    gl.gl["failed"] = 0
    gl.gl["skipped"] = 0
    if "*" not in config.inicfg["python_functions"]:
        order_list = config.inicfg["python_functions"].split("\n")
        order_dict = {value: idx for idx, value in enumerate(order_list)}
        items.sort(key=lambda x: order_dict[x.name.split("[")[0]])
    for item in items:
        if re.findall("_LT_|_PR_|_PF_", item.name) and gl.gl["G_RERUNS"] > 0:
            item.add_marker(pytest.mark.flaky(reruns=gl.gl["G_RERUNS"], reruns_delay=10))


def poseidon_sessionstart(session):
    """ 第二步，测试开始时的操作 """
    gl.set_global_value("Script_Gl", gl.gl)
    gl.gl["lt_pr_report"] = {"target_total": 1, "reruns": 0, "round": 0, "grand_total": 0,
                             "highest_total": 0, "cur_total": 0, "fail_time": ""}
    gl.gl["sessionstart"] = True
    if gl.gl.get("G_MONITOR_FLAG"):
        client = TCPClient(gl.gl["G_EVN_NUM"], 'MODULE_INFO1["model_id"]', gl.gl["G_EVN_REMOTE_ID"])
        gl.gl["monitor_cli"] = client
        th = threading.Thread(target=client.connect_tcp_server,
                              args=(gl.gl["G_MONITOR_SERVER_IP"], gl.gl["G_MONITOR_SERVER_PORT"]),
                              daemon=True)
        th.start()
    if gl.gl.get("G_DD_FLAG"):
        dd_client = UtilDd(gl.gl["G_DINGTALK_BOT_TOKEN"], gl.gl["G_DINGTALK_BOT_SECRET"])
        gl.gl["dd_cli"] = dd_client
        dd_client.lc_get_case_map(gl)
        th = threading.Thread(target=dd_client.lc_send_dd_test_report, args=(gl,), daemon=True)
        th.start()
    logger.debug(f"******************************* {session.fspath} *******************************")
    logger.debug("开始绑定模组环境信息")
    u_env.lc_bind_devices_info(gl.gl)
    logger.debug("模组环境信息绑定完成")
    if not os.path.exists(f"{LogPath}/output"):
        os.makedirs(f"{LogPath}/output")
    with open(f"{LogPath}/output/test_report_simple.json", "w", encoding="utf-8") as fd1:
        fd1.write("[\n")
    for i, dev_id in enumerate(gl.gl["G_DEV_IDS"]):
        index = i + 1
        logger.debug(f"开始初始化 {dev_id} 设备")
        ret = u_env.lc_setup_test_env(start_app=True, check_info=False, dev_index=index)
        assert ret, f"设备 {dev_id} 环境初始化失败！"


def poseidon_sessionfinish(session, exitstatus):
    """ 所有测试完成时的操作 """
    logger.debug(f"测试结束")
    with open(f"{LogPath}/output/test_report_simple.json", "a", encoding="utf-8") as fd2:
        fd2.write("{}]\n")
    allot_task(start_time, session.fspath)
    if gl.gl["G_DD_FLAG"]:
        gl.gl["dd_cli"].lc_send_end_log(gl)
    gl.gl["sessionstart"] = False


def __set_log_name(item):
    cur_time = datetime.now().strftime('%m%d%H%M%S')
    log_name = item.name.replace("test_", f"{cur_time}_")
    del_index = log_name.find("[")
    if del_index > 0:
        log_name = log_name[:del_index]
    return log_name


def poseidon_runtest_setup(item):
    """ 每个用例开始时的操作 """
    gl.test_result = {}
    if gl.gl.get("marks") is not None:
        del gl.gl["marks"]
    if gl.gl.get("fixture_names") is not None:
        del gl.gl["fixture_names"]
    gl.gl["marks"] = [i.name for i in item.own_markers]
    gl.gl["fixture_names"] = item.fixturenames
    # 打印用例开始执行日志
    gl.cur_case_name = __set_log_name(item)
    logger.debug(f'============================= CASE {gl.cur_case_name} START =============================')
    logger.debug(f'++++ 用例 [{item.name}] 测试执行阶段 [setup] start ++++')


def __case_end(mode=0):
    if mode == 0:
        logger.debug(
            f'============================== CASE {gl.cur_case_name} END ==============================')
    with open(f"{LogPath}/output/test_report_simple.json", "a", encoding="utf-8") as fd:
        fd.write(
            f'{{"case_num": "{gl.cur_case_name}", "result": "{gl.test_result["result"]}","info": "{gl.test_result["info"]}"}},\n')


def poseidon_runtest_call(item):
    if not gl.gl["G_TEARDOWN_FLAG"]:
        pytest.exit("保留测试环境,跳过 teardown")


def poseidon_runtest_teardown(item):
    """ 每个测试用例完成后的操作，与业务无关操作 """
    logger.debug(f'++++ 用例 [{item.name}] 测试执行阶段 [teardown] start ++++')
    if gl.gl["G_DD_FLAG"]:
        logger.info("错误信息发送到钉钉")
        if gl.test_result["result"] == "FAILED":
            gl.gl["dd_cli"].lc_send_fail_log(gl)
    if gl.test_result["result"] == "PASSED":
        gl.gl["passed"] += 1
    if gl.test_result["result"] == "FAILED":
        gl.gl["failed"] += 1
    if gl.test_result["result"] == "SKIPPED":
        gl.gl["skipped"] += 1
    if gl.test_result.get("setup_done") is None:  # 直接执行结束
        u_comm.lc_restore_device_info_lst()
        __case_end(1)  # 测试还原第三步：收集测试用例执行简报


def poseidon_runtest_makereport(output, item, call):
    report = output.get_result()
    logger.debug(f'++++ 用例 [{item.name}] 测试执行阶段 [{report.when}] end ++++')
    gl.test_result["when"] = report.when
    item.rep_call = report
    if report.outcome == "failed":
        gl.test_result["result"] = "FAILED"
        # 主动抛出异常
        result1 = re.findall(r"(PoseidonError:\s+.*?)\n", report.longreprtext, re.S)
        # 断言异常
        result2 = re.findall(r"(AssertionError:\s+.*?\n\s+assert.*?)\n", report.longreprtext, re.S)
        if result1:
            gl.test_result["info"] = result1[0]
        elif result2:
            gl.test_result["info"] = result2[0].replace("\n", " ")
        else:
            # 其它异常
            result3 = re.findall(r"(\w+Error:\s+.*?)\n", report.longreprtext, re.S)
            if result3:
                gl.test_result["info"] = result3[0]
            else:
                gl.test_result["info"] = ""
    elif report.outcome == "skipped":
        gl.cur_case_name = __set_log_name(item)
        gl.test_result["result"] = "SKIPPED"
        result = re.findall(r"ExceptionInfo\s+(\w+)", str(call.excinfo))
        if result:
            gl.test_result["info"] = result[0]
        else:
            gl.test_result["info"] = ""
    else:
        gl.test_result["result"] = "PASSED"
        gl.test_result["info"] = call.excinfo

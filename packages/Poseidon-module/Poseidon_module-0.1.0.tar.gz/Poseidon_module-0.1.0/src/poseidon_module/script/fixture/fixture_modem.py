# -*- coding: utf-8 -*-
from poseidon_module.__export__ import *


def scene_setup(request_node, name):
    marks = [i.name for i in request_node.own_markers]
    module_num, slot_list = u_comm.lc_get_slot_id_list(marks)
    assert module_num, "模块标签或SIM卡标签异常！"
    for dev in range(1, module_num + 1):
        if name.lower() == "sim":
            scene_sim.action_scene_sim_setup(dev_index=dev)
        elif name.lower() == "nw":
            scene_nw.action_scene_nw_setup(dev_index=dev)
        elif name.lower() == "dm":
            scene_dm.action_scene_dm_setup(dev_index=dev)
        elif name.lower() == "gnss":
            scene_gnss.action_scene_gps_setup(dev_index=dev)
        elif name.lower() == "voice":
            scene_voice.action_scene_voice_setup(dev_index=dev)
        elif name.lower() == "sms":
            scene_sms.action_scene_sms_setup(dev_index=dev)
        elif name.lower() == "data":
            scene_data.action_scene_data_setup(dev_index=dev)
        else:
            raise PoseidonError("场景名称错误！")


def scene_teardown(request_node, name):
    marks = [i.name for i in request_node.own_markers]
    module_num, slot_list = u_comm.lc_get_slot_id_list(marks)
    assert module_num, "模块标签或SIM卡标签异常！"
    for dev in range(1, module_num + 1):
        if name.lower() == "sim":
            scene_sim.action_scene_sim_teardown(dev_index=dev)
        elif name.lower() == "nw":
            scene_nw.action_scene_nw_teardown(dev_index=dev)
        elif name.lower() == "dm":
            scene_dm.action_scene_dm_teardown(dev_index=dev)
        elif name.lower() == "gnss":
            scene_gnss.action_scene_gps_teardown(dev_index=dev)
        elif name.lower() == "sms":
            scene_sms.action_scene_sms_teardown(dev_index=dev)
        elif name.lower() == "voice":
            scene_voice.action_scene_voice_teardown(dev_index=dev)
        elif name.lower() == "data":
            scene_data.action_scene_data_teardown(dev_index=dev)
        else:
            return False
    return True


@pytest.fixture()
def reset_auto(request):
    """ nw 初始化和teardown 动作 """
    marks = [i.name for i in request.node.own_markers]
    yield
    module_num, slot_list = u_comm.lc_get_slot_id_list(marks)
    for dev in range(1, module_num + 1):
        for slot in slot_list[dev - 1]:
            scene_nw.action_scene_nw_set_pref_mode(slot, "AUTO", dev_index=dev)


@pytest.fixture()
def nw_fixture(request):
    """ nw 初始化和teardown 动作 """
    scene_setup(request.node, "nw")
    yield
    scene_teardown(request.node, "nw")


@pytest.fixture()
def data_fixture(request):
    """ data 初始化和teardown 动作 """
    scene_setup(request.node, "data")
    yield
    scene_teardown(request.node, "data")


@pytest.fixture()
def sim_fixture(request):
    """ sim 初始化和teardown 动作 """
    scene_setup(request.node, "sim")
    yield
    scene_teardown(request.node, "sim")


@pytest.fixture()
def sms_fixture(request):
    """ sms 初始化和teardown 动作 """
    scene_setup(request.node, "sms")
    yield
    scene_teardown(request.node, "sms")


@pytest.fixture()
def dm_fixture(request):
    """ dm 初始化和teardown 动作 """
    scene_setup(request.node, "dm")
    yield
    scene_teardown(request.node, "dm")


@pytest.fixture()
def gnss_fixture(request):
    """ gnss 初始化和teardown 动作 """
    scene_setup(request.node, "gnss")
    yield
    scene_teardown(request.node, "gnss")


@pytest.fixture()
def voice_fixture(request):
    """ voice 初始化和teardown 动作 """
    scene_setup(request.node, "voice")
    yield
    scene_teardown(request.node, "voice")


@pytest.fixture()
def reset_voice_state(request):
    """ 恢复voice end动作 """
    marks = [i.name for i in request.node.own_markers]
    module_num, slot_list = u_comm.lc_get_slot_id_list(marks)
    assert module_num, "模块标签或SIM卡标签异常！"
    yield
    for dev in range(1, module_num + 1):
        single_voice.action_fibo_voice_end_all_call(dev_index=dev)


@pytest.fixture()
def reset_ims(request):
    """ 恢复ims动作 """
    marks = [i.name for i in request.node.own_markers]
    module_num, slot_list = u_comm.lc_get_slot_id_list(marks)
    assert module_num, "模块标签或SIM卡标签异常！"
    yield
    for dev in range(1, module_num + 1):
        scene_dm.action_scene_ims_enable(dev_index=dev)


@pytest.fixture()
def reset_centric(request):
    """ 恢复语音中心动作 """
    marks = [i.name for i in request.node.own_markers]
    yield
    module_num, slot_list = u_comm.lc_get_slot_id_list(marks)
    for dev in range(1, module_num + 1):
        for slot in slot_list[dev - 1]:
            single_nw.action_fibo_nw_bind_subscription(slot, dev_index=dev)
            single_nw.action_fibo_nw_set_centric(0, dev_index=dev)


@pytest.fixture()
def reset_sms_center(request):
    """ 恢复短信中心号码动作 """
    yield
    center_address_info = gl.gl.get("center_address_info")
    if center_address_info is not None:
        center_cfg = {"addr": center_address_info["addr"]}
        single_sms.action_fibo_sms_bind_subscription(center_address_info["slot_id"])
        single_sms.action_fibo_sms_set_sms_center_address(center_cfg)
        del gl.gl["center_address_info"]


@pytest.fixture()
def reset_http_server(request):
    """ 恢复 http 连接为断开状态 """
    yield
    client_id = gl.gl.get("http_client_id")
    if client_id is not None:
        u_http.lc_http_close_client_socket(client_id)
        del gl.gl["http_client_id"]


@pytest.fixture()
def reset_fplmn(request):
    """ 恢复 http 连接为断开状态 """
    yield
    for slot_id in range(1, 3):
        default_forbidden_plmn = gl.gl.get(f"default_forbidden_plmn_{slot_id}")
        if default_forbidden_plmn is not None:
            single_nw.action_fibo_nw_bind_subscription(slot_id)
            single_nw.action_fibo_nw_set_forbidden_networks(len(default_forbidden_plmn), default_forbidden_plmn)
            del gl.gl[f"default_forbidden_plmn_{slot_id}"]


@pytest.fixture()
def reset_flight(request):
    """ 恢复飞行模式 """
    yield
    scene_dm.action_scene_flight_mode_off()


@pytest.fixture()
def reset_loc_ind():
    """ 测试完成后设置set ind mask为全部开启"""
    logger.debug("设置定位信息源相关测试！")
    source = single_gnss.action_fibo_loc_get_location_information_source()
    if source != 6:
        single_gnss.action_fibo_loc_set_location_information_source(6)
        assert scene_comm.lc_modem_reboot(), "reboot重启失败！"
        single_gnss.action_fibo_loc_client_init()
    yield
    single_gnss.action_fibo_loc_set_nmea_ind_mask(0x3FFFFF)

# -*- coding:utf-8 -*-
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import threading

import poseidon_module.core.logger as log
from poseidon_module.utils.comm import UtilComm
from poseidon_module.core.decorators import LogFunMeta
from poseidon_module.action.scene.scene_nw import SceneNw
from poseidon_module.action.scene.scene_data import SceneData
from poseidon_module.action.scene.scene_sms import SceneSms
from poseidon_module.action.scene.scene_voice import SceneVoice
from poseidon_module.utils.shell import UtilShell
from poseidon_module.core.globals import Globals as gl


class FunCheck(metaclass=LogFunMeta):

    def __init__(self):
        self.log = log.get_system_logger()
        self.u_comm = UtilComm()
        self.shell = UtilShell()
        self.sc_nw = SceneNw()
        self.sc_data = SceneData()
        self.sc_sms = SceneSms()
        self.sc_voice = SceneVoice()
        self.data_checked_event = threading.Event()
        self.reg_success_event = threading.Event()
        self.check_data = False
        self.cid_list = None
        self.init_ret_dict = None
        self.pref_mode = None
        self.lst = ["VOICE", "SMS", "WIFI", "GNSS", "DATA", "NW", "VLAN", "SIM", "DM", "TZ", "SPI", "UART", "V2X"]
        self.server_list = ["default", "47.111.19.157", "47.110.136.146", "47.110.155.171"]

    def __set_up_all(self, name, dev_index):
        """
        根据接口名称选择要调用的初始化 action
        :param name: "VOICE", "SMS", "WIFI", "GNSS", "DATA", "NW", "SIM", "DM", "TZ"
        :param dev_index:
        :return: 返回 bool
        """
        try:
            assert name in self.lst, "配置问题！不支持该功能测试！"
            if name == "NW" and "nw_fixture" not in gl.gl["fixture_names"]:
                self.sc_nw.action_scene_nw_setup(dev_index=dev_index)
            if name == "DATA" and "data_fixture" not in gl.gl["fixture_names"]:
                self.sc_data.action_scene_data_setup(dev_index=dev_index)
            if name == "SMS" and "sms_fixture" not in gl.gl["fixture_names"]:
                self.sc_sms.action_scene_sms_setup(dev_index=dev_index)
            if name == "VOICE" and "voice_fixture" not in gl.gl["fixture_names"]:
                self.sc_voice.action_scene_voice_setup(dev_index=dev_index)
        except Exception as e:
            self.log.error(e)
            return False
        return True

    def set_up_all(self, check_dic, timeout=180, dev_index=1):
        """
        初始化要进行功能检查的接口
        :param dev_index:
        :param check_dic: 测试项字典
        :param timeout: 检测超时时间
        :return: 返回 初始化字典信息 e.g.{"DATA":[1,2], "GNSS":[]}
        """
        ret_dic = {}
        with ThreadPoolExecutor(max_workers=10) as pool:
            th_dic = {}
            for k, v in check_dic.items():
                if v == 1:
                    th = pool.submit(self.__set_up_all, k, dev_index)
                    th_dic[k] = th
            wait(list(th_dic.values()), timeout, return_when=ALL_COMPLETED)
            for r_k, r_v in th_dic.items():
                ret_dic[r_k] = r_v.result()
        self.init_ret_dict = ret_dic

    def __teardown_all(self, name, dev_index):
        try:
            assert name in self.lst, "配置问题！不支持该功能测试！"
            if name == "NW" and "nw_fixture" not in gl.gl["fixture_names"]:
                self.sc_nw.action_scene_nw_teardown(dev_index=dev_index)
            if name == "DATA" and "data_fixture" not in gl.gl["fixture_names"]:
                self.sc_data.action_scene_data_teardown(dev_index=dev_index)
            if name == "SMS" and "sms_fixture" not in gl.gl["fixture_names"]:
                self.sc_sms.action_scene_sms_teardown(dev_index=dev_index)
            if name == "VOICE" and "voice_fixture" not in gl.gl["fixture_names"]:
                self.sc_voice.action_scene_voice_teardown(dev_index=dev_index)
        except Exception as e:
            self.log.error(e)
            return False
        return True

    def teardown_all(self, check_dic, timeout=180, dev_index=1):
        """
        去初始化要进行功能检查的接口
        :param dev_index:
        :param check_dic: 测试项字典
        :param timeout: 检测超时时间
        :return: 检查结果
        """
        ret_dic = {}
        with ThreadPoolExecutor(max_workers=10) as pool:
            th_dic = {}
            for k, v in check_dic.items():
                if v == 1:
                    th = pool.submit(self.__teardown_all, k, dev_index)
                    th_dic[k] = th
            wait(list(th_dic.values()), timeout, return_when=ALL_COMPLETED)
            for r_k, r_v in th_dic.items():
                ret_dic[r_k] = r_v.result()
        return ret_dic

    def lc_check_nw_function(self, slot_list, dev_index=1):
        try:
            assert self.init_ret_dict.get("NW"), "NW 未初始化成功！"
            for slot_id in slot_list:
                self.sc_nw.action_scene_nw_set_pref_mode(slot_id, self.pref_mode, dev_index=dev_index)
            self.reg_success_event.set()  # 上报驻网成功事件
        except  Exception as e:
            self.log.error(e)
            return False
        return True

    def lc_check_data_function(self, slot_list, dev_index=1):
        result = True
        cid_dict = {1: [], 2: []}
        try:
            self.reg_success_event.wait(timeout=60)  # 等待上报驻网成功事件
            assert self.reg_success_event.is_set(), "驻网失败！跳过 DATA 测试！"
            assert self.init_ret_dict.get("DATA"), "DATA 未初始化成功！"
            for slot_id in slot_list:
                for i in range(2):
                    profile_id = slot_id + i if slot_id == 1 else slot_id + i + 1
                    apn_info = {"profile_id": profile_id, "apn_name": f"TestApn{profile_id}"}
                    ret = self.sc_data.action_scene_async_data_call(slot_id, apn_info, dev_index)
                    cid_dict[slot_id].append(ret["call_id"])
            self.data_checked_event.set()  # 上报数据拨号完成事件
            for slot_id in slot_list:
                for i in range(2):
                    index = i if slot_id == 1 else i + slot_id
                    ip = self.server_list[index]
                    info = self.sc_data.action_scene_add_route_and_dns(slot_id, cid_dict[slot_id][i], ip, dev_index)
                    target_ip = "www.baidu.com" if ip == "default" else ip
                    ret = self.shell.lc_ping_test(target_ip, info["iface_name"], dev_index=dev_index)
                    assert ret, f"ping {target_ip}失败！"
        except  Exception as e:
            self.data_checked_event.set()  # 上报数据拨号完成事件
            self.log.error(e)
            result = False
        for slot_id in slot_list:
            self.sc_data.action_scene_data_multi_data_call_stop(1, cid_dict[slot_id], dev_index)
        return result

    def lc_check_voice_function(self, slot_list, dev_index=1):
        if self.check_data:
            self.data_checked_event.wait()  # 等待数据拨号完成事件
        try:
            self.reg_success_event.wait(timeout=60)  # 等待上报驻网成功事件
            assert self.reg_success_event.is_set(), "驻网失败！跳过 VOICE 测试！"
            assert self.init_ret_dict.get("VOICE"), "VOICE 未初始化成功！"
            for slot_id in slot_list:
                phone_num = self.u_comm.lc_get_phone_num(slot_id, dev_index)
                ret, _, operator_num = self.u_comm.lc_get_operator_by_phone_num(phone_num)
                assert ret, "获取运营商号码失败！"
                self.sc_voice.action_scene_voice_check_func(slot_id, operator_num, dev_index)
        except  Exception as e:
            self.log.error(e)
            return False
        return True

    def lc_check_sms_function(self, slot_list, dev_index=1):
        try:
            self.reg_success_event.wait(timeout=60)  # 等待上报驻网成功事件
            assert self.reg_success_event.is_set(), "驻网失败！跳过 SMS 测试！"
            assert self.init_ret_dict.get("SMS"), "SMS 未初始化成功！"
            for slot_id in slot_list:
                phone_num = self.u_comm.lc_get_phone_num(slot_id, dev_index)
                self.sc_sms.action_scene_sms_check_fun(slot_id, phone_num, "sms test message", 60, dev_index)
        except  Exception as e:
            self.log.error(e)
            return False
        return True

    def __get_test_result_and_log_it(self, check_dic, count_dic, test_round, ret_dic, s_v_interval, func_name):
        if check_dic.get(func_name) == 1:
            if ret_dic.get(func_name):
                count_dic[func_name] += 1
            if func_name in ["VOICE", "SMS"]:
                test_round = test_round // s_v_interval + 1 if s_v_interval != 1 else test_round
            success_rate = str(round(count_dic[func_name] / test_round * 100, 2)) + "%"
            suc_times = str(count_dic[func_name])
            test_round = str(test_round)
            s = f'{func_name.ljust(6)} 测试总次数{test_round.ljust(4)}，成功次数 {suc_times.ljust(6)}, 成功率 {success_rate}'
            self.log.info(s)

    def statistic_test_result(self, test_round, check_dic, ret_dic, s_v_interval, count_dic):
        """ 测试结果统计 """
        if count_dic is None:
            count_dic = {}.fromkeys(self.lst, 0)
        self.log.info(f"第 {test_round} 轮功能检查结果统计".center(52, "*"))
        for func_name in self.lst:
            self.__get_test_result_and_log_it(check_dic, count_dic, test_round, ret_dic, s_v_interval, func_name)
        self.log.info("*" * 60)
        return count_dic

    def __check(self, name, slot_list):
        """
        根据名称检查对应功能
        :param name:
        :return:
        """
        ret = False
        try:
            if name == "NW":
                ret = self.lc_check_nw_function(slot_list, 1)
            elif name == "DATA":
                ret = self.lc_check_data_function(slot_list, 1)
            elif name == "VOICE":
                ret = self.lc_check_voice_function(slot_list, 1)
            elif name == "SMS":
                ret = self.lc_check_sms_function(slot_list, 1)
            else:
                raise Exception(f"不支持 {name} 功能检查！")
        except Exception as e:
            self.log.error(e)
        return ret

    def __set_class_para(self):
        if self.data_checked_event.is_set():
            self.data_checked_event.clear()
        if self.reg_success_event.is_set():
            self.reg_success_event.clear()
        self.check_data = False
        self.cid_list = []

    @staticmethod
    def __should_check(k, test_round, interval):
        return not (k in ["VOICE", "SMS"] and test_round % interval != 0 and test_round != 1)

    def check_main_fun(self, check_item, slot_id=1, test_round=1, interval=1, pref_mode="AUTO", check_mode=1,
                       timeout=180):
        """功能检查函数"""
        check_dic = {check_item: 1} if isinstance(check_item, str) else check_item  # 检查项字典, 格式为 {"VOICE":1, "SMS":1}
        slot_list = [slot_id] if isinstance(slot_id, int) else slot_id  # 待检查的槽位列表
        check_dic["NW"] = 1  # modem 必须要检查 NW 功能
        self.pref_mode = pref_mode
        self.__set_class_para()
        self.check_data = True if check_dic.get("DATA") == 1 else False
        self.set_up_all(check_dic)
        if check_mode == 0:  # 串行模式
            ret_dic = {k: self.__check(k, slot_list)
                       for k, v in check_dic.items() if v == 1 and self.__should_check(k, test_round, interval)}
        else:  # 并行模式
            with ThreadPoolExecutor(max_workers=len(self.lst) + 1) as pool:
                futures = {k: pool.submit(self.__check, k, slot_list)
                           for k, v in check_dic.items() if v == 1 and self.__should_check(k, test_round, interval)}
                wait(futures.values(), timeout, return_when=ALL_COMPLETED)
                ret_dic = {k: f.result() for k, f in futures.items()}
        self.teardown_all(check_dic)
        self.__set_class_para()
        return ret_dic

# -*- coding:utf-8 -*-
import itertools
import re

from poseidon_module.core.decorators import SingletonMeta
from poseidon_module.core.globals import Globals
from poseidon_module.core.logger import sys_log


def get_operator_by_phone_num(phone_num):
    """
    根据电话号码查询对应的运营商和运营商电话
    :param phone_num:
    :return: True/False, operator, operator_num
    """
    ct_list = [133, 141, 149, 153, 173, 177, 180, 181, 189, 190, 191, 193, 199]
    cmcc_list = [134, 135, 136, 137, 138, 139, 144, 147, 148, 150, 151, 152, 157, 158, 159, 172, 178, 182, 183, 184,
                 187, 188, 195, 197, 198]
    cu_list = [130, 131, 132, 145, 146, 155, 156, 166, 175, 176, 185, 186, 196]
    if len(phone_num) < 11:
        sys_log.error(f"[{phone_num}]非11位手机号码，请检查SIM卡！")
        return False, "", ""
    id_num = str(phone_num)[-11:-8]
    if int(id_num) in ct_list:
        return True, "CT", "10000"
    elif int(id_num) in cmcc_list:
        return True, "CMCC", "10086"
    elif int(id_num) in cu_list:
        return True, "CU", "10010"
    else:
        sys_log.error("非3大运营商号码，请检查SIM卡！")
        return False, "", ""


class Reorder(metaclass=SingletonMeta):
    def __init__(self):
        self.bind_info = []
        self.relay_set = {"R0", "R1", "R2", "R3", "R4", "R5", "R6"}
        self.marks = []

    @staticmethod
    def __get_target_module_info(cur_app_lst, slot_id, operator, tmp_list, module_id):
        """
        根据卡槽号和运营商信息获取对应电话信息的模组绑定信息
        :param cur_app_lst: 模组绑定信息
        :param slot_id: 卡槽号
        :param operator: 运营商信息
        :param tmp_list: []
        :return: tmp_list
        """
        for j in cur_app_lst:
            if j["phone_num"] is None:
                sys_log.warning("未配置任何电话号码信息！")
                break
            if not isinstance(j["phone_num"], list):
                sys_log.warning("请配置电话号码信息为二维数组N*2！e.g. [['13025468963', None]]")
                break
            if len(j["phone_num"]) != 2:
                sys_log.warning("请配置电话号码信息为二维数组N*2！e.g. [['13025468963', None]]")
                break
            phone_num1 = j["phone_num"][0]
            phone_num2 = j["phone_num"][1]
            if slot_id == 0:
                if phone_num1 is None and phone_num2 is None:
                    cur_app_lst.remove(j)
                    tmp_list[module_id] = j
                    break
            elif slot_id == 1:
                if isinstance(phone_num1, str):
                    operator1 = get_operator_by_phone_num(phone_num1)[1]
                    if "CA" == operator or operator == operator1:
                        cur_app_lst.remove(j)
                        tmp_list[module_id] = j
                        break
            elif slot_id == 2:
                if isinstance(phone_num2, str):
                    operator2 = get_operator_by_phone_num(phone_num2)[1]
                    if "CA" == operator or operator == operator2:
                        cur_app_lst.remove(j)
                        tmp_list[module_id] = j
                        break
            else:
                if isinstance(phone_num1, str) and isinstance(phone_num2, str):
                    operator1 = get_operator_by_phone_num(phone_num1)[1]
                    operator2 = get_operator_by_phone_num(phone_num2)[1]
                    check_operator = operator.split("0")
                    if len(check_operator) == 1:  # 双卡单运营商标签，默认只检查SIM1运营商
                        if check_operator[0] == operator1 or check_operator[0] == "CA":
                            cur_app_lst.remove(j)
                            tmp_list[module_id] = j
                            break
                    if "CA" in check_operator:  # 双卡单运营商标签，设置1张卡的运营商名称
                        if check_operator[0] == operator1 or check_operator[1] == operator2:
                            cur_app_lst.remove(j)
                            tmp_list[module_id] = j
                            break
                    else:  # 双卡单运营商标签，设置两张卡的运营商名称
                        if check_operator[0] == operator1 and check_operator[1] == operator2:
                            cur_app_lst.remove(j)
                            tmp_list[module_id] = j
                            break

    @staticmethod
    def __sort_key(item):
        index, slot, opr = item
        contains_ca = 'CA' in opr
        is_ca = opr == 'CA'
        tmp_slot = 12 - int(slot.replace("SIM", ""))
        return contains_ca, is_ca, tmp_slot, index

    def __get_slot_operator_list(self, tags):
        slot_set = {"SIM0", "SIM1", "SIM2", "SIM12"}
        opr_list = ["CT", "CU", "CMCC", "CA"]
        tmp_list1 = []
        for i in list(itertools.product(opr_list, ["0"], opr_list)):
            tmp_list1.append("".join(list(i)))
        opr_set = set(tmp_list1 + opr_list)
        opr_tags = [tag for tag in tags if set(tag.split("_")) & opr_set]
        slot_tags = [tag for tag in tags if set(tag.split("_")) & slot_set]
        result = [tag for tag in tags if re.findall(r"^M\d", tag)]
        assert result
        module_num = int(result[0][-1])
        index_list = list(range(module_num))
        if not opr_tags and not slot_tags:
            return [], []
        opr_tags = ["CA" for _ in range(module_num)] if not opr_tags else opr_tags[0].split("_")
        slot_tags = ["SIM1" for _ in range(module_num)] if not slot_tags else slot_tags[0].split("_")
        old_list = []
        for slot_tag, opr_tag, module_id in zip(slot_tags, opr_tags, index_list):
            old_list.append([module_id, slot_tag, opr_tag])
        new_list = sorted(old_list, key=self.__sort_key)
        return new_list, old_list

    @staticmethod
    def __print_cur_device_list(app_info_list):
        tmp_list = [{i["dev_id"]: i["phone_num"]} for i in app_info_list]
        sys_log.info(f"当前的设备顺序为：{tmp_list}")

    def reorder_device_info_lst_by_tag(self, tags):
        """ 根据 tag 调整模块顺序 """
        # 保存当前模组配置到全局变量
        poseidon_list_init = Globals.get('PoseidonList')
        self.bind_info = []
        self.bind_info.extend(poseidon_list_init)
        # 获取分别检查 relay 和 sim 的继电器组合
        check_list = self.__get_check_list(tags)
        sorted_sim_list, check_sim_list = self.__get_slot_operator_list(tags)
        sys_log.info(f"当前用例标签为: {tags}")
        copy_list = []
        copy_list.extend(sorted_sim_list)
        if check_list[0][0] is None and not check_sim_list:  # 无继电器和卡标签直接返回
            self.__print_cur_device_list(poseidon_list_init)
            return True
        if check_sim_list:
            copy_list.remove(check_sim_list[0])
        for check_item in check_list:
            poseidon_list1 = []
            poseidon_list2 = []
            poseidon_list1.extend(poseidon_list_init)
            poseidon_list2.extend(poseidon_list_init)
            if check_item[0] is None:  # 无继电器配置，直接对SIM卡进行排序
                ret, reorder_list = self.__reorder_device_info_lst_by_sim(poseidon_list_init, sorted_sim_list)
                if ret:
                    if not reorder_list:
                        self.__print_cur_device_list(reorder_list)
                        return True
                    Globals.set("PoseidonList", reorder_list)
                    self.__print_cur_device_list(reorder_list)
                    return True
                sys_log.error("未匹配到可测试的环境配置！")
                return False
            # 检查 device1 卡是否符合有继电器配置的环境
            if check_sim_list:
                for index, i in enumerate(poseidon_list_init):
                    if i != check_item[0][0]:
                        poseidon_list1[index] = {'phone_num': [None, None]}
                ret1, reorder_list1 = self.__reorder_device_info_lst_by_sim(poseidon_list1, [check_sim_list[0]])
                if reorder_list1:
                    check_re_index = poseidon_list2.index(check_item[0][0])
                    poseidon_list2[check_re_index] = {'phone_num': [None, None]}
                ret2, reorder_list2 = self.__reorder_device_info_lst_by_sim(poseidon_list2, copy_list)
                if ret1 and ret2 and reorder_list1 == check_item[0] and reorder_list1[0] not in reorder_list2:
                    Globals.set("PoseidonList", reorder_list1 + reorder_list2)
                    self.__print_cur_device_list(reorder_list1 + reorder_list2)
                    return True
            else:
                merged_list = [item for sublist in check_item for item in sublist]
                Globals.set("PoseidonList", merged_list)
                self.__print_cur_device_list(merged_list)
                return True
        sys_log.error("未匹配到可测试的环境配置！")
        return False

    def __reorder_device_info_lst_by_sim(self, poseidon_list, sorted_list):
        """ 根据 tag 调整模块顺序 """
        # copy_list = deepcopy(poseidon_list)
        copy_list = []
        copy_list.extend(poseidon_list)
        slot_dic = {"SIM0": 0, "SIM1": 1, "SIM2": 2, "SIM12": 3}
        if not sorted_list:
            return True, []
        reorder_list = [None for _ in range(len(copy_list))]
        for i in sorted_list:
            slot_id = slot_dic.get(i[1])
            self.__get_target_module_info(copy_list, slot_id, i[2], reorder_list, i[0])
        reorder_list = [info for info in reorder_list if info is not None]
        if len(reorder_list) != len(sorted_list):
            return False, reorder_list
        return True, reorder_list

    @staticmethod
    def __get_relay_list(tags):
        """ 获取符合继电器组合的模组配置信息 """
        relay_set = {"R0", "R1", "R2", "R3", "R4", "R5", "R6"}
        poseidon_list = Globals.get('PoseidonList')
        bind_relay_list = []
        for poseidon_info in poseidon_list:
            tmp_re_list = []
            for index, relay in enumerate(poseidon_info["relay_info"][0]):
                result = re.findall("com(\d+)", relay, re.I)
                assert result, "未匹配到端口号！"
                if int(result[0]) != 0:
                    tmp_re_list.append(f"R{index}")
            sorted_list = sorted(tmp_re_list)
            bind_relay_list.append(sorted_list)
        re_tags = sorted(list(set(tags) & relay_set))
        # 无继电器标签
        if not re_tags:
            return []
        # 有继电器标签
        match_relay_info = []
        for index, dev_re in enumerate(bind_relay_list):
            if set(re_tags).issubset(set(dev_re)):
                match_relay_info.append(poseidon_list[index])
        return match_relay_info

    def __get_check_list(self, tags):
        """ 获取分别检查 relay 和 sim 的继电器组合 """
        poseidon_list = Globals.get('PoseidonList')
        match_relay_info = self.__get_relay_list(tags)
        if not match_relay_info:
            return [[None, poseidon_list]]
        check_list = []
        for index, info in enumerate(match_relay_info):
            copy_poseidon = []
            copy_poseidon.extend(poseidon_list)
            # copy_poseidon = deepcopy(poseidon_list)
            check_re = match_relay_info[index]
            copy_poseidon.remove(check_re)
            check_list.append([[check_re], copy_poseidon])
        return check_list

    def restore_device_info_lst(self):
        """ 还原模块顺序 """
        Globals.set("PoseidonList", self.bind_info)


reorder = Reorder()

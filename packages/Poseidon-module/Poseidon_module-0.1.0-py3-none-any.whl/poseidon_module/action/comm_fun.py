# -*- coding:utf-8 -*-
import time
# import win32serviceutil
# import win32service

from poseidon_module.core.globals import Globals as gl
import poseidon_module.core.logger as log
from poseidon_module.utils.env import UtilEnv
from poseidon_module.utils.pc import UtilNet
from poseidon_module.utils.uart import UtilSerial
from poseidon_module.utils.shell import UtilShell
from poseidon_module.utils.comm import UtilComm
from poseidon_module.utils.registry import UtilWin
from poseidon_module.core.decorators import PoseidonUtil, LogFunMeta

exec_mode = 1  # 0 -- 自动； 1 --  手动


class SceneCommFun(metaclass=LogFunMeta):
    def __init__(self):
        self.log = log.get_system_logger()
        self.poseidon_util = PoseidonUtil()
        self.lc_shell = UtilShell()
        self.lc_net = UtilNet()
        self.lc_serial = UtilSerial()
        self.lc_env = UtilEnv()
        self.lc_util = UtilComm()
        self.lc_win = UtilWin()

        self.bind_info = None
        self.flight_flag = False

    def lc_power_down_up(self, start_app=True, dev_index=1):
        """
        继电器控制掉电后上电
        :param start_app:
        :param dev_index: 设备编号
        :return: True / False
        """
        started_flag = gl.get_global_value("Module_Default_Start_Process")
        try:
            port_pwr, re_type_pwr, num_pwr = self.lc_util.lc_get_relay_info(2, dev_index=dev_index)
            port_key, re_type_key, num_key = self.lc_util.lc_get_relay_info(3, dev_index=dev_index)
            self.log.info("模块掉电开始")
            if exec_mode == 1:
                assert self.lc_util.lc_manual_step("掉电上电完点击确认")
            else:
                assert self.lc_serial.lc_serial_control_relay(port_pwr, 0, re_type_pwr, num_pwr)
                ret = self.lc_shell.lc_check_adb_device_status(0, dev_index, timeout=10)
                assert ret, "10秒钟未检测到模块掉电"
                time.sleep(2)
                self.log.info("模块上电开始")
                assert self.lc_serial.lc_serial_control_relay(port_pwr, 1, re_type_pwr, num_pwr)
                if port_key != "COM0":
                    time.sleep(3)
                    self.log.info("按键开机")
                    assert self.lc_serial.lc_serial_control_relay(port_key, 0, re_type_key, num_key)
                    time.sleep(1)
                    assert self.lc_serial.lc_serial_control_relay(port_key, 1, re_type_key, num_key)
            self.log.info("检查开机状态")
            assert self.lc_shell.lc_check_module_boot_status(started_flag, 180, dev_index), "检查开机标志超时"
            assert self.lc_env.lc_setup_test_env(start_app, False, dev_index), "测试环境准备失败！"
        except Exception as e:
            self.log.error(e)
            return False
        return True

    def lc_power_down(self, dev_index=1):
        """
        继电器控制掉电
        :param dev_index: 设备编号
        :return: True / False
        """
        try:
            port_pwr, re_type_pwr, num_pwr = self.lc_util.lc_get_relay_info(2, dev_index=dev_index)
            self.log.info("模块掉电开始")
            if exec_mode == 1:
                assert self.lc_util.lc_manual_step("掉电完点击确认")
            else:
                assert self.lc_serial.lc_serial_control_relay(port_pwr, 0, re_type_pwr, num_pwr)
            ret = self.lc_shell.lc_check_adb_device_status(0, dev_index, timeout=10)
            assert ret, "10秒钟未检测到模块掉电"
        except Exception as e:
            self.log.error(e)
            return False
        return True

    def lc_power_up(self, start_app=True, dev_index=1):
        """
        继电器控制上电
        :param start_app:
        :param dev_index: 设备编号
        :return: True / False
        """
        started_flag = gl.get_global_value("Module_Default_Start_Process")
        try:
            port_pwr, re_type_pwr, num_pwr = self.lc_util.lc_get_relay_info(2, dev_index=dev_index)
            port_key, re_type_key, num_key = self.lc_util.lc_get_relay_info(3, dev_index=dev_index)
            self.log.info("模块上电开始")
            if exec_mode == 1:
                assert self.lc_util.lc_manual_step("上电完点击确认")
            else:
                assert self.lc_serial.lc_serial_control_relay(port_pwr, 1, re_type_pwr, num_pwr)
                if port_key != "COM0":
                    time.sleep(3)
                    self.log.info("按键开机")
                    assert self.lc_serial.lc_serial_control_relay(port_key, 0, re_type_key, num_key)
                    time.sleep(1)
                    assert self.lc_serial.lc_serial_control_relay(port_key, 1, re_type_key, num_key)
            self.log.info("检查开机状态")
            assert self.lc_shell.lc_check_module_boot_status(started_flag, 180, dev_index), "检查开机标志超时"
            assert self.lc_env.lc_setup_test_env(start_app, False, dev_index), "测试环境准备失败！"
        except Exception as e:
            self.log.error(e)
            return False
        return True

    def lc_force_boot_bootloader(self, reset=True, dev_index=1):
        """
        继电器控制模块进入bootloader
        :param reset: 是否恢复管脚状态
        :param dev_index: 设备编号
        :return: True / False
        """
        result = True
        boot, type5, num5 = self.lc_util.lc_get_relay_info(5, dev_index=dev_index)
        power, type2, num2 = self.lc_util.lc_get_relay_info(2, dev_index=dev_index)
        key, type3, num3 = self.lc_util.lc_get_relay_info(3, dev_index=dev_index)
        try:
            self.log.info("硬件方式进入fastboot 模式")
            assert self.lc_serial.lc_serial_control_relay(power, 0, type2, num2)
            assert self.lc_shell.lc_check_adb_device_status(0, dev_index=dev_index), "控制继电器掉电失败！"
            assert self.lc_serial.lc_serial_control_relay(boot, 0, type5, num5)
            assert self.lc_serial.lc_serial_control_relay(power, 1, type2, num2)
            if key:
                time.sleep(3)
                self.log.info("按键开机")
                assert self.lc_serial.lc_serial_control_relay(key, 0, type3, num3)
                time.sleep(1)
                assert self.lc_serial.lc_serial_control_relay(key, 1, type3, num3)
            assert self.lc_shell.lc_check_fastboot_device_status(1, dev_index=dev_index), "进入bootloader失败！"
        except Exception as e:
            self.log.error(e)
            result = False
        if reset:
            assert self.lc_serial.lc_serial_control_relay(boot, 1, type5, num5)
        return result

    def lc_power_down_up_edl(self, service_pin=False, reset=True, dev_index=1):
        """
        继电器控制模块进入 edl模式
        :param reset: 是否恢复管脚状态
        :param service_pin: 是否使用service 管脚
        :param dev_index: 设备编号
        :return: True / False
        """
        result = True
        service, type6, num6 = self.lc_util.lc_get_relay_info(6, dev_index=dev_index)
        power, type2, num2 = self.lc_util.lc_get_relay_info(2, dev_index=dev_index)
        key, type3, num3 = self.lc_util.lc_get_relay_info(3, dev_index=dev_index)
        try:
            self.log.info("硬件方式进入edl 模式")
            assert self.lc_serial.lc_serial_control_relay(power, 0, type2, num2)
            assert self.lc_shell.lc_check_adb_device_status(0, dev_index=dev_index), "控制继电器掉电失败！"
            if service_pin:
                assert self.lc_serial.lc_serial_control_relay(service, 0, type6, num6)
            assert self.lc_serial.lc_serial_control_relay(power, 1, type2, num2)
            if key:
                self.log.info("按键开机")
                assert self.lc_serial.lc_serial_control_relay(key, 0, type3, num3)
                time.sleep(1)
                assert self.lc_serial.lc_serial_control_relay(key, 1, type3, num3)
            assert self.lc_util.lc_check_9008_port()[0], "进入 edl 失败！"
        except Exception as e:
            self.log.error(e)
            result = False
        if service_pin and reset:
            assert self.lc_serial.lc_serial_control_relay(service, 1, type6, num6)
        return result

    def lc_modem_reset(self, start_app=True, dev_index=1):
        """
        继电器控制掉电后上电
        :param start_app:
        :param dev_index: 设备编号
        :return: True / False
        """
        result = True
        started_flag = gl.get_global_value("Module_Default_Start_Process")
        try:
            port_reset, re_type_reset, num_reset = self.lc_util.lc_get_relay_info(4, dev_index=dev_index)
            self.log.info("模块reset开始")
            if exec_mode == 1:
                assert self.lc_util.lc_manual_step("reset完点击确认")
            else:
                assert self.lc_serial.lc_serial_control_relay(port_reset, 0, re_type_reset, num_reset)
                time.sleep(3)
                assert self.lc_serial.lc_serial_control_relay(port_reset, 1, re_type_reset, num_reset)
            ret = self.lc_shell.lc_check_adb_device_status(0, dev_index, timeout=10)
            assert ret, "10秒钟未检测到模块进入重启"
            self.log.info("检查开机状态")
            assert self.lc_shell.lc_check_module_boot_status(started_flag, 180, dev_index), "检查开机标志超时"
            assert self.lc_env.lc_setup_test_env(start_app, False, dev_index), "测试环境准备失败！"
        except Exception as e:
            self.log.error(e)
            result = False
        return result

    def lc_modem_reboot(self, start_app=True, dev_index=1):
        """
        模组软重启， reboot
        :param start_app:
        :param dev_index: 设备编号
        :return: True / False
        """
        started_flag = gl.get_global_value("Module_Default_Start_Process")
        try:
            assert self.lc_shell.lc_adb_shell_reboot(False, 60, dev_index), "reboot 失败！"
            self.log.info("检查开机状态")
            assert self.lc_shell.lc_check_module_boot_status(started_flag, 180, dev_index), "检查开机标志超时"
            assert self.lc_env.lc_setup_test_env(start_app, False, dev_index), "测试环境准备失败！"
        except Exception as e:
            self.log.error(e)
            return False
        return True

    def lc_modem_force_reboot(self, start_app=True, dev_index=1):
        """
        模组强制重启， reboot -f
        :param start_app:
        :param dev_index: 设备编号
        :return: True / False
        """
        result = True
        started_flag = gl.get_global_value("Module_Default_Start_Process")
        try:
            assert self.lc_shell.lc_adb_shell_reboot(True, 60, dev_index), "reboot 失败！"
            self.log.info("检查开机状态")
            assert self.lc_shell.lc_check_module_boot_status(started_flag, 180, dev_index), "检查开机标志超时"
            assert self.lc_env.lc_setup_test_env(start_app, False, dev_index), "测试环境准备失败！"
        except Exception as e:
            self.log.error(e)
            result = False
        return result

    def lc_goto_sleep_by_vbus(self, dev_index=1):
        """
        通过 Vbus 控制休眠
        :param dev_index:
        :return: True / False
        """
        result = True
        try:
            gl.set_global_value("CheckDebug", True)
            port_vbus, re_type_vbus, num_vbus = self.lc_util.lc_get_relay_info(0, dev_index=dev_index)
            port_pin, re_type_pin, num_pin = self.lc_util.lc_get_relay_info(1, dev_index=dev_index)
            # assert self.lc_shell.lc_execute_adb_shell("echo 8 8 8 8 > /proc/sys/kernel/printk", 1)[0], "开日志失败！"
            assert self.lc_shell.lc_execute_adb_shell("echo 7 4 1 7 > /proc/sys/kernel/printk", 1)[0], "开日志失败！"
            # assert self.lc_shell.lc_poseidon_shortcut_action(2, 0)[0], "调用suspend失败！"
            self.log.info("模块休眠开始")
            if exec_mode == 1:
                assert self.lc_util.lc_manual_step("确认后拔出USB")
            else:
                assert self.lc_serial.lc_serial_control_relay(port_vbus, 0, re_type_vbus, num_vbus)
                if port_pin != "COM0":
                    assert self.lc_serial.lc_serial_control_relay(port_pin, 1, re_type_pin, num_pin)
            assert self.lc_serial.lc_serial_check_sleep_status(60, dev_index=dev_index), "休眠检测失败！"
        except Exception as e:
            self.log.error(e)
            result = False
        gl.set_global_value("CheckDebug", False)
        return result

    def lc_wakeup_by_vbus(self, dev_index=1):
        """
        通过 Vbus 控制唤醒
        :param dev_index:
        :return: True / False
        """
        result = True
        try:
            gl.set_global_value("CheckDebug", True)
            port_vbus, re_type_vbus, num_vbus = self.lc_util.lc_get_relay_info(0, dev_index=dev_index)
            port_pin, re_type_pin, num_pin = self.lc_util.lc_get_relay_info(1, dev_index=dev_index)
            if exec_mode == 1:
                assert self.lc_util.lc_manual_step("确认后插入USB")
            else:
                assert self.lc_serial.lc_serial_control_relay(port_vbus, 1, re_type_vbus, num_vbus)
            assert self.lc_serial.lc_serial_check_wakeup_status(30, dev_index=dev_index), "唤醒检测失败！"
            if port_pin != "COM0":
                assert self.lc_serial.lc_serial_control_relay(port_pin, 0, re_type_pin, num_pin)
            assert self.lc_shell.lc_check_adb_device_status(1, dev_index=dev_index, timeout=10)
            time.sleep(3)
            # assert self.lc_shell.lc_poseidon_shortcut_action(3, 0)[0], "调用resume失败！"
        except Exception as e:
            self.log.error(e)
            result = False
        gl.set_global_value("CheckDebug", False)
        return result

    def lc_sleep_wakeup_by_vbus(self, dev_index=1):
        """
        通过 Vbus 控制休眠唤醒
        :param dev_index:
        :return: True / False
        """
        result = True
        port_vbus, re_type_vbus, num_vbus = self.lc_util.lc_get_relay_info(0, dev_index=dev_index)
        port_pin, re_type_pin, num_pin = self.lc_util.lc_get_relay_info(1, dev_index=dev_index)
        try:
            gl.set_global_value("CheckDebug", True)
            assert self.lc_shell.lc_execute_adb_shell("echo 7 4 1 7 > /proc/sys/kernel/printk", 1)[0], "开日志失败！"
            self.log.info("模块休眠开始")
            # assert self.lc_shell.lc_poseidon_shortcut_action(2, 0)[0], "调用suspend失败！"
            if exec_mode == 1:
                assert self.lc_util.lc_manual_step("确认后拔出USB")
            else:
                assert self.lc_serial.lc_serial_control_relay(port_vbus, 0, re_type_vbus, num_vbus)
                if port_pin != "COM0":
                    assert self.lc_serial.lc_serial_control_relay(port_pin, 1, re_type_pin, num_pin)
            assert self.lc_serial.lc_serial_check_sleep_status(60), "休眠检测失败！"
            gl.set_global_value("CheckDebug", True)
            time.sleep(3)
            if exec_mode == 1:
                self.lc_util.lc_manual_step("确认后插入USB")
            else:
                assert self.lc_serial.lc_serial_control_relay(port_vbus, 1, re_type_vbus, num_vbus)
            assert self.lc_serial.lc_serial_check_wakeup_status(30), "唤醒检测失败！"
            if port_pin != "COM0":
                assert self.lc_serial.lc_serial_control_relay(port_pin, 0, re_type_pin, num_pin)
            assert self.lc_shell.lc_check_adb_device_status(1, timeout=10)
            time.sleep(3)

            # assert self.lc_shell.lc_poseidon_shortcut_action(3, 0)[0], "调用resume失败！"
        except Exception as e:
            self.log.error(e)
            if exec_mode == 1:
                assert self.lc_util.lc_manual_step("失败后插入USB后确认")
            else:
                assert self.lc_serial.lc_serial_control_relay(port_vbus, 1, re_type_vbus, num_vbus)
            time.sleep(5)

            # assert self.lc_shell.lc_poseidon_shortcut_action(3, 0)[0], "调用resume失败！"
            result = False
        gl.set_global_value("CheckDebug", False)
        return result

    def __change_other_device_usb_state(self, poseidon_list, state=0):
        for i in range(len(poseidon_list) - 1):
            port_vbus, re_type_vbus, num_vbus = self.lc_util.lc_get_relay_info(0, dev_index=i + 2)
            assert self.lc_serial.lc_serial_control_relay(port_vbus, state, re_type_vbus, num_vbus)
            ret = self.lc_shell.lc_check_adb_device_status(state, dev_index=i + 2, timeout=10)
            assert ret, f"修改设备 {i + 2} USB 状态失败！"

    # def __change_quts_service_state(self, service_name="QUTS"):
    #     result = True
    #     try:
    #         service_status = win32serviceutil.QueryServiceStatus(service_name)
    #         status_code = service_status[1]
    #         if status_code == win32service.SERVICE_RUNNING:
    #             win32serviceutil.StopService(service_name)
    #             self.log.info(f"服务 {service_name} 已成功停止")
    #         if status_code == win32service.SERVICE_STOPPED:
    #             win32serviceutil.StartService(service_name)
    #             self.log.info(f"服务 {service_name} 已成功启动")
    #     except Exception as e:
    #         self.log.error(e)
    #         result = False
    #     return result

    # def lc_multi_update_tool_upgrade(self, G_SETUP_INFO, dev_num=1, station_num="auto", mode=1):
    #     """
    #     多路升级
    #     :param G_SETUP_INFO: 升级工具信息
    #     :param dev_num: 路数，默认1路
    #     :param station_num: 升级工站数,auto：默认模块数与工站数相同, 0:默认使用station1, 1:随机选择station, 2:随机选择2路, 以此类推。
    #     :param mode: mode = 1 升级高版本，mode = 2 升级低版本。
    #     :return: True / False
    #     """
    #     result = True
    #     started_flag = gl.get_global_value("Module_Default_Start_Process")
    #     poseidon_list = gl.get_global_value("PoseidonList")
    #     try:
    #         assert self.__change_quts_service_state(), "修改QUTS服务状态失败！"
    #         self.__change_other_device_usb_state(poseidon_list, state=0)
    #         for dev_id in range(dev_num):
    #             assert self.lc_shell.lc_check_module_boot_status(started_flag, 180, dev_id + 1), "检查开机标志超时"
    #             assert self.lc_shell.lc_adb_push_app_to_modem(G_SETUP_INFO["G_RESOURCE_PATH"]["G_APP_PATH"], dev_id + 1)
    #             assert self.lc_env.lc_setup_test_env(True, False, dev_id + 1), "测试环境准备失败！"
    #     except Exception as e:
    #         self.log.error(e)
    #         result = False
    #     self.__change_other_device_usb_state(poseidon_list, state=1)
    #     assert self.__change_quts_service_state(), "修改QUTS服务状态失败！"
    #     return result

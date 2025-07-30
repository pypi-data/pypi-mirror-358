# -*- coding:utf-8 -*-
import locale
import re
import subprocess
import time
from typing import Union, List, Optional, Tuple

from poseidon_module.core.decorators import TraceActionMeta
from poseidon_module.core.globals import Globals
from poseidon_module.core.logger import sys_log


class Shell(metaclass=TraceActionMeta):
    def __init__(self, dev_index: Union[int, str] = 1, pwd: Optional[str] = None):
        self.device_id = Globals.dev_id(dev_index)
        self.pwd = pwd if pwd is not None else Globals.pwd(dev_index)
        default_locale = locale.getdefaultlocale()
        self.coding = default_locale[1] if len(default_locale) > 1 else "utf-8"
        self.adb_output_eliminate_list = [
            "\x1b.*?m",
            "Enter \w+ Passwd:",
            "\[WARNING]\*+ADB NOT USE \w+ PASSWD\*+",
            "/etc/adb_auth: line 14: can't create /tmp/adb_error: Permission denied"
        ]

    def __build_shell_cmd(self, commands: Union[str, List[str]]) -> str:
        """构建 adb shell/其它 cmd 命令字符串"""
        base_cmd = f"adb -s {self.device_id} shell "
        if isinstance(commands, list):
            commands = ' && '.join(commands)
        else:
            commands = commands
        if self.pwd is not None:
            base_cmd = f'echo {self.pwd} | {base_cmd}'
        return f'{base_cmd}"{commands}" ; echo $?'

    def __process_output(self, raw_output: str, log_output: bool = True) -> List[str]:
        """处理命令输出"""
        output_lines = []
        for line in raw_output.splitlines():
            if not line:
                continue
            line = self.__filter_line(line, self.pwd)
            if line:
                output_lines.append(line)
        if log_output:
            sys_log.debug(f"Output: {output_lines}")
        return output_lines

    def __filter_line(self, line: str, pwd: str) -> str:
        """过滤敏感信息和噪音"""
        for pattern in self.adb_output_eliminate_list:
            line = re.sub(pattern, '', line)
        if pwd:
            line = line.replace(pwd, '')
        return line

    def execute_adb_shell(self, commands: Union[str, List[str]], log_output: bool = True, timeout: int = 30
                          ) -> Tuple[bool, str]:
        """
        执行 adb shell 指令并返回执行结果
        Args:
            commands: 指令 or 指令列表
            log_output: 是否记录输出
            timeout: 超时时间
        Returns:
            Tuple(bool, str): 布尔型结果，结果字符串
        """
        try:
            cmd = self.__build_shell_cmd(commands)
            sys_log.debug(f"Executing command: {cmd}")
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                timeout=timeout,
                text=True,
                encoding="utf-8",
                errors='replace'
            )
            output = self.__process_output(result.stdout.strip(), log_output)
            if not output:
                return False, "Command execution failed, no output!"
            if output and output[-1].isdigit() and output[-1] != "0":
                out_str = '\n'.join(output[:-1])
                return False, f"Command failed: errcode {output[-1]} {f'error info {out_str}' if len(output) > 1 else ''}"
            return True, '\n'.join(output[:-1])
        except subprocess.TimeoutExpired:
            return False, f"Command execution timeout {timeout} s"
        except subprocess.CalledProcessError as e:
            return False, f"Command failed: errcode {e.returncode} error info {e.stdout}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def execute_adb_shell_background(self, command: str, proc_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        执行异步 adb shell 指令并返回执行结果，通常为一些阻塞指令，如 poseidon.sh 等
        Args:
            command: 指令
            proc_name: 检查的进程名称
        Returns:
            Tuple(bool, str): 布尔型结果，结果字符串
        """
        base_cmd = f'adb -s {self.device_id} shell'
        obj, result, info = None, False, ""
        try:
            obj = subprocess.Popen(base_cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, encoding="utf-8")
            if self.pwd is not None:
                obj.stdin.write(f'{self.pwd}\n')
            obj.stdin.write(f"cd /tmp\n")
            obj.stdin.write(f'nohup {command} > /dev/null 2>&1\n')
            obj.stdin.write('exit\n')
            obj.stdin.close()
            proc_name = command if proc_name is None else proc_name
            start_time = time.time()
            while time.time() - start_time < 10:
                time.sleep(3)
                ret, info = self.execute_adb_shell(f"pgrep {proc_name}")
                if ret:
                    result = True
                    break
            else:
                result, info = False, "Command execution timeout"
        except subprocess.CalledProcessError as e:
            result, info = False, f"Command failed: errcode {e.returncode} error info {e.stderr}"
        except Exception as e:
            result, info = False, f"Unexpected error: {str(e)}"
        finally:
            if obj:
                obj.terminate()
                obj.kill()
            return result, info

    def execute_common_shell(
            self,
            commands: Union[str, List[str]],
            log_output: bool = True,
            timeout: int = 30
    ) -> Tuple[bool, str]:
        """ 执行其它非 adb shell 指令并返回执行结果 """
        try:
            cmd = commands if isinstance(commands, str) else " && ".join(commands)
            sys_log.debug(f"Executing command: {cmd}")
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                check=True,
                timeout=timeout,
                text=True,
                encoding=self.coding,
                errors='replace'
            )
            output = self.__process_output(result.stdout.strip(), log_output)
            return True, '\n'.join(output)
        except subprocess.TimeoutExpired:
            return False, f"Command execution timeout {timeout} s"
        except subprocess.CalledProcessError as e:
            return False, f"Command failed: errcode {e.returncode} error info {e.stderr}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

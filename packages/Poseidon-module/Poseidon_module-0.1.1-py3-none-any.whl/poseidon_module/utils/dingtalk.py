# -*- coding: utf-8 -*-
import requests
import json
import time
import hmac
import hashlib
import base64
from urllib.parse import quote_plus
from configparser import ConfigParser


class UtilDingTalk:
    def __init__(self, webhook, secret=None):
        self.webhook = webhook
        self.secret = secret
        self.case_map = None

    def _sign(self):
        """生成加签"""
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = f'{timestamp}\n{self.secret}'
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = quote_plus(base64.b64encode(hmac_code))
        return f"&timestamp={timestamp}&sign={sign}"

    def send(self, content, at="", at_all=False):
        """发送消息"""
        url = self.webhook
        if self.secret:
            url += self._sign()
        headers = {'Content-Type': 'application/json'}
        message = {
            "at": {
                "atMobiles": [at],
                "isAtAll": at_all
            },
            "text": {
                "content": content
            },
            "msgtype": "text"
        }
        return requests.post(url, headers=headers, data=json.dumps(message))

    def send_markdown(self, title, text, at="", at_all=False):
        """发送Markdown格式消息"""
        url = self.webhook
        if self.secret:
            url += self._sign()
        headers = {'Content-Type': 'application/json'}
        message = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": f"@{at}\n{text}"
            },
            "at": {
                "atMobiles": [at],
                "isAtAll": at_all
            }
        }
        return requests.post(url, headers=headers, data=json.dumps(message)).json()

    def get_case_map(self, g_args):
        self.case_map = {}
        config_ini = ConfigParser()
        config_ini.read(g_args.gl["G_MAP_SHEET_PATH"], encoding="utf-8")
        for section in config_ini.sections():
            for option in config_ini.options(section):
                self.case_map[option] = config_ini.get(section, option)

    def send_dd_test_report(self, g_args):
        while g_args.gl["sessionstart"]:
            start_t = time.time()
            while time.time() - start_t < g_args.gl["G_DD_INTERVAL"]:
                if not g_args.gl["sessionstart"]:
                    break
                time.sleep(1)
            markdown_text = "## **测试状态简报**\n"
            case_name = g_args.cur_case_name
            if case_name is None:
                time.sleep(10)
                continue
            case_name = "_".join(case_name.split("_")[1:])
            for k, v in self.case_map.items():
                if case_name in v:
                    markdown_text += f"- **用例编号**\n*{case_name}*\n"
                    markdown_text += f"- **测试次数**\n*{g_args.gl['lt_pr_report']['target_total']}*\n"
                    markdown_text += f"- **当前次数**\n*{g_args.gl['lt_pr_report']['round']}*\n"
                    self.send_markdown("测试简报", markdown_text, at=f"{k}", at_all=False)
                    break

    def send_fail_log(self, g_args):
        markdown_text = "## **测试失败告警！！！！！！**\n"
        case_name = g_args.cur_case_name
        case_name = "_".join(case_name.split("_")[1:])
        for k, v in self.case_map.items():
            if case_name in v:
                markdown_text += f"- **用例编号**\n*{case_name}*\n"
                markdown_text += f"- **测试次数**\n*{g_args.gl['lt_pr_report']['target_total']}*\n"
                markdown_text += f"- **当前轮次**\n*{g_args.gl['lt_pr_report']['round']}*\n"
                markdown_text += f"- **失败信息**\n*{g_args.test_result['info']}*\n"
                markdown_text += f"- **远程信息**\n*{g_args.gl['G_EVN_REMOTE_ID']}*\n"
                self.send_markdown("测试简报", markdown_text, at=f"{k}", at_all=False)
                break

    def send_end_log(self, g_args):
        markdown_text = "## **测试结束统计**\n"
        markdown_text += f"- **用例总数**\n*{g_args.gl['total_case']}*\n"
        markdown_text += f"- **成功总计**\n*{g_args.gl['passed']}*\n"
        markdown_text += f"- **失败总计**\n*{g_args.gl['failed']}*\n"
        markdown_text += f"- **跳过总计**\n*{g_args.gl['skipped']}*\n"
        markdown_text += f"- **远程信息**\n*{g_args.gl['G_EVN_REMOTE_ID']}*\n"
        self.send_markdown("测试简报", markdown_text, at=f"所有人", at_all=True)

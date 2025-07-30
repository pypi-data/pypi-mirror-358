# _*_ coding :UTF-8 _*_
import codecs
from typing import Tuple

from poseidon_module.core.const import gsm7_base, gsm7_ext
from poseidon_module.core.decorators import trace_action


class _Codec:
    @staticmethod
    def __swip(data):
        chars = list(data)
        for i in range(0, len(chars) - 1, 2):
            chars[i], chars[i + 1] = chars[i + 1], chars[i]
        return "".join(chars)

    @staticmethod
    def __pdu7encode(string, udh=False):
        """将字符串编码为PDU7格式的十六进制字符串"""
        binstr = ''.join(f"{ord(c):07b}" for c in reversed(string))
        if udh:
            binstr += '0'
        padding = (8 - len(binstr) % 8) % 8
        binstr = binstr.ljust(len(binstr) + padding, '0')
        hex_str = ''.join(f"{int(binstr[i:i + 8], 2):02X}" for i in range(0, len(binstr), 8))
        return hex_str

    @staticmethod
    def __pdu7decode(hex_str):
        """将PDU7格式的十六进制字符串解码为原始字符串"""
        binstr = ''.join(f"{int(c, 16):04b}" for c in hex_str)
        bin_blocks = [binstr[i:i + 8] for i in range(0, len(binstr), 8)][::-1]
        binstr = ''.join(bin_blocks)
        string = ''.join(chr(int(binstr[i:i + 7].ljust(7, '0'), 2)) for i in range(0, len(binstr), 7))
        return string[::-1]

    def __gsm7decode(self, hex_str):
        result = []
        i = 0
        string = self.__pdu7decode(hex_str)
        while i < len(string):
            byte = int(string[i:i + 2], 16)
            if byte == 0x1B:  # 转义字符
                i += 2
                ext_byte = int(string[i:i + 2], 16)
                result.append(gsm7_ext.get(ext_byte, ''))
            else:
                result.append(gsm7_base.get(byte, ''))
            i += 2
        return ''.join(result)

    def __gsm7encode(self, text_str, flag):
        # 创建反向映射字典
        base_reverse = {v: k for k, v in gsm7_base.items()}
        ext_reverse = {v: k for k, v in gsm7_ext.items()}
        result = []
        for char in text_str:
            if char in ext_reverse:  # 处理扩展字符
                result.append(f'1B{ext_reverse[char]:02X}')
            elif char in base_reverse:  # 处理基础字符
                result.append(f'{base_reverse[char]:02X}')
            else:  # 不支持的字符处理
                result.append('3F')  # 默认替换为问号
        return self.__pdu7encode(''.join(result), flag)

    @trace_action
    def pdu_encode(self, phone_num: str = '', data: str = '', cs_num: str = "", format_type: int = 0,
                   class_valid: int = 1, message_class: int = 0, expect_segments: int = 1,
                   current_no: int = 1) -> Tuple[str, int]:
        # 编码类型映射
        encode_map = {0: ("7BIT", "00"), 1: ("8BIT", "01"), 2: ("UCS2", "10")}
        class_map = {0: "00", 1: "01", 2: "10", 3: "11", 4: "00"}
        segment_limit = {"7BIT": [160, 150], "8BIT": [140, 130], "UCS2": [70, 65]}
        # 1. 处理短信中心号码
        if not cs_num or len(cs_num) == 0:
            cs_num = "00"
        else:
            cs_type = '91' if cs_num.startswith('+') else '81'
            cs_num = cs_num[1:] if cs_num.startswith('+') else cs_num
            if len(cs_num) % 2 != 0:
                cs_num += 'F'
            cs_num = self.__swip(cs_num)
            cs_len = len(cs_num) // 2 + 1
            cs_num = f"{cs_len:02X}{cs_type}{cs_num}"
        # 2. 处理目标号码
        phone_type = "91" if phone_num.startswith('+') else "81"
        phone_num = phone_num[1:] if phone_num.startswith('+') else phone_num
        phone_len = len(phone_num)
        if len(phone_num) % 2 != 0:
            phone_num += 'F'
        phone_num = self.__swip(phone_num)
        dst_phone = f"{phone_len:02X}{phone_type}{phone_num}"
        # 3. 确定编码参数
        encode, encode_code = encode_map[format_type]
        if message_class == 4:
            class_valid = 0
        msg_class = class_map[message_class]
        dcs = f"000{class_valid}{encode_code}{msg_class}"
        dcs = hex(int(dcs, 2))[2:].zfill(2).upper()
        # 4. 处理长短信分包
        segment_size = segment_limit[encode][1]
        actual_segments = (len(data) + segment_size - 1) // segment_size
        if expect_segments > 1:
            assert expect_segments == actual_segments, "分包数量不匹配"
            start = segment_size * (current_no - 1)
            end = segment_size * current_no if current_no != expect_segments else None
            data = data[start:end]
            pdu_type = "51"  # 长短信类型
        else:
            pdu_type = "11"  # 普通短信类型
        # 5. 内容编码处理
        if encode == "7BIT":
            data_len = len(data)
            data_code = self.__gsm7encode(data, expect_segments > 1)
            dcs = dcs if dcs else "00"
        elif encode == "8BIT":
            data_len = len(data)
            data_code = ''.join(f"{ord(c):02X}" for c in data)
            dcs = dcs if dcs else "04"
        else:  # UCS2
            data_len = len(data) * 2
            data_code = codecs.encode(data.encode('utf_16_be'), 'hex').decode("ascii").upper()
            dcs = dcs if dcs else "08"
        # 6. 生成UDH头(长短信)
        if expect_segments > 1:
            if encode == "7BIT":
                udh_code = f"05000339{expect_segments:02X}{current_no:02X}"
            else:
                udh_code = f"0608040039{expect_segments:02X}{current_no:02X}"  # 当前编码和软件解码方式有差异
            udh_len = 7
        else:
            udh_code = ""
            udh_len = 0
        # 7. 组装PDU
        pdu = f"{cs_num}{pdu_type}00{dst_phone}00{dcs}FF{data_len + udh_len:02X}{udh_code}{data_code}"
        return pdu, len(pdu) // 2


codec = _Codec()

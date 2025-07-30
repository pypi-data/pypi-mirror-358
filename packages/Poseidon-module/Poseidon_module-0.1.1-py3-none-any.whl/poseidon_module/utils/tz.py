# -*- coding:utf-8 -*-
import re

from poseidon_module.core.decorators import TraceActionMeta
from poseidon_module.core.logger import sys_log
from poseidon_module.core.poseidon import Poseidon
from poseidon_module.utils._shell import Shell


class UtilTZ(Shell, metaclass=TraceActionMeta):
    def __init__(self):
        super().__init__()
        self.poseidon = Poseidon()

    @staticmethod
    def __reverse_and_pairwise_reverse(s):
        reversed_s = s[::-1]
        length = len(reversed_s)
        if length % 2 != 0:
            reversed_s = reversed_s[:-1]
        pairwise_reversed = ''.join(reversed_s[i:i + 2][::-1] for i in range(0, len(reversed_s), 2))
        return pairwise_reversed

    def generator_ecc_sign_file(self, sign_buf):
        buf_size = int(len(sign_buf) / 2)
        try:
            # 根据r值生成r值的文件内容
            r = self.__reverse_and_pairwise_reverse(sign_buf[:buf_size])  # 大小端转换
            if r[:2] == "00":
                r = r[2:]
            head_r = '{:08b}'.format(int(r[:2], 16))  # 获取r的第一个字节的二进制
            r = "00" + r if head_r[0] == "1" else r  # 第一个数字为1，则补 00
            r = "02" + hex(int(len(r) / 2))[2:] + r  # 最终回填的r为 02+r长度+r值
            # 根据r值生成r值的文件内容
            s = self.__reverse_and_pairwise_reverse(sign_buf[buf_size:])
            if s[:2] == "00":
                s = s[2:]
            head_s = '{:08b}'.format(int(s[:2], 16))  # 获取s的第一个字节的二进制
            s = "00" + s if head_s[0] == "1" else s
            s = "02" + hex(int(len(s) / 2))[2:] + s  # 最终回填的s为 02+s长度+s值
            sequence_size = int(len(r + s) / 2)  # 获取序列整体长度
            if buf_size >= 130:
                sequence_head = "3081" + hex(sequence_size)[2:]  # 序列头为 03 + 长度
            else:
                sequence_head = "30" + hex(sequence_size)[2:]  # 序列头为 03 + 长度
            sequence = sequence_head + r + s  # 最终文件内容为 序列头 + r+ s
            sign_file = "/oemdata/ecc_signature.der"
            ret = self.poseidon.module_write_file(sign_file, sequence, len(sequence) / 2)  # 将信息写入签名文件
            assert ret, "写签名文件失败！"
            return True, sign_file
        except Exception as e:
            sys_log.error(e)
        return False, None

    def lc_openssl_generate_ecc_key(self, key_size, file_path="/oemdata"):
        """
        openssl 生成ecc密钥并返回适配接口的密钥字典
        :param key_size:
        :param file_path:
        :return:
        """
        size_dic = {20: "secp160r1", 24: "secp192k1", 28: "secp224r1", 32: "prime256v1", 48: "secp384r1",
                    66: "secp521r1", }
        private_key_file = f"{file_path}/ecc_private_key.pem"
        public_key_file = f"{file_path}/ecc_public_key.pem"
        gen_private_key = f"openssl ecparam -name {size_dic[key_size]} -genkey -noout -out {private_key_file}"
        gen_public_key = f"openssl ec -in {private_key_file} -pubout -out {public_key_file}"
        get_key = f"openssl ec -in {private_key_file} -text -noout"
        try:
            ret, info = self.execute_adb_shell(gen_private_key)
            assert ret, "生成私钥失败！"
            ret, info = self.execute_adb_shell(gen_public_key)
            assert ret, "生成公钥失败！"
            ret, info = self.execute_adb_shell(get_key)
            assert ret, "查看密钥失败！"
            result = re.findall(r"pub:(.*)ASN", info, re.S)
            assert result, "匹配公钥失败！"
            public_key = result[0].replace(" ", "").replace(":", "").replace("\n", "")[2:]
            assert len(public_key) % 8 == 0, "公钥长度不是8的倍数！"
            tmp_x = public_key[:key_size * 2]
            if key_size == 66:
                tmp_x = tmp_x + "0000"  # 当key_size 为66时需对公私钥补0，为8的倍数
            public_key_x = [int('0x' + self.__reverse_and_pairwise_reverse(i), 16) for i in
                            re.findall(r'.{8}', tmp_x)]
            public_key_x = public_key_x + [0] * (key_size - len(public_key_x))
            tmp_y = public_key[key_size * 2:]
            if key_size == 66:
                tmp_y = tmp_y + "0000"  # 当key_size 为66时需对公私钥补0，为8的倍数
            public_key_y = [int('0x' + self.__reverse_and_pairwise_reverse(i), 16) for i in
                            re.findall(r'.{8}', tmp_y)]
            public_key_y = public_key_y + [0] * (key_size - len(public_key_y))
            result = re.findall(r"priv:(.*)pub", info, re.S)
            assert result, "匹配私钥失败！"
            private_key = result[0].replace(" ", "").replace(":", "").replace("\n", "")
            if key_size == 20:
                private_key = private_key[2:]
            if key_size == 66:
                private_key = private_key + "0000"  # 当key_size 为66时需对公私钥补0，为8的倍数
            assert len(private_key) % 8 == 0, "私钥长度不是8的倍数！"
            private_key = [int('0x' + self.__reverse_and_pairwise_reverse(i), 16) for i in
                           re.findall(r'.{8}', private_key)]

            private_key = private_key + [0] * (key_size - len(private_key))
        except Exception as e:
            sys_log.error(e)
            return False, None, None, None
        sys_log.info(f"public_key_x:{public_key_x}")
        sys_log.info(f"public_key_y:{public_key_y}")
        sys_log.info(f"private_key:{private_key}")
        key_x = {"num": public_key_x, "size": key_size}
        key_y = {"num": public_key_y, "size": key_size}
        pri_key = {"num": private_key, "size": key_size}
        info = {"key_size": key_size, "public_keyx": key_x, "public_keyy": key_y,
                "private_key": pri_key, "filename": "", "filename_size": 0}
        return True, info, public_key_file, private_key_file

    def lc_openssl_ecc_sign(self, hash_idx, private_key_file, plaintext_file, file_path="/oemdata"):
        hash_dic = {"0x11": "sha1", "0x12": "sha224", "0x13": "sha256", "0x14": "sha384", "0x15": "sha512"}
        sign_file = f"{file_path}/ecc_signature.der"
        ecc_sign = f"openssl dgst -{hash_dic[hash_idx]} -sign {private_key_file} -out {sign_file} {plaintext_file}"
        ret, info = self.execute_adb_shell(ecc_sign)
        if not ret:
            return False, None, None
        ret, info = self.execute_adb_shell(f"openssl asn1parse -inform DER -in {sign_file}")
        result = re.findall(r"INTEGER.*:(\w+)", info)
        r = self.__reverse_and_pairwise_reverse(result[0])
        r = r + (132 - len(r)) * "0"  # r值不够66 需补0
        s = self.__reverse_and_pairwise_reverse(result[1])
        s = s + (132 - len(s)) * "0"  # s值不够66 需补0
        sign_buf = r + s
        return True, sign_file, sign_buf

    def lc_openssl_ecc_verify(self, hash_idx, public_key_file, sign_file, plaintext_file):
        hash_dic = {"0x11": "sha1", "0x12": "sha224", "0x13": "sha256", "0x14": "sha384", "0x15": "sha512"}
        ecc_verify = f"openssl dgst -{hash_dic[hash_idx]} -verify {public_key_file} -signature {sign_file} {plaintext_file}"
        ret, info = self.execute_adb_shell(ecc_verify)
        return ret

    def lc_openssl_generate_rsa_key(self, pub_exp, key_size, file_path="/oemdata"):
        """
        openssl 生成rsa密钥并返回适配接口的密钥字典
        :param pub_exp:
        :param key_size:
        :param file_path:
        :return:
        """
        private_key_file = f"{file_path}/rsa_private_key.pem"
        public_key_file = f"{file_path}/rsa_public_key.pem"
        gen_private_key = f"openssl genpkey -algorithm RSA -out {private_key_file} -pkeyopt rsa_keygen_bits:{key_size * 8} -pkeyopt rsa_keygen_pubexp:{int(pub_exp, 16)}"
        gen_public_key = f"openssl rsa -in {private_key_file} -pubout -out {public_key_file}"
        get_key = f"openssl rsa -in {private_key_file} -text -noout"
        try:
            ret, info = self.execute_adb_shell(gen_private_key)
            assert ret, "生成私钥失败！"
            ret, info = self.execute_adb_shell(gen_public_key)
            assert ret, "生成公钥失败！"
            ret, info = self.execute_adb_shell(get_key)
            assert ret, "查看密钥失败！"
            result = re.findall(r"modulus:(.*)publicexponent", info.lower(), re.S)
            assert result, "匹配模数 n 失败！"
            n = result[0].replace(" ", "").replace(":", "").replace("\n", "")[2:]
            # n_size = len(n) / 2 / 4  # 2：16进制每两位表示一个字节；4：uint32_t占用字节
            assert len(n) % 8 == 0, "模数 n 长度不是8的倍数！"
            result = re.findall(r"privateexponent:(.*)prime1", info.lower(), re.S)
            assert result, "匹配私钥指数 d 失败！"
            d = result[0].replace(" ", "").replace(":", "").replace("\n", "")
            assert len(d) % 8 == 0, "私钥指数 d 长度不是8的倍数！"
            if len(d) / 2 != key_size:
                sys_log.info(f"私钥指数 d 生成的长度为{len(d)}，传入的key_size为{key_size}，脚本进行匹配！")
                if len(d) / 2 > key_size:
                    for i in range(int(len(d) / 2 - key_size)):
                        if d[0:2] == "00":
                            d = d[2:]
                        else:
                            sys_log.info("私钥指数 d 前两位不为0！")
                            return False, None, None
        except Exception as e:
            sys_log.error(e)
            return False, None, None
        return True, n, d

    def lc_openssl_rsa_sign(self, hash_idx, private_key_file, plaintext, plaintext_size, file_path="/oemdata"):
        hash_dic = {"0x11": "sha1", "0x12": "sha224", "0x13": "sha256", "0x14": "sha384", "0x15": "sha512"}
        plaintext_file = f"{file_path}/rsa_plaintext.bin"
        sign_file = f"{file_path}/rsa_signature.bin"
        self.poseidon.module_write_file(plaintext_file, plaintext, plaintext_size), "写文件失败！"
        rsa_sign = f"openssl dgst -{hash_dic[hash_idx]} -sign {private_key_file} -out {sign_file} {plaintext_file}"
        ret, info = self.execute_adb_shell(rsa_sign)
        if not ret:
            return False, None
        ret, info = self.execute_adb_shell(f"stat {sign_file}")
        file_size = re.findall(r"Size: (\d+)", info)[0]
        sign_data = self.poseidon.module_read_file(sign_file, int(file_size))
        return True, sign_data, sign_file

    def lc_openssl_rsa_verify(self, hash_idx, public_key_file, sign_file, plaintext, plaintext_size,
                              file_path="/oemdata"):
        hash_dic = {"0x11": "sha1", "0x12": "sha224", "0x13": "sha256", "0x14": "sha384", "0x15": "sha512"}
        plaintext_file = f"{file_path}/rsa_plaintext.bin"
        self.poseidon.module_write_file(plaintext_file, plaintext, plaintext_size), "写文件失败！"
        rsa_verify = f"openssl dgst -{hash_dic[hash_idx]} -verify {public_key_file} -signature {sign_file} {plaintext_file}"
        ret, info = self.execute_adb_shell(rsa_verify)
        if not ret:
            return False
        return True

    def lc_openssl_hash(self, hash_idx, plaintext_file):
        hash_dic = {"0x11": "sha1", "0x12": "sha224", "0x13": "sha256", "0x14": "sha384", "0x15": "sha512"}
        rsa_verify = f"openssl dgst -{hash_dic[hash_idx]} {plaintext_file}"
        ret, info = self.execute_adb_shell(rsa_verify)
        if not ret:
            return False, None
        result = re.findall(r"=.*?(\w+)", info)
        return True, result[0].upper()

    def lc_openssl_aes_encrypt(self, aes_mode, key_size, key, iv, plaintext, plaintext_size, file_path="/oemdata"):
        mode_dic = {"0x10": "ecb", "0x11": "cbc", "0x12": "ctr"}
        plaintext_file = f"{file_path}/aes_plaintext.bin"
        encrypted_file = f"{file_path}/aes_encrypted.bin"
        _iv = f" -iv {iv}" if iv is not None else ""
        self.poseidon.module_write_file(plaintext_file, plaintext, plaintext_size)
        cmd = f"openssl enc -aes-{key_size * 8}-{mode_dic[aes_mode]} -e -K {key}{_iv} -in {plaintext_file} -out {encrypted_file}"
        ret, info = self.execute_adb_shell(cmd)
        if not ret:
            return False, ""
        ret, info = self.execute_adb_shell(f"stat {encrypted_file}")
        file_size = re.findall(r"Size: (\d+)", info)[0]
        encrypted_data = self.poseidon.module_read_file(encrypted_file, int(file_size))
        return True, encrypted_data, encrypted_file

    def lc_openssl_aes_decrypt(self, aes_mode, key_size, key, iv, encrypt_data, file_path="/oemdata"):
        mode_dic = {"0x10": "ecb", "0x11": "cbc", "0x12": "ctr"}
        encrypt_file = f"{file_path}/aes_encrypted.txt"
        decrypt_file = f"{file_path}/rsa_decrypted.txt"
        _iv = f" -iv {iv}" if iv is not None else ""
        self.poseidon.module_write_file(encrypt_file, encrypt_data, len(encrypt_data) / 2)
        cmd = f"openssl enc -aes-{key_size * 8}-{mode_dic[aes_mode]} -d -K {key}{_iv} -in {encrypt_file} -out {decrypt_file}"
        ret, info = self.execute_adb_shell(cmd)
        if not ret:
            return False, None
        ret, info = self.execute_adb_shell(f"stat {decrypt_file}")
        file_size = re.findall(r"Size: (\d+)", info)[0]
        decrypt_data = self.poseidon.module_read_file(decrypt_file, int(file_size))
        return True, decrypt_data, decrypt_file

    def lc_openssl_aes_cmac(self, aes_mode, key, key_size, plaintext, plaintext_size, file_path="/oemdata"):
        mode_dic = {"0x10": "ecb", "0x11": "cbc", "0x12": "ctr"}
        plaintext_file = f"{file_path}/aes_cmac_plaintext.txt"
        self.poseidon.module_write_file(plaintext_file, plaintext, plaintext_size)
        cmd = f"openssl dgst -mac cmac -macopt cipher:aes-{key_size * 8}-{mode_dic[aes_mode]} -macopt hexkey:{key} {plaintext_file}"
        ret, info = self.execute_adb_shell(cmd)
        hex_cmac = info.split('= ')[1].strip().upper()
        if not ret:
            return False, None
        return True, hex_cmac


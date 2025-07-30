"""
# File       : 解密小程序加密数据.py
# Time       ：2022/8/23 11:54
# Author     ：xuewei zhang(张薛伟)
# Email      ：307080785@qq.com
# version    ：python 3.9
# Description：解密小程序加密数据，用于获取用户信息，比如用户的昵称、头像等。以及验证用户信息是否真实。
Crypto安装方法为：pip install pycryptodome
"""
import base64
import json
from Crypto.Cipher import AES


class DecryptUserData:
    _解密后数据 = None

    def __init__(self, encrypted_data, iv, session_key):
        self.encrypted_data = encrypted_data
        self.iv = iv
        self.session_key = session_key
        self._decrypt_data()

    def _decrypt_data(self):
        # Base64 decode
        session_key = base64.b64decode(self.session_key)
        encrypted_data = base64.b64decode(self.encrypted_data)
        iv = base64.b64decode(self.iv)

        # AES decryption
        cipher = AES.new(session_key, AES.MODE_CBC, iv)
        self._解密后数据 = json.loads(cipher.decrypt(encrypted_data).rstrip(b"\x10"))

        return self._解密后数据

    def get_解密后数据(self):
        return self._解密后数据

    def get_appid(self):
        return self._解密后数据.get("watermark", {}).get("appid")

    def _unpad(self, s):
        return s[:-ord(s[len(s) - 1:])]

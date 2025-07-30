"""
# File       : 生成订单号.py
# Time       ：2024/8/28 下午12:41
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from uuid import uuid4
import hashlib


def 生成订单号() -> str:
    原始订单号 = str(uuid4())  # 或者其他生成逻辑
    return hashlib.md5(原始订单号.encode('utf-8')).hexdigest()  # 生成md5值, 作为订单号, 32位长度

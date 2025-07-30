import binascii
import struct
from typing import List
import re


def __位数补齐(hex16Str: str) -> str:
    if len(hex16Str) % 2 == 1:
        hex16Str = "0" + hex16Str
    return hex16Str


def convert_16进制_int(num: str):
    return int(num, 16)


def convert_16进制_Bytes(x):
    bytesStr = bytes.fromhex(x)
    return bytesStr


def convert_16进制_str(x: str):
    return binascii.a2b_hex(x).decode()


def convert_Bytes_Str(x: bytes):
    return x.decode('utf-8')


def convert_str_16进制(myStr: str):
    str_16 = binascii.b2a_hex(myStr.encode("gb2312")).decode()  # 字符串转16进制
    return __位数补齐(str_16)


def convert_int_16进制(num: int) -> str:
    tmp = hex(num)[2:]
    return __位数补齐(tmp)


def convert_intList_二进制16位字符串(num: List[int]):
    req = struct.pack(f"{len(num)}B", *num)  # 转换发送命令：二进制字符串
    return req


def convert_16进制str_intList(myStr: str, 输出位数=0, 逆序: bool = False) -> List[int]:
    # 分割
    st2 = re.findall(r'.{2}', myStr)
    # 转换
    intList = [int(i, 16) for i in st2]
    # 补齐位数
    if len(intList) < 输出位数:
        intList = [0] * (输出位数 - len(intList)) + intList
    #
    if 逆序 is False:
        return intList
    else:
        intList_reverse = []
        for item in intList:
            intList_reverse = [item] + intList_reverse
        return intList_reverse


def convert_IntList_16进制Str(x: List[int]):
    tmp = ""
    for i in x:
        tmp += convert_int_16进制(i) + " "
    return tmp


if __name__ == '__main__':
    print(convert_str_16进制("扫"))
    print(convert_16进制_int("EE"))
    print(convert_16进制str_intList("00EEFF"))
    print(convert_int_16进制(88010))

import asyncio
from typing import NoReturn
import time
from app_tools_zxw.SDK_硬件读写.进制转换 import *
from app_tools_zxw.SDK_硬件读写.crc16 import crc16
from app_tools_zxw.SDK_硬件读写.串口_网口_通讯封装.串口读写.serial封装 import rw串口操作
from app_tools_zxw.SDK_硬件读写.串口_网口_通讯封装.串口读写.app应用级封装 import serial串口读写设备

"""
硬件设置：
    单张过滤：5秒
    rs232输出
"""


class readUHF卡(serial串口读写设备):
    # 覆写 - 参数配置
    波特率 = 57600
    读取字节长度 = 18

    # 覆写 - 定义返回数据格式（re）
    def _接受校验(self, d: str) -> bool:
        d = d.upper()
        验证1 = len(d) == self.读取字节长度 * 2
        验证2 = d[:2] == "11"
        验证3 = d[4:6] == "EE"
        return 验证1 and 验证2 and 验证3

    # 覆写 - 数据提取与转换
    def _提取数据(self, origin16Data: str):
        data16 = origin16Data[4 * 2: 4 * 2 + 6 * 4]
        # 16进制数据转换
        finalData = convert_16进制_int(data16)
        print(time.time(), ",读取到的卡号 = ", finalData)
        print("__________________________________________")

        return finalData


class 写UHF卡:
    """
    这个命令向电子标签写入EPC号。写入的时候，天线有效范围内只能有一张电子标签。
    命令：
        Len	    Adr	    Cmd	            Data[]	            CRC-16
                                ENum	Pwd 	WEPC
        0xXX	0xXX	0x04	0xXX	4Byte	变长	        LSB	MSB

    参数解析：
    ENum：1个字节。要写入的EPC的长度，以字为单位。不能为0，也不能超过15，否则返回参数错误信息。
    Pwd：4个字节的访问密码。32位的访问密码的最高位在Pwd的第一字节(从左往右)的最高位，
        访问密码最低位在Pwd第四字节的最低位，Pwd的前两个字节放置访问密码的高字。
        在本命令中，当EPC区设置为密码锁、且标签访问密码为非0的时候，才需要使用访问密码。在其他情况下，Pwd为零或正确的访问密码。
    WEPC：要写入的EPC号，长度必须和ENum说明的一样。WEPC最小1个字，最多15个字，否则返回参数错误信息。

    应答：
        Len	    Adr	    reCmd	Status	Data[]	CRC-16
        0x05	0xXX	0x04	0x00	——	    LSB	MSB
    """

    def __init__(self):
        self.COM = rw串口操作("COM1", 57600, None, 返回bytes长度=5)

    def __del__(self):
        self.COM.DColsePort()

    def 写入卡号(self, __cardID: int):
        __cardID = str(__cardID)
        if len(__cardID) > 6:
            raise ValueError("卡号不能超过6位")
        #
        __cardID16 = convert_int_16进制(int(__cardID)).zfill(6)
        status = self.COM.DWritePort_str(self.__生成写入指令(__cardID16))
        print("卡号写入返回状态：", status)
        self.__验证是否写入成功()

    def __验证是否写入成功(self):
        print("等待写入结果返回值...")
        while True:
            time.sleep(0.1)
            res16 = self.COM.DReadPort()
            res = binascii.b2a_hex(res16)
            if res[:0] == "05" and res[4:6] == "04":
                print("写入命令成功输入，status = ", res[6:8])
                break

    @staticmethod
    def __生成写入指令(cardID16进制并补齐位数: str):
        """
        Len	    Adr	    Cmd	            Data[]	            CRC-16
                                ENum	Pwd 	WEPC
        0xXX	0xXX	0x04	0xXX	4Byte	变长	        LSB	MSB
        """
        lens = convert_int_16进制(13)
        adr = "00"
        cmd = "04"
        eNum = convert_int_16进制(6)
        pwd = "00000000"
        wepc = cardID16进制并补齐位数
        crc = crc16(lens + adr + cmd + eNum + pwd + wepc)
        return (lens + adr + cmd + eNum + pwd + wepc + crc).upper()


if __name__ == '__main__':
    # com = 写UHF卡()
    # print(com.写入卡号(1))
    # del com

    # 读卡
    async def getdata(x: str) -> NoReturn:
        print("接受卡号 :", x)


    async def 转ws格式(some: str):
        return some


    com = readUHF卡(端口="COM3")
    print("执行完毕")
    asyncio.run(com.持续get数据并转发(getdata, 转ws格式))

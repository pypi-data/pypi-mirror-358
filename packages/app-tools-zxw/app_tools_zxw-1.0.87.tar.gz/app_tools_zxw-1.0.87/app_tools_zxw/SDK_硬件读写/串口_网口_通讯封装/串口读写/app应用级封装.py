import asyncio
from typing import Coroutine
from typing import Callable, Any
from app_tools_zxw.SDK_硬件读写.串口_网口_通讯封装.串口读写.serial封装 import rw串口操作
from app_tools_zxw.SDK_硬件读写.进制转换 import *


#
# 波特率 = 57600
# 读取字节长度 = 18


class serial串口读写设备:
    # 覆写 - 参数配置
    波特率 = 57600
    读取字节长度 = 18

    # 覆写 - 定义返回数据格式（re）
    def _接受校验(self, d: str) -> bool:
        d = d.upper()
        验证1 = len(d) == 18 * 2
        验证2 = d[:2] == "11"
        验证3 = d[4:6] == "EE"
        return 验证1 and 验证2 and 验证3

    # 覆写 - 数据提取与转换
    def _提取数据(self, origin16Data: str):
        # 开始位数 = 2*（n-1）, 结束位数 = 2*（n-1）+ 1 , 链表内结束index = 结束位数 + 1
        data16 = origin16Data[4 * 2: 4 * 2 + 6 * 4]
        # 16进制数据转换
        finalData = convert_16进制_int(data16)
        return finalData

    # -------------- ------------------------- --------------
    def __init__(self, 端口="COM4", 是否持续接受消息=True, timeout=None):
        # 打开COM口
        self.COM = rw串口操作(端口, self.波特率, timeout, 返回bytes长度=self.读取字节长度, 是否持续接受消息=是否持续接受消息)
        print(f"\n打开端口:{端口}")

    def close(self):
        self.COM.DColsePort()
        # pass

    async def 持续get数据并转发(self, ws数据发送: Callable[[str], Any], 转ws格式: Callable[[Any], Coroutine]):
        # 11 00 EE 00 E2 00 00 1D 76 05 00 17 15 50 02 00 71 20
        # 判断串口是否成功打开
        while True:
            read = self.COM.DReadPort()
            readData_16转str = binascii.b2a_hex(read).decode()

            if self._接受校验(readData_16转str):
                finalData = self._提取数据(readData_16转str)
                # 向外发送数据
                ws数据 = await 转ws格式(finalData)
                if ws数据 is not None:
                    await ws数据发送(ws数据)
                else:
                    print("数据为None,不发送")
                #
                # print("原始数据 = ", readData_16转str)
                # print("标准样例 = ", "11 00 EE 00 E2 00 00 1D 76 05 00 17 15 50 02 00 71 20".replace(" ", "").lower())
                # print("发送数据, 10进制数据 = ", finalData)
                # print("发送数据, 16进制数据 = ", convert_int_16进制(finalData))
                # print("__________________________________________")
            await asyncio.sleep(0.01)

    def 单次get数据(self):
        """
        return: -99 无有效值
        """
        read = self.COM.DReadPort()
        readData_16转str = binascii.b2a_hex(read).decode()

        if self._接受校验(readData_16转str):
            finalData = self._提取数据(readData_16转str)
            return finalData
        else:
            return -99

    def 写入数据_整数列表命令(self, cmd: List[int]) -> int:
        x = self.COM.DWritePort_List(cmd)
        return x

    @staticmethod
    async def crc16(string: str):
        data = bytearray.fromhex(string)
        crc = 0xFFFF
        for pos in data:
            crc ^= pos
            for i in range(8):
                if ((crc & 1) != 0):
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return hex(((crc & 0xff) << 8) + (crc >> 8))[2:]

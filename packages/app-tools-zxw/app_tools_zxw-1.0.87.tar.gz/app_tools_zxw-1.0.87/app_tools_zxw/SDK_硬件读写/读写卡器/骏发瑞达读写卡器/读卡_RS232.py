import asyncio
from typing import NoReturn
from datetime import datetime
from app_tools_zxw.SDK_硬件读写.进制转换 import *
from app_tools_zxw.SDK_硬件读写.串口_网口_通讯封装.串口读写.app应用级封装 import serial串口读写设备

"""
硬件设置：
    单张过滤：5秒
    rs232输出
"""


class readUHF卡(serial串口读写设备):
    # 覆写 - 参数配置
    波特率 = 115200
    读取字节长度 = 25

    # 覆写 - 定义返回数据格式（re）
    def _接受校验(self, d: str) -> bool:
        # 1B 39 01 FF 12 00 10 D4 30 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 F4
        # 1b3901ff120010d430000000000000000000000000000000f4
        d = d.upper()
        #
        验证1 = len(d) == self.读取字节长度 * 2
        if not 验证1:
            return False
        # 结构/命令 验证
        验证2 = d[:6] == "1B3901"
        验证3 = d[12:14] == "10"
        # 传输正确性验证:BCC校验
        ...
        return 验证1 and 验证2 and 验证3

    # 覆写 - 数据提取与转换
    def _提取数据(self, origin16Data: str):
        # 16进制数据转换
        data16 = origin16Data[20: 44]
        print(f"data16={len(data16), data16}")
        finalData = convert_16进制_int(data16)
        print(datetime.now(), "  读取到的卡号 = ", finalData)
        print("__________________________________________")
        return finalData


if __name__ == '__main__':
    # 读卡
    async def getdata(x: str) -> NoReturn:
        print("接受卡号 :", x)


    async def 转ws格式(some: str):
        return some


    com = readUHF卡(端口="/dev/tty.usbserial-CECRb189553")
    print("执行完毕")
    asyncio.run(com.持续get数据并转发(getdata, 转ws格式))

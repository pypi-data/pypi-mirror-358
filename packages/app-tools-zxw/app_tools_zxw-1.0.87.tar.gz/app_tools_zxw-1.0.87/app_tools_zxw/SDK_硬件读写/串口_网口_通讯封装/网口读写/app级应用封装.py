import asyncio
import socket
import time
from typing import Coroutine, Callable, Any
from app_tools_zxw.SDK_硬件读写.进制转换 import *
import datetime


# tcp客户端版
class 通过网口读写设备:
    """
    使用方法：方法1、with 通过网口读写设备(ip,port) as x:
            方法2     x = 通过网口读写设备(ip,port)
                     x.conncet()
                     ...
                     x.close()
    """

    # 覆写 - 定义返回数据格式（re）
    def _接受校验(self, d: str) -> bool:
        d = d.upper()
        验证1 = len(d) == 18 * 2
        验证2 = d[:2] == "11"
        验证3 = d[4:6] == "EE"
        return 验证1 and 验证2 and 验证3

    # 覆写 - 数据提取与转换
    def _提取数据(self, data16Str: str):
        # 开始位数 = 2*（n-1）, 结束位数 = 2*（n-1）+ 1 , 链表内结束index = 结束位数 + 1
        data16 = data16Str[4 * 2: 4 * 2 + 6 * 4]
        # 16进制数据转换
        finalData = convert_16进制_int(data16)
        return finalData

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def __init__(self, ip="192.168.0.199", port=5005, timeout=1):
        self.ip = ip
        self.port = port
        self.timeout = timeout

    def connect(self):
        try:
            # 创建连接
            self.mySockets = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.mySockets.settimeout(self.timeout)
            self.mySockets.connect((self.ip, self.port))
            print(f"--- 创建连接成功：{self.ip, self.port} ---")
        except (socket.timeout, TimeoutError, OSError) as e:
            print("创建连接失败（不自动重连）")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.mySockets.close()

    def close(self):
        self.mySockets.close()

    def 写入数据_整数列表命令(self, cmd: List[int]) -> (bool, str):
        req = convert_intList_二进制16位字符串(cmd)
        try:
            self.mySockets.send(req)
            res = self.mySockets.recv(1024)
            return True, res
        except (socket.timeout, TimeoutError) as res:
            print("连接超时：", res)
            return False, res

    def 单次get数据(self):
        """
        return: -99 无有效值
        """
        try:
            read = self.mySockets.recv(1024)
            readData_16进制Bytes转16进制str = binascii.b2a_hex(read).decode()

            if self._接受校验(readData_16进制Bytes转16进制str):
                finalData = self._提取数据(readData_16进制Bytes转16进制str)
                return finalData
            else:
                return -99
        except (socket.timeout, TimeoutError, ConnectionRefusedError) as re:
            return -999

    async def 持续get数据并转发(self, ws数据发送: Callable[[str], Any], 转ws格式: Callable[[Any], Coroutine]):
        # 11 00 EE 00 E2 00 00 1D 76 05 00 17 15 50 02 00 71 20
        self.connect()
        上次心跳 = time.time()
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), f"websocket硬件连接-持续获取数据, 地址：{self.ip}:{self.port}")
        while True:
            readData = self.单次get数据()
            if readData == "心跳包":
                上次心跳 = time.time()
            elif time.time() - 上次心跳 > 3:
                上次心跳 = time.time()
                # 硬件连接失败
                print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 硬件连接失败,3秒重连")
                self.close()
                self.connect()
            elif readData != -99 and readData != -999:  # -99是无数据，-999是未读取到数据或者连接失败
                上次心跳 = time.time()
                # 向外发送数据
                ws数据 = await 转ws格式(readData)
                if ws数据 is not None:
                    await ws数据发送(ws数据)
                else:
                    print("数据为None,不发送")
            await asyncio.sleep(0.1)

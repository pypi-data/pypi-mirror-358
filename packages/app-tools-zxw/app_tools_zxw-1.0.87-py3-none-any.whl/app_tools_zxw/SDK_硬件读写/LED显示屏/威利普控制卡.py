# -*- coding: UTF-8 -*-
from app_tools_zxw.SDK_硬件读写.串口_网口_通讯封装.串口读写.app应用级封装 import serial串口读写设备


class _led文字控制(serial串口读写设备):
    # 覆写 - 参数配置
    波特率 = 9600
    读取字节长度 = 8

    # 覆写 - 定义返回数据格式（re）
    def _接受校验(self, d: str) -> bool:
        d = d.upper()
        print("--received data = ", d)
        return True

    # 覆写 - 数据提取与转换
    def _提取数据(self, origin16Data: str):
        return origin16Data


class 修改LED显示屏文字:
    """
    为确保串口通信安全，仅能使用 with ... as ... 语法
    """
    led: _led文字控制

    def __init__(self, 端口):
        self.端口 = 端口

    def __enter__(self):
        self.led = _led文字控制(端口=self.端口, 是否持续接受消息=False, timeout=2)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.led.COM.DColsePort()
        except:
            print("修改LED显示屏文字 -> __exit__ -> 串口关闭失败")
            # 退出时删除变量
            # 删除串口变量时，默认关闭串口() ： 串口读写 -> app应用级封装 -> __del__

    def send更改命令(self, text: str, 行号=1, 显示方式=1, 刷新速度=1):
        # 生成命令
        cmd_Int = self._creat_data(行号, 显示方式, 刷新速度, color=0, text=text)
        # 发送命令
        try:
            re = self.led.写入数据_整数列表命令(cmd_Int)
            return re
        except:
            print("错误, LED串口命令发送失败")
            return 0

    @classmethod
    def __check_sum(cls, data):
        a = 0x00
        for byte in data:
            a += byte
        return a & 0xff

    @classmethod
    def _creat_data(cls, 行号, 显示方式, 刷新速度, color, text):
        """
        显示方式: 01 静止  02 左移   文字一行显示不完全则左移 （显示方式一位将无效）
        刷新速度:  0-250 数值越大移动慢
        行号取值为: 第一行：0x01，第二行：0x02，第三行：0x03）
        颜色取值为: 红：0x00，绿：0x01，蓝：0x02）
        效验位：   所有数据（除效验位）累加）
        """
        data = []
        st_list = text.encode('gb2312')
        data.append(0xf0)
        data.append(0x01)
        data.append(0xd0)
        data.append(行号)
        data.append(显示方式)
        data.append(刷新速度)
        data.append(len(st_list) + 1)
        data.append(color)
        for x in st_list:
            data.append(x)

        data.append(cls.__check_sum(data))

        return data


if __name__ == '__main__':
    import random

    while True:
        with 修改LED显示屏文字(端口="COM3") as x:
            x.send更改命令(f"first line: {random.randint(0, 100)}", 行号=1)
            x.send更改命令(f"second line: {random.randint(0, 100)}", 行号=2)
            # x.led.COM.DColsePort()
        # time.sleep(0.1)

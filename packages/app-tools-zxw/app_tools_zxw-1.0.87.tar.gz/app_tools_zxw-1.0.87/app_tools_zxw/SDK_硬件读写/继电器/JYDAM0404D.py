# -*- coding: UTF-8 -*-
from app_tools_zxw.SDK_硬件读写.串口_网口_通讯封装.串口读写.app应用级封装 import serial串口读写设备
from configs import 继电器_端口


class _继电器控制(serial串口读写设备):
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


class 继电器控制:
    """
    为确保串口通信安全，仅能使用 with ... as ... 语法
    """
    COM串口设备: _继电器控制

    def __enter__(self):
        self.COM串口设备 = _继电器控制(端口=继电器_端口, 是否持续接受消息=False, timeout=2)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.COM串口设备.COM.DColsePort()
        except:
            print(f"{继电器_端口}，继电器 -> __exit__ -> 串口关闭失败")

    def send命令(self, 输出口: int, 开关: bool):
        # 生成命令
        cmd_Int = self._creat_data(输出口, 开关)
        # 发送命令
        try:
            re = self.COM串口设备.写入数据_整数列表命令(cmd_Int)
            return re
        except:
            print("错误, LED串口命令发送失败")
            return 0

    def _creat_data(self, 输出口: int, 开关: bool):
        if 输出口 == 1:
            if 开关 is True:
                msg = [1, 5, 0, 0, 255, 0, 140, 58]
            else:
                msg = [1, 5, 0, 0, 0, 0, 205, 202]
        elif 输出口 == 2:
            if 开关 is True:
                msg = [1, 5, 0, 1, 255, 0, 221, 250]
            else:
                msg = [1, 5, 0, 1, 0, 0, 156, 10]

        else:
            msg = []
        return msg


if __name__ == '__main__':
    # intList = []
    # for i in ["01", "05", "00", "01", "00", "00", "9C", "0A"]:
    #     intList.append(convert_16进制_int(i))
    # print(intList)
    with 继电器控制() as 继电器:
        继电器.send命令(输出口=1, 开关=True)

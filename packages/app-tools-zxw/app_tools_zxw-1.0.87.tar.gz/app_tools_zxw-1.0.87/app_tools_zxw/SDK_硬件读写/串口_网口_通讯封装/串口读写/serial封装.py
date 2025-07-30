import serial  # 导入模块
import threading
import time
from typing import List

"""
读取数据： 自动断线重连
"""


class rw串口操作:
    mySerial: serial.Serial
    STRGLO = b""  # 读取的数据
    is串口打开 = True  # 读取标志位
    _PARAMS = []  # portx, bps, timeout, 返回bytes长度

    def __init__(self, portx, bps, timeout, 返回bytes长度=18, 是否持续接受消息=True):
        self._PARAMS = [portx, bps, timeout, 返回bytes长度]
        self.mySerial, self.is串口打开 = self.DOpenPort(portx, bps, timeout, 返回bytes长度, 是否持续接受消息)  # 串口类

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.DColsePort()

    # 打开串口
    # 端口，GNU / Linux上的/ dev / ttyUSB0 等 或 Windows上的 COM3 等
    # 波特率，标准值之一：50,75,110,134,150,200,300,600,1200,1800,2400,4800,9600,19200,38400,57600,115200
    # 超时设置,None：永远等待操作，0为立即返回请求结果，其他值为等待超时时间(单位为秒）
    def DOpenPort(self, portx, bps, timeout, 返回bytes长度=18, 是否持续接受消息=True):
        ret = False
        is串口打开 = False
        try:
            # 打开串口，并得到串口对象
            mySerial = serial.Serial(portx, bps, timeout=timeout)

            # 打开成功: 后台线程 持续接受新消息
            if mySerial.is_open:
                is串口打开 = True
                if 是否持续接受消息:
                    print("开启新线程：后台持续接受新消息")
                    threading.Thread(target=self.__ReadData, args=(mySerial, 返回bytes长度)).start()
            #
            return mySerial, is串口打开

        except Exception as e:
            print("---异常---：", e)
            return None, False

    # 关闭串口
    def DColsePort(self):
        self.is串口打开 = False
        # try:
        self.mySerial.flush()  # 清除缓冲区
        # except:
        #     print("缓冲区清除失败")
        try:
            self.mySerial.close()
        except:
            print("串口关闭失败")

    # 写字符串数据 - 此方式命令发送有问题，尚未成功过
    def DWritePort_str(self, text: str):
        self.__断线检测并重连(self.mySerial)
        print("最终发送命令 = ", text.encode("gb2312"))
        result = self.mySerial.write(text.encode("gb2312"))  # 写数据
        return result

    # 发送命令 - 16进制整数数组
    def DWritePort_List(self, cmd: List[int]) -> int:
        self.__断线检测并重连(self.mySerial)
        print("最终发送命令 = ", cmd)
        result = self.mySerial.write(cmd)  # 写数据
        return result

    # 读数据
    def DReadPort(self):
        strs = self.STRGLO
        self.STRGLO = b""  # 清空当次读取
        return strs

    # 读取数据 本体实现
    def __ReadData(self, mySerial: serial.Serial, 读取bytes长度=18):
        print("开启循环读取进程，0.01秒读取一次串口数据")
        # 循环接收数据，此为死循环，可用线程实现
        while self.is串口打开:
            if not self.__断线检测并重连(mySerial):
                return None  # 断线重连成功，结束此废弃线程。
            # 读取数据
            if mySerial.in_waiting:
                self.STRGLO = mySerial.read(size=读取bytes长度)
            #
            time.sleep(0.01)

    #
    def __断线检测并重连(self, mySerial: serial.Serial):
        """
        return: True 表示连接正常无需处理 ，
                False 表示连接断开，重连成功，开启新的循环读取线程，旧读取线程需关闭 （写入没有分支线程，不影响）
        """
        # 异常检测 - 设备拔出自动重连
        # 若无法连接：永远尝试循环
        while True:

            try:
                tmp = mySerial.in_waiting
                return True
            except OSError as e:
                print(e)
                self.mySerial, self.is串口成功打开 = self.DOpenPort(*self._PARAMS)  # 串口类
                if self.is串口成功打开 is True:
                    return False  # 结束此线程

            time.sleep(1)


if __name__ == "__main__":
    mySerials = rw串口操作("COM3", 57600, None)

    if mySerials.is串口成功打开 is True:  # 判断串口是否成功打开
        print("串口打开成功")
        read = mySerials.DReadPort()

        # count = DWritePort_str(ser, "我是东小东，哈哈")
        # print("写入字节数：", count)
        # DReadPort() #读串口数据
        # DColsePort(ser)  #关闭串口
    else:
        print(mySerials.is串口成功打开)

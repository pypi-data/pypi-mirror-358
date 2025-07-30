from app_tools_zxw.SDK_硬件读写.进制转换 import convert_int_16进制, convert_16进制str_intList, convert_16进制_str, \
    convert_intList_二进制16位字符串, convert_Bytes_Str, convert_IntList_16进制Str
from app_tools_zxw.SDK_硬件读写.crc16 import *
from app_tools_zxw.SDK_硬件读写.串口_网口_通讯封装.网口读写.app级应用封装 import 通过网口读写设备
from typing import List


class LED通讯(通过网口读写设备):
    # LED屏幕分区
    __LED屏更新区域 = {
        0: {"areaID": 0, "宽高": [16, 0x80, 16, 0], "XY": [0, 0x80, 0, 0]},
        1: {"areaID": 1, "宽高": [48, 0x80, 16, 0], "XY": [16, 0x80, 0, 0]},
        2: {"areaID": 2, "宽高": [64, 0x80, 16, 0], "XY": [0, 0x80, 16, 0]}
    }

    @staticmethod
    def __生成包头(中间命令: List[int]):
        # 包头
        包头 = [0xA5, 0xA5, 0xA5, 0xA5, 0xA5, 0xA5, 0xA5, 0xA5]
        包头 += [1, 0x00]  # 屏地址
        包头 += [0x01, 0x80]  # 源地址
        包头 += [0x00, 0x00, 0x00]
        包头 += [0x00]
        # 校验模式
        # 校验值共两个字节当该字节为0时，采用CRC16方式
        # 当该字节为1时，采用和校验的方式，仅保留最低位两个字节，采用小端模式
        # 当该字节为2时，无校验，校验字节可以为任意值
        包头 += [0]
        # 显示模式
        # 0x00：普通模式，动态区与节目可同时显示，但各区域不可重叠。
        # 0x01：动态模式，优先显示动态区，无动态区则显示节目，动态区与节目区可重叠。
        包头 += [0x00]
        包头 += [0x61, 0x02]  # 设备类型,协议版本号
        包头数据域长度 = convert_16进制str_intList(convert_int_16进制(len(中间命令)), 输出位数=2, 逆序=True)
        #
        return 包头 + 包头数据域长度 + 中间命令

    @classmethod
    def __生成包尾(cls, data: List[int]):
        # crc16校验
        cmd_16str = ""
        for i in data[8:]:
            cmd_16str += convert_int_16进制(i)
        crc = crc16_ibm(cmd_16str).upper().replace(" ", "")

        # 正确值：0xA8, 0x7D
        if len(crc) == 4:
            crcInt = [int(crc[2:], 16), int(crc[:2], 16)]
        elif len(crc) == 2:
            crcInt = [int(crc, 16), 0]
        elif crc == "0":
            crcInt = [0, 0]
        else:
            crcInt = [0, 0]
            print("CRC值不为1/2/4位：", crc)

        # 添加
        data += crcInt
        # 包尾
        data.append(0x5A)
        #
        return data

    @staticmethod
    def __字符转义(data: List[int]):
        newCMD = data[0:8]
        for i in data[8:-1]:
            if i == 0xA5:
                newCMD += [0xA6, 0x02]
            elif i == 0xA6:
                newCMD += [0xA6, 0x01]
            elif i == 0x5A:
                newCMD += [0x5B, 0x02]
            elif i == 0x5B:
                newCMD += [0x5B, 0x01]
            else:
                newCMD += [i]
        newCMD += data[-1:]
        return newCMD

    @classmethod
    def __生成包头和尾并转义(cls, 中间命令: List[int]):
        cmd = cls.__生成包头(中间命令)
        cmd = cls.__生成包尾(cmd)
        cmd = cls.__字符转义(cmd)
        return cmd

    def ping(self):
        cmd = [0xA5, 0xA5, 0xA5, 0xA5, 0xA5, 0xA5, 0xA5, 0xA5, 0x01, 0x00, 0x00, 0x80, 0x00,
               0x00, 0x00, 0x00, 0x00, 0x00, 0xFE, 0x02, 0x05, 0x00, 0xA2, 0x00, 0x01, 0x00,
               0x00, 0x68, 0xF8, 0x5A]
        # 转换发送命令：二进制字符串
        req = self.写入数据_整数列表命令(cmd)
        return req

    def 修改亮度(self, 亮度: int):
        """
        @params:亮度: 1-16
        """
        命令 = [0xA3, 0x02, 0x01, 0x00, 0x00, 0x01, 亮度] + [0x01] * 48
        data = self.__生成包头(命令)
        data = self.__生成包尾(data)
        self.写入数据_整数列表命令(data)

    def 清屏(self):
        cmd = [0xA5, 0xA5, 0xA5, 0xA5, 0xA5, 0xA5, 0xA5, 0xA5
            , 0x01, 0x00, 0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFE, 0x02, 0x05, 0x00
            , 0xA3, 0x10, 0x01, 0x00, 0x00, 0x51, 0xF8, 0x5A]
        isOK, _ = self.写入数据_整数列表命令(cmd)
        # print("清屏结果 = ", _)

    def 修改ip地址(self, ip: List[int], port: int = 5005, 子网掩码: List[int] = [255, 255, 255, 0],
               默认网关: List[int] = [192, 168, 0, 1]):
        cmd = [0xA4, 0x05, 0x01, 0x00, 0x00]
        # 控制器连接模式：
        # 0x00 – 单机直连（PC 与控制器直接连接）
        # 0x01 – 自动获取 IP（DHCP）
        # 0x02 – 手动设置 IP（Static IP）
        # 0x03 – 服务器模式（动态 IP）
        cmd += [0x00]
        # ip等
        cmd += ip + 子网掩码 + 默认网关 + convert_16进制str_intList(convert_int_16进制(port), 输出位数=2, 逆序=True)
        cmd = self.__生成包头和尾并转义(cmd)
        cmd[8:11] = convert_16进制str_intList("FEFF00")
        print(convert_IntList_16进制Str(cmd))

    def 修改文字(self, text: str, 更新区域: int = -1, color: int = 0, speed: int = 10,
             显示方式: int = 3, 特技停留时间: int = 0, 动态区运行模式: int = 0, is初始化=False,
             自动换行: bool = False, 多行显示: bool = False) -> (bool, any):
        """
        注释
        @param text: 待显示的文字
        @param color: 0,1,2
        @param 动态区运行模式: 0~5
        @param 更新区域: 0-2
        @param speed: 0-255
        @param 特技停留时间: 0-255
        @param is初始化: 是否清除区域
        @param 自动换行: True / False
        @param 多行显示: True / False
        @param 显示方式: 0x01——静止显示，0x02——快速打出，0x03——向左移动，0x04——向右移动，0x05——向上移动，0x06——向下移动
        @return: str,硬件返回的二进制结果
        """
        if 更新区域 in [0, 1, 2]:
            cmd = self._修改文字_生成命令(text, color=color, speed=speed, 显示方式=显示方式,
                                  特技停留时间=特技停留时间, is初始化=is初始化, is删除所有动态区=is初始化,
                                  动态区运行模式=动态区运行模式, 自动换行=自动换行, 多行显示=多行显示,
                                  更新区域编号=self.__LED屏更新区域.get(更新区域).get("areaID"),
                                  更新区域坐标=self.__LED屏更新区域.get(更新区域).get("XY"),
                                  更新区域宽高=self.__LED屏更新区域.get(更新区域).get("宽高"))
        else:
            cmd = self._修改文字_生成命令(text, color=color, speed=speed,
                                  显示方式=显示方式, 特技停留时间=特技停留时间, 动态区运行模式=动态区运行模式,
                                  is初始化=is初始化, is删除所有动态区=is初始化,
                                  自动换行=自动换行, 多行显示=多行显示)

        isOK, _ = self.写入数据_整数列表命令(cmd)
        if not isOK:
            print(convert_IntList_16进制Str(cmd))
        return isOK, _

    @classmethod
    def _修改文字_生成命令(cls, text, color=0, speed=0, 显示方式=1, 特技停留时间=5, 动态区运行模式=3,
                   自动换行=False, 多行显示=False, is初始化=False, is删除所有动态区=False,
                   更新区域编号=4,
                   更新区域坐标: List[int] = [0, 0, 0, 0],
                   更新区域宽高: List[int] = [64, 0, 32, 0]):
        # 文字转换
        if color == 0:  # 红色
            text = "\C1" + text
        elif color == 1:  # 绿色
            text = "\C2" + text
        elif color == 2:  # 黄色
            text = "\C3" + text

        text_编码 = text.encode("gb2312")
        text_编码_list = [i for i in text_编码]
        #
        命令, 区域数据 = [], []
        # 命令
        命令 += [0xA3, 0x06, 0x01]  # 发送实时显示信息
        # 当该字节为 0 时，收到动态信息后不再进行清区域和初始化区域的操作，
        # 当该字节为 1 时，收到动态信息后需要进行清区域和初始化区域的操作。
        命令 += [0x01 if is初始化 else 0x00]
        命令.append(0x00)
        # 要删除的区域个数，0：不删除，FF：全部删除（ 此值为 0 则下一个参数“删除的区域 ID 号”不发送。
        命令 += [0x00 if not is删除所有动态区 else 0xFF]
        命令 += [0x01]  # 本次发送的动态区个数
        # 区域数据格式
        # 区域类型
        区域数据 += [0x00]
        # 动态区坐标
        区域数据 += 更新区域坐标
        # 动态区：宽，高
        # 默认以字节(8 个像素点)为单位
        # 高字节高位为 1 时，表示以像素点为单位
        区域数据 += 更新区域宽高
        区域数据 += [更新区域编号]  # 动态区域编号
        区域数据 += [0]  # 行间距
        # # 动态区运行模式:
        # # 0—动态区数据循环显示。
        # # 1—动态区数据显示完成后静止显示最后一页数据。
        # # 2—动态区数据循环显示，超过设定时间后数据仍未更新时不再显示
        # # 3—动态区数据循环显示，超过设定时间后数据仍未更新时显示 Logo 信息,Logo 信息即为动态区域的最后一页信息
        # # 4—动态区数据顺序显示，显示完最后一页后就不再显示
        # # 5—动态区数据顺序显示，超过设定次数后数据仍更新时不再显示
        区域数据 += [动态区运行模式]
        # # 动态区数据超时时间，单位为秒 / 次数
        区域数据 += [0x00, 0x00]
        区域数据 += [0x00, 0x00]  # 是否发送语音,拓展位个数
        # # 文本对齐方式
        # # 字体对齐方式/区域数据排版
        # # 行（上下左右）字对齐方式
        # # Bit1 Bit0
        # # 0 0 ----左对齐（左右 默认）
        # # 0 1 ----右对齐（左右）
        # # 1 0 ----居中对齐（左右）
        # # Bit3 Bit2 0 0 ----上对齐（上下 默认）
        # # 0 1 ----下对齐（上下）
        # # 1 0 ----居中对齐（上下）
        区域数据 += [0x00]
        # # 是否单行显示：01单行，02多行
        区域数据 += [0x02 if 多行显示 else 0x01]
        # # 是否自动换行：01不自动，02自动换
        区域数据 += [0x02 if 自动换行 else 0x01]
        # # 显示方式：0x01——静止显示，0x02——快速打出，0x03——向左移动，0x04——向右移动，0x05——向上移动，0x06——向下移动
        区域数据 += [显示方式]
        # # 退出方式
        区域数据 += [0x00]
        # # 显示速度
        区域数据 += [speed]
        # # 特技停留时间
        区域数据 += [特技停留时间]

        # 命令组合:计算数据长度，组合
        文本长度 = len(text_编码_list)
        文本长度 = convert_16进制str_intList(convert_int_16进制(文本长度), 输出位数=4, 逆序=True)
        # print(f"文本长度={convert_int_16进制(len(text_编码_list)), 文本长度}")
        #
        区域数据 = 区域数据 + 文本长度 + text_编码_list
        #
        动态区数据长度 = convert_16进制str_intList(convert_int_16进制(len(区域数据)), 输出位数=2, 逆序=True)
        # print(f"动态区数据长度={convert_int_16进制(len(区域数据)), 动态区数据长度}")
        命令 = 命令 + 动态区数据长度
        #
        # print(f"包头数据域长度={convert_int_16进制(len(命令 + 区域数据)), 包头数据域长度}")

        # 显示信息“012345QRSTTV’B”
        # text_编码_demo = [0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x51, 0x52, 0x53, 0x54, 0x54, 0x56, 0x27, 0x42]
        # print(f"text_编码_demo:{text_编码_demo}\ntext_编码_list:{text_编码_list}")
        # 整合
        data = cls.__生成包头(命令 + 区域数据)
        data = cls.__生成包尾(data)
        data = cls.__字符转义(data)
        return data


if __name__ == "__main__":
    import time
    import random

    ledx = LED通讯(timeout=1,ip="192.168.0.201")
    with ledx as ledHardware:
        ledHardware.修改亮度(10)

    # while True:
    #     发送失败次数 = 0
    #     while 发送失败次数 >= 0:
    #         with ledx as ledHardware:
    #             r = random.randint(0, 99)
    #             is发送成功, res = ledHardware.修改文字("●", color=r % 3, 更新区域=0, 显示方式=1)
    #             #
    #             r = random.randint(10000, 99999)
    #             is发送成功x, resx = ledHardware.修改文字(f"卡号{r}", color=r % 3, 显示方式=1,
    #                                              更新区域=1, speed=50)
    #             #
    #             r = random.randint(0, 99)
    #             is发送成功x, resx = ledHardware.修改文字(f"{r}吨sdadssww", color=r % 3, 显示方式=1,
    #                                              特技停留时间=0, 更新区域=2, speed=50)
    #             #
    #             time.sleep(0.1)
    #
    #             if is发送成功:
    #                 发送失败次数 = -1
    #             else:
    #                 time.sleep(1)
    #                 print(f"发送失败，{res},重新发送")

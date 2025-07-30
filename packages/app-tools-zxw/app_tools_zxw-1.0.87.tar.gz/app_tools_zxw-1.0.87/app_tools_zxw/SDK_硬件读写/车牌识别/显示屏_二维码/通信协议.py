from app_tools_zxw.SDK_硬件读写.进制转换 import *
from app_tools_zxw.SDK_硬件读写.车牌识别.显示屏_二维码.生成二维码 import make二维码
from app_tools_zxw.SDK_硬件读写.crc16 import crc16

"""
控制域：
    DA   0x00~0xff     1Bytes       设备地址
    VR   0x00~0xff     1Bytes       协议版本
    PN   0x0000~0xffff 2Bytes       16位包序列
数据域：
    CMD  0x00~0xff     1Byte        指令ID
    DL   0x0000~0xffff 1~2Bytes     数据长度
    DATA 0x00~0xff     最大255Bytes  数据
校验域：
    CRC  0x0000~0xffff 2Bytes        16位包校验值
"""

"""
指令集
    0xE1    扫码支付界面  SF + EM + ETM + ST + NI + TIME + MONEY + ML + TL + FLAGS + QRSIZE + RESERVED[15] + MSG[ML + 1] + TEXT[TL + 1]
    0xE5    扫码支付界面  SF + EM + ETM + ST + NI + VEN + TL + TEXT[TL] + BMPDATA [….]
    ACK(成功为 0，失败返回非 0 的值)
"""


def __生成指令头(cmd: str, DA="00", VR=100, PN="FFFF"):
    """"""
    """
    DA:为显示屏的地址，取值范围为 0x00 - 0xFF。
    VR:描述了协议版本号，目前支持版本 100 和版本 200。
    PN:是包的序列，在传输超过 255 个字节的数据时，需要分包传输，PN 表示了包的序列，每次交
    互完之后自增 1，设置为最大值 0XFFFF 时表示当前包是最后一个包。在传输小于 255 个字节的
    数据时，该值应该设置为 0XFFFF。
    CMD: 该字段描述了该包的作用，显示屏通过这个值完成不同的功能服务。
    DL: 该字段用来描述 DATA 的数据长度，当 VR 为 100 时，DL 只有 1 个字节，最大取值为 255。 当 VR 为 200 时，DL 为 2 个字节组成 16 位数据,最大取值为 65535。
    DATA: 是参数数据，每条指令携带的参数和长度是不同的，详解参见后指令集章节。
    CRC: 数据包的校验码。参与校验的字段是从 DA 到 DATA 的最后一个字节。校验算法采用 CRC16，见后章节详解
    """
    VR = convert_int_16进制(VR)
    return DA + VR + PN + cmd


def 根据字符串显示二维码(二维码字符串="http://www.baidu.com", 文本字符串="please scan", 二维码尺寸=1, 界面显示时间=10):
    """"""
    """
    请求格式: DA + VR + PN[2] + 0xE1+ DL + SF + EM + ETM + ST + NI + TIME + MONEY + ML + TL + FLAGS + QRSIZE + RESERVED[15] + MSG[ML + 1] + TEXT[TL + 1] + CRC[2]
    请求参数描述:
        SF: 显示标志，1 为显示，0 为不显示。
        EM: 进入模式，保留赋值为 0(无操作)。
        ETM:退出模式，保留赋值为 0(无操作)。
        ST:界面的显示时间，单位为秒，0 为一直显示。
        NI:下一个界面的索引号，目前保留取值为 0.
        TIME:停车时间(目前没有用到)，单位为秒，32 位数据类型，小端模式。
        MONEY:收费金额(目前没有用到)，单位为 0.1 元，32 位数据类型，小端模式。
        ML:二维码信息长度。
        TL:文本信息长度。
        FLAGS:标志域，最高位为 1 时，表示携带文本信息，否则可以不携带文本信息；最低位为 1 时表示同时播报语音。
        常用的组合是,0X80 不播报语音，0X81 显示及播报语音。
        QRSIZE:二维码尺寸，取值为 0 时表示 49X49 的像素，取值为 1 时表示 32X32 的像素。
        RESERVED:保留的 15 个字节
        MSG:二维码字符串，包含最后结束符。
        TEXT:文本信息字符串，包含最后结束符
    回复格式: DA + VR + PN[2] + 0xE1+ DL + ACK + CRC[2]
    """

    header = __生成指令头("E1")
    #
    num0_hex16 = convert_int_16进制(0)
    num1_hex16 = convert_int_16进制(1)

    SF = num1_hex16
    EM = ETM = NI = num0_hex16
    FLAGS = "80"
    ST = convert_int_16进制(界面显示时间)
    RESERVED = 15 * "00"
    MSG = convert_str_16进制(二维码字符串) + "00"
    TEXT = convert_str_16进制(文本字符串) + "00"
    TIME = convert_int_16进制(0) + convert_int_16进制(0) + convert_int_16进制(0) + convert_int_16进制(0)
    MONEY = convert_int_16进制(0) + convert_int_16进制(0) + convert_int_16进制(0) + convert_int_16进制(0)
    ML = convert_int_16进制(len(二维码字符串).encode("gb2312"))
    TL = convert_int_16进制(len(文本字符串).encode("gb2312"))
    QRSIZE = convert_int_16进制(二维码尺寸)
    #

    DATA = SF + EM + ETM + ST + NI + TIME + MONEY + ML + TL + FLAGS + QRSIZE + RESERVED + MSG + TEXT
    DL = convert_int_16进制(int(len(DATA) / 2))

    return (header + DL + DATA + crc16(header + DL + DATA)).upper()


def 绘制二维码_绘图模式(二维码字符串="http://www.baidu.com", 文本字符串="please scan", 二维码尺寸=3, 界面显示时间=10):
    """
    :param 二维码字符串:
    :param 文本字符串:
    :param 二维码尺寸:  只能为3或者7
    :param 界面显示时间:
    :return:
    """
    """
    请求参数描述:
        SF: 显示标志，1 为显示，0 为不显示。
        EM: 进入模式，保留赋值为 0(无操作)。
        ETM:退出模式，保留赋值为 0(无操作)。
        ST:界面的显示时间，单位为秒，0 为一直显示。
        NI:下一个界面的索引号，目前保留取值为 0.
        VEN:语音播报开关，为 0 不播报语音，为 1 播报语音。
        TL:显示文本长度。
        TEXT:文本信息字符串。
        BMPDATA:二维码单色位图数据,只支持 LEVEL3(29X29)和 LEVEL7(45X45)的二维码位图。29X29 为 2 行屏显示，45X45 为 4 行屏显示。
        回复格式: DA + VR + PN[2] + 0xE5+ DL[2] + ACK + CRC[2]
        回复参数描述: 包含 1 个字节的参数，DL 取值为 1，ACK 是显示屏返回的结果，取值为 0 表示成
        功，非 0 表示不成功。
    """
    header = __生成指令头("E5", VR=200)
    #
    SF = convert_int_16进制(1)
    EM = ETM = NI = convert_int_16进制(0)
    ST = convert_int_16进制(界面显示时间)
    VEN = convert_int_16进制(0)
    TEXT = convert_str_16进制(文本字符串)
    TL = convert_int_16进制(len(文本字符串.encode("gb2312")))
    BMPDATA = make二维码(txt=二维码字符串, size_level=二维码尺寸).decode()
    #
    DATA = SF + EM + ETM + ST + NI + VEN + TL + TEXT + BMPDATA
    DL = convert_int_16进制(int(len(DATA) / 2))
    DL = DL + (len(DL.zfill(4)) - len(DL)) * "0"
    print("DL = ", DL)
    #
    return (header + DL + DATA + crc16(header + DL + DATA)).upper()


if __name__ == '__main__':
    dataDemo = "00 64 FF FF E1 41 01 00 00 0A 00 00 00 00 00 0000 00 00 14 0B 80 01 00 00 00 00 00 00 00 0000 00 00 00 00 00 00 68 74 74 70 3A 2F 2F 7777 77 2E 62 61 69 64 75 2E 63 6F 6D 00 70 6C65 61 73 65 20 73 63 61 6E 00 D5 24 ".replace(
        " ", "")
    #
    print(绘制二维码_绘图模式())

import qrcode
import io
import binascii


def make二维码(txt="http://www.baidu.com", size_level=3) -> bytes:
    """
    :param txt:
    :param size_level: 只能是3或者7
    :return:
    """
    # 调用qrcode的make()方法传入url或者想要展示的内容
    img = qrcode.make(txt, version=size_level, border=0, box_size=1)

    # 写入文件
    with open("test.bmp", "wb") as f:
        img.save(f, format="BMP")

    # 读取成16进制字符串
    im_bytes = io.BytesIO()
    img.save(im_bytes, format="BMP")
    print(im_bytes.getvalue())
    im_hex = binascii.hexlify(im_bytes.getvalue())
    #
    return im_hex


def convert_bmp16_int(data):
    t = convert_16进制_Bytes(data)
    tmp = [str(int(i)).zfill(3) for i in t]
    return tmp


if __name__ == '__main__':
    # print(make二维码(size_level=3))

    data = make二维码(txt = "http://www.baidu.com", size_level=3).decode()
    from 进制转换 import *

    dataDemoBMP = "424DB2000000000000003E000000280000001D000000E3FFFFFF01000100000000000000000000000000000000000000000000000000FFFFFF0000000000FEF773F882911208BA4442E8BA1992E8BA999AE882EEEA08FEAAABF800C45800E6DDCF9871889318526EF76825BBAC003EE66B08E4267B384631154805E45D80CE9DCB4825A89A78C68EF208193BB100CB867FD000A668E8FE510A8882E458D0BA3DDF88BA688DD0BAAEE09882DBADC0FEE67A88"

    print(convert_bmp16_int(dataDemoBMP))
    print(convert_bmp16_int(data))

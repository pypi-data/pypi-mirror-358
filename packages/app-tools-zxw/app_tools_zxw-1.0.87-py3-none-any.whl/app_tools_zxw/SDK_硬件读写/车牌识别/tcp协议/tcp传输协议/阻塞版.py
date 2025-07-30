from socket import *
import struct
import math
import json

def send_data(session: socket, data: str) -> int:
    """"""
    """ 发送数据，若成功，则返回发送胡数据长度"""
    # 计算传输头
    dataLen = len(data)

    headerList = [b'V', b'Z', 0, 0, dataLen >> 24 & 0xFF, dataLen >> 16 & 0xFF, dataLen >> 8 & 0xFF, dataLen & 0xFF]
    header = struct.pack("<ccBBBBBB", *headerList)
    # print("传输头：", headerList)

    # 传输数据
    session.send(header)
    tmp = session.send(data.encode())
    #
    return tmp


def receive_data(session: socket) -> dict:
    """"""
    """ 接受数据 """
    headerBytes = session.recv(8)

    # 解析数据头
    try:
        header = struct.unpack("<ccBBBBBB", headerBytes)
        数据长度 = int(header[4] << 24) + int(header[5] << 16) + int(header[6] << 8) + int(header[7])

        # 读取数据
        if 数据长度 < 1000:
            data = session.recv(数据长度)
        else:
            data = b""
            for i in range(1,int(math.ceil(数据长度/1000))+1):
                if  数据长度 - i*1000 >= 0:
                    lens = 1000
                else:
                    lens = 数据长度 - i*1000

                data = data + session.recv(lens)
    except:
        print(headerBytes)
        data = headerBytes
    return data
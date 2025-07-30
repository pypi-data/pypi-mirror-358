import struct

async def send_data(session, data: str) -> int:
    """"""
    """ 发送数据，若成功，则返回发送胡数据长度"""
    # 计算传输头
    dataLen = len(data)

    headerList = [b'V', b'Z', 0, 0, dataLen >> 24 & 0xFF, dataLen >> 16 & 0xFF, dataLen >> 8 & 0xFF, dataLen & 0xFF]
    header = struct.pack("<ccBBBBBB", *headerList)
    # print("传输头：", headerList)

    # 传输数据
    await session.send(header)
    tmp = await session.send(data.encode())
    #
    return tmp


async def receive_data(session) -> dict:
    """"""
    """ 接受数据 """
    headerBytes = await session.recv(8)

    # 解析数据头
    header = struct.unpack("<ccBBBBBB", headerBytes)
    数据长度 = int(header[4] << 24) + int(header[5] << 16) + int(header[6] << 8) + int(header[7]) + 100
    # print("解析的数据头 = ", header, "数据长度 = ", 数据长度)

    # 读取数据
    if 数据长度 < 1024:
        data = await session.recv(数据长度)
    else:
        raise ValueError("接受长度超过1024请循环接受")


    return data
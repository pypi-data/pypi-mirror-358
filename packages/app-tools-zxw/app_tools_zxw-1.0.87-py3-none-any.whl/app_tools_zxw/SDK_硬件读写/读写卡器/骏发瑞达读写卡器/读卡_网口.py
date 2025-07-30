import datetime
from app_tools_zxw.SDK_硬件读写.进制转换 import *
from app_tools_zxw.SDK_硬件读写.串口_网口_通讯封装.网口读写.app级应用封装 import 通过网口读写设备


class readUHF卡(通过网口读写设备):
    """
    1B 39 01 00 12 00 10 81 30 00 AA BB 20 16 03 01 10 80 A0 00 A0 01 00 (00) xx
    """
    读取字节长度 = 25
    心跳包 = ["1B2001FF01000101", "1B2001FF01000303"]

    # 覆写 - 定义返回数据格式（re）
    def _接受校验(self, d: str) -> bool:
        # 1B 39 01 FF 12 00 10 D4 30 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 F4
        # 1b3901ff120010d430000000000000000000000000000000f4
        d = d.upper()
        # 过滤心跳包
        if len(d) > 0:
            if d in self.心跳包:
                return True
        #
        验证1 = len(d) == self.读取字节长度 * 2
        if not 验证1:
            return False
        # 结构/命令 验证
        验证2 = d[:6] == "1B3901"
        验证3 = d[12:14] == "10"
        # 传输正确性验证:BCC校验
        data = convert_16进制str_intList(d)
        sum = 0
        for i in data[6:-1]:
            sum += i
        验证4 = sum == data[-1]
        # print(验证1, 验证2, 验证3, 验证4)
        return 验证1 and 验证2 and 验证3

    # 覆写 - 数据提取与转换
    def _提取数据(self, origin16Data: str):
        # 设备心跳包
        if origin16Data.upper() in self.心跳包:
            return "心跳包"

        # 16进制数据转换
        data16 = origin16Data[20: 44]
        print(f"data16={len(data16), data16}")
        finalData = convert_16进制_int(data16)
        print(datetime.datetime.now(), "  读取到的卡号 = ", finalData)
        print("__________________________________________")
        return finalData


if __name__ == "__main__":
    import asyncio
    import threading
    from app_硬件通信.webSocket客户端.main import websocket链接
    from configs import *

    cardReader = readUHF卡(ip="192.168.0.190", port=5005)


    async def 员工_转ws格式(cardID: int) -> str:
        return f"{cardID}"


    url = f"ws://{服务ip}:{服务端口}/cardID"
    myWS_员工读卡 = websocket链接(url)
    cardReader员工 = readUHF卡(ip="192.168.0.190", port=5005)

    threading.Thread(target=asyncio.run,
                     args=[myWS_员工读卡.持续获取硬件信息_并实时通过websocet传递(cardReader员工.持续get数据并转发, 员工_转ws格式)]).start()

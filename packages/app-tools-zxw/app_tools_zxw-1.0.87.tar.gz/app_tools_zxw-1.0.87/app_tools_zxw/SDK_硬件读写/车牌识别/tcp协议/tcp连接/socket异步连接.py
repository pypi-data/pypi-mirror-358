import asyncio
from app_tools_zxw.SDK_硬件读写.车牌识别.tcp协议.tcp传输协议 import receive_data, send_data


# 异步读写按socket格式打包一下
class _clientSocket:
    def __init__(self, writer: asyncio.StreamWriter, reader: asyncio.StreamReader):
        self.writer = writer
        self.reader = reader

    async def send(self, data: bytes):
        self.writer.write(data)
        await self.writer.drain()

    async def recv(self, lens: int):
        data = await self.reader.read(lens)
        return data

# 连接tcp服务器，并处理
class socketConnection:
    发送心跳包 = True
    cmdData = ""
    responsData = ""

    async def init(self):
        # 连接服务器
        serverName = '192.168.3.100'
        serverPort = 8131
        #
        reader, writer = await asyncio.open_connection(serverName, serverPort)
        self.clientSocket = _clientSocket(writer=writer, reader=reader)
        await self.__保持线程()

    async def __保持线程(self):
        while True:
            if self.发送心跳包:
                await send_data(self.clientSocket,"")
                print("发送心跳包...")
                await asyncio.sleep(delay=1)
            else:
                self.responsData = ""
                await send_data(self.clientSocket, self.cmdData)
                self.responsData = await receive_data(self.clientSocket)
                self.发送心跳包 = True

    async def send_cmd(self, data: str):
        self.发送心跳包 = False
        self.cmdData = data

    async def get_response(self):
        #
        times = 1
        while not self.responsData:
            asyncio.sleep(0.2)
            times += 1
            if times > 500:break
        #
        res = self.responsData
        self.responsData = ""
        return res


if __name__ == '__main__':
    socks = socketConnection()
    socks.init()
    asyncio.get_event_loop().run_until_complete(socketConnection().send_cmd())

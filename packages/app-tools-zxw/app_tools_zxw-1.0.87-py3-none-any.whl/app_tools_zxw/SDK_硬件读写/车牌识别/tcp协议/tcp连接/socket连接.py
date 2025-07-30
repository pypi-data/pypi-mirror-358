from socket import *
from app_tools_zxw.SDK_硬件读写.车牌识别.tcp协议.tcp传输协议.阻塞版 import receive_data, send_data


class socketConnection:
    def __enter__(self):
        return self

    def __exit__(self, type, value, trace):
        self.clientSocket.close()

    def __init__(self,ip="192.168.3.100",port=8131):
        # 连接服务器
        serverName = ip
        serverPort = port
        #
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((serverName, serverPort))

        self.clientSocket = clientSocket


    def send_cmd(self, data: str):
        return send_data(self.clientSocket, data)

    def get_response(self):
        data = receive_data(self.clientSocket)
        return data


if __name__ == '__main__':
    socketConnection()

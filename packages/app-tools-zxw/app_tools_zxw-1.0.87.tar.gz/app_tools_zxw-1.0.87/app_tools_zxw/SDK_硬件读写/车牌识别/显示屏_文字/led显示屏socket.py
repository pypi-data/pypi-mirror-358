import json
from socket import *
from app_tools_zxw.SDK_硬件读写.车牌识别.显示屏_文字.set屏显文字 import cmd空闲, cmd获取屏显文字
from app_tools_zxw.SDK_硬件读写.车牌识别.tcp协议.tcp传输协议.阻塞版 import send_data, receive_data

# 定义传输数据
data = cmd空闲
data = json.dumps(data)

# 连接服务器
serverName = '192.168.1.100'
serverPort = 8131
ADDR = (serverName, serverPort)

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect(ADDR)

# 数据传输
while True:
    if not data:
        break
    # 发送数据
    是否发送成功 = send_data(clientSocket, data)
    print("发送是否成功：", 是否发送成功)
    # 接受数据
    returnData = receive_data(clientSocket)
    print(returnData)
    #
    if returnData:
        send_data(clientSocket,json.dumps(cmd获取屏显文字))
        print(receive_data(clientSocket))
        break

clientSocket.close()

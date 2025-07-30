# -*- coding: utf-8 -*-
import serial
from serial.tools import list_ports
# 获取串口列表
port_list = list(list_ports.comports())
print(port_list)
if len(port_list) == 0:
    print('无可用串口')
else:
    for i in range(0,len(port_list)):
        print(port_list[i])

# 打开串口
serialPort = "COM3"  # 串口
baudRate = 9600  # 波特率
ser = serial.Serial(serialPort, baudRate, timeout=0.5)
print("参数设置：串口=%s ，波特率=%d" % (serialPort, baudRate))

# 收发数据
while 1:
    str = input("请输入要发送的数据（非中文）并同时接收数据: ")
    ser.write((str + '\n').encode())
    print(ser.readline())  # 可以接收中文
    ser.close()

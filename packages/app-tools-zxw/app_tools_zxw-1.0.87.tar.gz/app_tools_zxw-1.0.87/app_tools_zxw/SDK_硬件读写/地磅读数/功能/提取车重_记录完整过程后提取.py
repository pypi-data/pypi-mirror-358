import asyncio
import time
from app_tools_zxw.SDK_硬件读写.串口_网口_通讯封装.串口读写.app应用级封装 import serial串口读写设备
from app_硬件通信.func_led出入指示 import LED文字指示系统

录入系统的最低重量 = 50  # 小轿车重1450KG
测量间隔 = 0.01
超时退出 = 20
重量过程_最低有效长度 = 4
led文字指示 = LED文字指示系统()


async def 提取车重(read地磅数据: serial串口读写设备, 车辆方向is出: bool):
    """
    return:
        -99   ：串口通信失败
        -999  ：车辆未长时间未上磅
        -1234 : 车辆行驶过快
    """
    # return 1234

    串口通信成功次数 = 0
    开始时间 = time.time()
    重量变化过程 = [0]
    print("等待车辆上磅")

    # 等待车辆上磅
    while True:
        # 0 异常退出
        if time.time() - 开始时间 >= 超时退出:
            if 串口通信成功次数 < 超时退出 * 0.1:
                print(f"串口通信失败，成功次数{串口通信成功次数},超时退出:{超时退出},测量间隔{测量间隔}")
                return -99
            else:
                return -999

        # 1 读取地磅实时重量
        当前重量 = read地磅数据.单次get数据()
        if 当前重量 != -99:
            串口通信成功次数 = 串口通信成功次数 + 1
        #
        if 当前重量 > 录入系统的最低重量:
            重量变化过程.append(当前重量)
            break
        #
        await asyncio.sleep(测量间隔)

    # 录入上磅过程
    while True:
        # 1 读取地磅实时重量
        当前重量 = read地磅数据.单次get数据()
        # 2 录入过磅重量过程
        if 当前重量 > 录入系统的最低重量:
            print("车辆过磅中..当前重量 = ", 当前重量)
            重量变化过程.append(当前重量)
            if len(重量变化过程) > 重量过程_最低有效长度:
                led文字指示.led出入指示(is出=车辆方向is出, 状态=2, 重量=当前重量)
        # 3 车辆下磅
        elif 当前重量 != -99 and 当前重量 >= 0:
            break
        # 4 测量间隔
        await asyncio.sleep(测量间隔)

    # 提取车辆重量
    if len(重量变化过程) < 重量过程_最低有效长度:
        return -1234

    # 提取车重
    return max(重量变化过程)

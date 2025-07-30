import asyncio
import datetime
from app_tools_zxw.SDK_硬件读写.串口_网口_通讯封装.串口读写.app应用级封装 import serial串口读写设备
from app_硬件通信.func_led出入指示 import LED文字指示系统

总读数次数上限 = 20
连续重量相等次数_判定阈值 = 2
录入系统的最低重量 = 1000  # 小轿车重1450KG
测量间隔 = 0.5
led文字指示 = LED文字指示系统()


# 新增方法
async def 提取车辆稳定后重量(read地磅数据: serial串口读写设备, 车辆方向is出: bool):
    前一秒重量 = 0
    重量相等的连续次数 = 0
    待选的实际重量 = []
    读数总次数 = 0
    while True:
        读数总次数 = 读数总次数 + 1
        # 1 读取地磅实时重量
        当前重量 = read地磅数据.单次get数据()
        print(f"{datetime.datetime.now()},当前重量 = {当前重量}")

        # 2 记录地磅稳定读数的持续时常
        if 当前重量 == 前一秒重量 and 当前重量 > 录入系统的最低重量:
            重量相等的连续次数 = 重量相等的连续次数 + 1
        else:
            重量相等的连续次数 = 0

        # 3 持续时常超过阈值：则记录为车辆实际重量
        if 重量相等的连续次数 >= 连续重量相等次数_判定阈值:
            待选的实际重量.append(当前重量)

        # 4 退出读数
        if len(待选的实际重量) > 0:
            最终真实重量 = max(待选的实际重量)
            return 最终真实重量

        # 5 异常退出
        else:
            if 读数总次数 > 总读数次数上限:
                return -99
            # 5 更新数据
            前一秒重量 = 当前重量

        # 6 测量间隔
        await asyncio.sleep(测量间隔)

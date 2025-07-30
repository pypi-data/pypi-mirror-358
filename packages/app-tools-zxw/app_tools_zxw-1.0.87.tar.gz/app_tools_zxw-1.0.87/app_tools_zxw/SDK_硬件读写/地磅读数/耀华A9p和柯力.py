from app_tools_zxw.SDK_硬件读写.串口_网口_通讯封装.串口读写.app应用级封装 import serial串口读写设备
from app_tools_zxw.SDK_硬件读写.根据始末标志位提取数据 import get_data
import time

"""
空 0 
接受到的数据 =  52983525027.888
验证通过，开始提取数据 =  022b30303030303030314203
提取的数据 : data16 = 303030303030, 小数点位数 = 30
十进制数据=52983525027888,小数点位数=48

车 1560KG
接受到的数据 =  52983542134.32
验证通过，开始提取数据 =  022b30303135363030313903
提取的数据 : data16 = 303031353630, 小数点位数 = 30
十进制数据=52983542134320,小数点位数=48

车+人 1650KG
接受到的数据 =  52983542199.6
验证通过，开始提取数据 =  022b30303136353030313903
提取的数据 : data16 = 303031363530, 小数点位数 = 30
十进制数据=52983542199600,小数点位数=48
"""


class read地磅(serial串口读写设备):
    # 覆写 - 参数配置
    波特率 = 1200
    读取字节长度 = 12 * 4

    # 覆写 - 定义返回数据格式（re）
    def _接受校验(self, d: str) -> bool:
        d = d.upper()
        data = get_data(data=d, start="02", end="03", data_les=int(self.读取字节长度 / 2))
        #
        if data is None:
            return False
        else:
            return True

    # 覆写 - 数据提取与转换
    def _提取数据(self, origin16Data: str) -> float:
        # 根据始末特征数提取完整数据
        origin16Data = get_data(data=origin16Data, start="02", end="03", data_les=int(self.读取字节长度 / 2))
        # print("验证通过，开始提取数据 = ", origin16Data)
        # 开始位数 = 2*（n-1）, 结束位数 = 2*（n-1）+ 数据长度 , 链表内结束index = 结束位数
        正负号 = origin16Data[2:4]
        data16 = origin16Data[(3 - 1) * 2: (3 - 1) * 2 + 6 * 2]
        小数点位数 = origin16Data[(3 - 1) * 2 + 6 * 2: (3 - 1) * 2 + 6 * 2 + 2]
        # 数据转换
        finalData = self.__读数转换(data16)
        小数点位数int = self.__读数转换(小数点位数)
        #
        # print(f"重量数据 :{data16}, 小数点位数： {小数点位数}")
        # print(f"重量数据={finalData},小数点位数={小数点位数int}，{(10 ** 小数点位数int)}")
        # print(正负号)
        # print("__________________________________________")
        if 正负号 == "2b":
            return finalData / (10 ** 小数点位数int)
        else:
            return - finalData / (10 ** 小数点位数int)

    # 新增方法
    @staticmethod
    def __读数转换(data="303031353630") -> int:
        newData = ""
        for i in range(len(data)):
            if i % 2 != 0:
                newData = newData + data[i]
        #
        return int(newData)


if __name__ == '__main__':
    from configs import weight_地磅端口

    weightCOM = read地磅(端口=weight_地磅端口)
    while True:
        print(weightCOM.单次get数据())
        time.sleep(0.6)

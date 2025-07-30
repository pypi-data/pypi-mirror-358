cmd_init = {"cmd": "ttransmission", "id": "1", "subcmd": "init", "data": "rs485-1"}  # rs485-1
cmd_uninit = {"cmd": "ttransmission", "id": "3", "subcmd": "uninit"}

""""""
import json
import base64
from app_tools_zxw.SDK_硬件读写.车牌识别.tcp协议.tcp连接.socket连接 import socketConnection
from app_tools_zxw.SDK_硬件读写.车牌识别.显示屏_二维码.通信协议 import 根据字符串显示二维码, 绘制二维码_绘图模式


class 相机透传命令:
    send_cmd = {"cmd": "ttransmission", "id": "1", "subcmd": "send", "datalen": 6, "data": "QUJDREVG",
                "comm": "rs485-1"}

    def __init__(self):
        self.conn = socketConnection(ip="192.168.1.100")

    def __del__(self):
        self.conn.clientSocket.close()

    def send一条tcp命令(self, __cmd: dict):
        # 发送指令
        id = __cmd.get("id", None)
        x = self.conn.send_cmd(json.dumps(__cmd))
        # 接受第一条返回值
        res = self.conn.get_response()
        # 循环接受返回值，直到返回值的id匹配
        if id is not None:
            try:
                resid = json.loads(res).get("id", None)
            except:
                resid = None
            #
            while resid != str(id):
                res = self.get_data()
                try:
                    resid = json.loads(res).get("id", None)
                except:
                    resid = None
        #
        print("成功发送：{}, 接受结果：{}".format(x, res))
        return res

    def send_透传16进制二维码数据(self, data_16进制: str):
        # 整理数据
        data_bytes = base64.b16decode(data_16进制)
        dataBase64 = base64.b64encode(data_bytes).decode()
        dataLens = int(len(data_bytes))
        print("透传16进制指令，dataLens = {},  data = {}".format(dataLens, dataBase64))
        #
        self.send_cmd["id"] = str(int(self.send_cmd["id"]) + 1)
        if int(self.send_cmd["id"]) > 9999:
            self.send_cmd["id"] = "1"

        self.send_cmd["datalen"] = dataLens
        self.send_cmd["data"] = dataBase64
        #
        self.send一条tcp命令(self.send_cmd)

    def get_data(self):
        res = self.conn.get_response()
        print(res)
        return res


if __name__ == '__main__':
    # 数据
    # data = 根据字符串显示二维码(二维码字符串="http://www.baidu.com/", 文本字符串="please scan", 界面显示时间=20)
    data = 绘制二维码_绘图模式(二维码字符串="http://www.bing.com/", 文本字符串="首次入场请微信扫描二维码绑定手机号", 界面显示时间=50, 二维码尺寸=3)
    #
    # dataDemo = "00 C8 FF FF E5 C4 00 01 00 00 14 00 80 0B 70 6C 65 61 73 65 20 73 63 61 6E 42 4D B2 00 00 00 00 00 00 00 3E 00 00 00 28 00 00 00 1D 00 00 00 E3 FF FF FF 01 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF 00 00 00 00 00 FE F7 73 F8 82 91 12 08 BA 44 42 E8 BA 19 92 E8 BA 99 9A E8 82 EE EA 08 FE AA AB F8 00 C4 58 00 E6 DD CF 98 71 88 93 18 52 6E F7 68 25 BB AC 00 3E E6 6B 08 E4 26 7B 38 46 31 15 48 05 E4 5D 80 CE 9D CB 48 25 A8 9A 78 C6 8E F2 08 19 3B B1 00 CB 86 7F D0 00 A6 68 E8 FE 51 0A 88 82 E4 58 D0 BA 3D DF 88 BA 68 8D D0 BA AE E0 98 82 DB AD C0 FE E6 7A 88 5A 80 ".replace(" ", "")
    # print("16data      = ", data)
    # print("dataDemo    = ", dataDemo)
    #
    camera透传 = 相机透传命令()
    # 初始化
    camera透传.send一条tcp命令(cmd_init)
    # 设置屏幕二维码
    camera透传.send_透传16进制二维码数据(data)
    #
    # camera透传.__del__()

import serial
import serial.tools.list_ports
import threading
from time import sleep


class EletronicScale(object):
    """
    称重仪
    """

    def __init__(self):
        self.com = None
        self.serial = None
        self.off = None

    def open_port(self):
        if self.off != None and self.off != False:
            print("已连接请勿重复连接")
            return
        try:
            self.port_list = list(serial.tools.list_ports.comports())
            for prot in self.port_list:
                if prot.vid == 6790:
                    self.com = prot.device
            if self.com != None:
                self.serial = serial.Serial(self.com, 9600, timeout=0.5)
                self.off = True
                t = threading.Thread(target=self.xunhuanjieshoushuju)
                t.start()
                print("连接成功")
            else:
                print("请连接称重仪")
        except Exception as e:
            raise e

    def xunhuanjieshoushuju(self):
        while True:
            if self.off is False:
                break
            data = self.serial.read_all()
            if len(data) > 10:
                print("Weight%d" % (float(data.decode("utf8")[1:8])))
                sleep(0.02)

                # def threading_data(self):
                #     t = threading.Thread(target=self.xunhuanjieshoushuju)
                #     t.start()

    def close_port(self):
        self.off = False
        sleep(0.3)
        self.serial.close()
        print("关闭成功")


if __name__ == '__main__':
    ele = EletronicScale()
    ele.open_port()
    ele.serial.isOpen()
    t = threading.Thread(target=ele.xunhuanjieshoushuju)
    t.start()
    while True:
        cur = int(input("1111"))
        if cur == 2:
            ele.off = False
            sleep(0.3)
            ele.close_prot()

            print("关闭端口")
            print(t.is_alive())
        if cur == 1:
            ele.off = True
            ele.open_port()
            t = threading.Thread(target=ele.xunhuanjieshoushuju)
            t.start()
            print("开启线程")
            print(t.is_alive())

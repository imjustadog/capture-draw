import struct
import threading
import time
from dataparse import GetData

BUFSIZE = 1024

class PCIeHost():
    def __init__(self):
        self.cap_data = GetData()
        self.__exit = False
        self.generating = True

    def startthread(self):
        self.__exit = False
        self.tData = threading.Thread(name="dataGenerator", target=self.receivedata)
        self.tData.start()

    def releasethread(self):
        self.__exit = True

    def receivedata(self):
        while True:
            if self.__exit:
                break
            #fb = open("/dev/xillybus_read_32", "rb")
            fb = open("D:/xillybus_read_32.txt", "rb")
            x = 0
            while True:
                data = fb.read(4)
                if not data:
                    break
                ch1, ch2 = struct.unpack('<HH', data)
                # ch1 = (float(ch1) - 8192) / 8192 * 2.5
                # ch2 = (float(ch2) - 8192) / 8192 * 2.5
                ch1 = float(ch1)
                ch2 = float(ch2)
                self.cap_data.datalist[0]['datay'].append(ch1)
                self.cap_data.datalist[1]['datay'].append(ch2)
                self.cap_data.datalist[0]['datax'].append(x)
                self.cap_data.datalist[1]['datax'].append(x)
                x = x + 1
                if x > 500:
                    break
            fb.close()
            if self.generating:
                self.cap_data.signal_realtimedata_emitter()
            time.sleep(1)

from socket import *
import struct
import threading
from datetime import datetime
import time

BUFSIZE = 1024

class TcpServer:
    def __init__(self):
        self.__exit = False
        setdefaulttimeout(1)

    def setremote(self, ip, port):
        self.HOST = ip    # The remote host
        self.PORT = port              # The same port as used by the server

    def open(self):
        ADDR = (self.HOST, self.PORT)
        self.tcpSerSock = socket(AF_INET, SOCK_STREAM)
        try:
            self.tcpSerSock.bind(ADDR)
        except error, msg:
            print msg
        try:
            self.tcpSerSock.listen(1)
        except error, msg:
            print msg

    def startthread(self):
        self.tData = threading.Thread(name="dataGenerator", target=self.receivedata)
        self.tData.start()

    def releasethread(self):
        self.__exit = True
        self.tcpSerSock.close()

    def receivedata(self):
        while True:
            try:
                tcpCliSock, addr = self.tcpSerSock.accept()
            except error, msg:
                # print "accept err"
                continue
            while True:
                try:
                    data = tcpCliSock.recv(BUFSIZE)
                    if not data:
                        break
                    print data
                except error, msg:
                    # print "receive err"
                    pass
            tcpCliSock.close()

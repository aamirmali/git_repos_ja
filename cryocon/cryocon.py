import numpy as np
import socket
import time

class Cryocon:
    """class that intitializes and controls the cryocon """
    ip_add=None
    """ip address of cryocon """
    port=None
    """port that cryocon listens on"""
    def __init__(self, ip_add="192.168.1.5",port=5000):
        self.ip_add=ip_add
        self.port=port
        self.s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.res_val=np.zeros(1)
    def connect(self):
        self.s.connect((self.ip_add,self.port))

    def send(self,message):
        self.s.send(message)
    def recv(self, buff_size=1024):
        data=self.s.recv(buff_size)
        return data
    def idn(self, comm='*IDN?\n'):
        self.send(comm)
        data=self.recv()
        return data
    def temp(self, comm='inp A:temp?\n'):
        self.send(comm)
        data=self.recv()
        return data
    def time(self, comm='system:time?\n'):
        self.send(comm)
        data=self.recv()
        return data
    def close(self):
        self.s.close()
    def daq_cc(self):
        while True:
#            start=time.time()
            time.sleep(0.001)
            try:
                temp_cc=float(self.temp().split('\r')[0])
            except ValueError:
                self.res_val[0]=self.res_val[0]
                print "Value Error cryocon"
            else:
                self.res_val[0]=temp_cc
#            stop=time.time()
#            print "res cryocon=", stop-start

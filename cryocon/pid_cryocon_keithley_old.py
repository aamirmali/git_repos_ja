import keithley
import time
import numpy as np

class PID:
    """This class initializes, starts and stops a PID temperature control loop using the cryocon readout as input and the keithly current source as control"""
    file_cryocon=None
    """binary data file containg cryocon measurments """
    def __init__(self,res_val,setpoint=0,P=0,I=0,D=0,factor=1e-9,keithley='Keithley1'):
        self.res_val=res_val
        self.setpoint=setpoint
        self.P=P
        self.I=I
        self.D=D
        self.factor=factor
    def get_error(self):
        error=self.res_val-self.setpoint
        return error
    def calc_PID(self,err_buf):
        value=self.factor*(self.P*err_buf[0]+self.I*np.mean(err_buf)+self.D*(err_buf[1]-err_buf[0]))
        return value

    def set_curr_value(self,value):
        print 'resistance=', self.res_val
        print 'pid value to apply=', value
        print 'time=', time.time()
        time.sleep(4)
        return 0

    def start_PID(self,num=10):
        err_buf=np.zeros(num)
        while True:
            for i in range(num-1):
                err_buf[i+1]=err_buf[i]
            err_buf[0]=self.get_error()
            value=self.calc_PID(err_buf)
            self.set_curr_value(value)
            time.sleep(0.1)

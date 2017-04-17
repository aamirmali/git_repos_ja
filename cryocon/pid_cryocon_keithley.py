import numpy as np

class PID:
    """This class initializes, starts a PID temperature control loop calculation using the cryocon readout"""
    file_cryocon=None
    """binary data file containg cryocon measurments """
    def __init__(self,res_val,setpoint=0,P=0,I=0,D=0,factor=1e-9):
        self.res_val=res_val
        self.setpoint=setpoint
        self.P=P
        self.I=I
        self.D=D
        self.factor=factor
        self.pid_value=0
    def get_error(self):
        error=self.res_val-self.setpoint
        return error
    def calc_PID(self,err_buf):
        value=self.factor*(self.P*err_buf[0]+self.I*np.mean(err_buf)+self.D*(err_buf[0]-err_buf[1]))
        return value


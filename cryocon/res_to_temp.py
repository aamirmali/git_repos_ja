import numpy as np

class Res2temp:
    """Converts resistance measurement to temperature given a calibration table """
    calib_table=None
    """calibration table, 2d numpy array resistance,temperature """
    def __init__(self,filename_calib):
        self.filename_calib=filename_calib
        self.array_calib=np.genfromtxt(self.filename_calib)
        self.R=self.array_calib[:,0]
        self.T=self.array_calib[:,1]
        if not np.all(np.diff(self.R) > 0):
            raise Exception("Error: not all resistance values are ncreasing ")
    def get_temp(self, res):
        temp=np.interp(res,self.R,self.T)
        return temp
    def get_res(self, temp):
        res=np.interp(temp,self.T[::-1],self.R[::-1])
        return res
    def giveT(self,res):
        """
        Gives the temperature specified channel
        in accordance with Linghzhen's code
        """
        r = res
        Z = np.log10(r)
        ZL = 1.66182687794
        ZU = 5.44937964961
        k = ((Z-ZL) - (ZU-Z))/(ZU-ZL)
        A = [0.307806, -0.418601, 0.236946, -0.123511, 0.060647, -0.029181,
             0.013858, -0.006252, 0.003088, -0.001497, 0.000467, -0.000026]
        A = np.array(A)
        Temp = 0.0
        ack = np.arccos(k)
        T = np.cos(ack*np.arange(12))
        Temp = np.sum(T*A)
#        for i in range(0,12):
#            Temp = Temp + A[i]*np.cos((i)*np.arccos(k))
#        Temp = Temp*1000
        return Temp

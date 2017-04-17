import numpy as np

class Qband_param:
    def __init__(self):
        self.num_cols=8
        self.num_rows=11
        self.Rsh=np.array([250.,250.,250.,250.,250.,250.,250.,250.,250.])*1e-6
#        self.filtgain=2048.
        self.filtgain=1216.
        self.dac_bits=14
        self.M_ratio=np.array([24.6,24.6,24.6,24.6,24.6,24.6,24.6,24.6,24.6])
        self.Rfb=np.array([5100.,5100.,5100.,5100.,5100.,5100.,5100.,5100.,5100.])
        self.db_bits=15
        self.Rdetb=np.array([573.,573.,573.,573.,573.,573.,573.,573.,573.])
        self.fb_DAC_volts=1.0
        self.db_DAC_volts=5.0
        self.index_normal=50
        self.bias_lines =np.array([0,1,2,3,4,5,6,7])
        self.buff=8 # number of points around target index to avg/median to get TES parameter value
        self.PRn_low=np.array([0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3])
        self.PRn_high=np.array([0.6,0.6,0.6,0.6,0.6,0.6,0.6,0.6])
        self.bias_DAC_default=1000
        self.thres_jump=1e7

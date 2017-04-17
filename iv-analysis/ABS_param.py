import numpy as np

class ABS_param:
    def __init__(self):
        self.num_cols=24
        self.num_rows=22
        self.Rshunt_cols=np.array([148,157,153,147, 151,168,149,165,146,144,160,170,148,170,172,149, 161,146,147,148,149,165,150,149])*1e-6
        self.filtgain=1311.
        self.dac_bits=14
        self.M_ratio=8.5
        self.Rfb=7080.
        self.db_bits=16
        self.Rdetb=582.
        self.fb_DAC_volts=1.0
        self.db_DAC_volts=2.5
        self.index_normal=100
        self.bias_lines =np.array([1,0,1,3, 6,4,7,6,6,7,7,4,5,5,4,5, 2,3,3,2,2,0,0,1])
        self.num=8

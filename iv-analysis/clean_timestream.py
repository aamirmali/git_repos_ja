import numpy as np

class Clean:
    data=None
    '''input timestream of one detector'''
    def __init__(self, thres_jump=1000000):
        self.thres_jump=thres_jump

    def data_fix_jumps(self,data):
        diff=np.diff(data)
        index_jump=np.where(np.abs(diff) > self.thres_jump)[0]
        for i in index_jump:
            data[i+1:]=data[i+1:]-diff[i]
        return data

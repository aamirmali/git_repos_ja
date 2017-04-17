import numpy as np

class Vphi:
    '''Analysis vphi from mce acquisition'''
    data=None
    ''' raw vphi data for a single channel'''
    def __init__(self, data, smooth_num=10):
        self.data=data
        self.smooth_num=smooth_num

    def smooth_vphi(self):
        d=self.data-np.mean(self.data)
        num=self.smooth_num
        size=len(d)
        s_vphi=np.zeros(size/num)
        for i in np.arange(size/num):
            s_vphi[i]=np.median(d[i*num:(i+1)*num])
        return s_vphi
    def find_period(self):
        d=self.smooth_vphi()
        slope=np.diff(d)
        neg_slope=np.where(slope < 0)
        pos_slope=np.where(slope > 0)
        neg_per=np.max(np.diff(neg_slope))
        pos_per=np.max(np.diff(pos_slope))
        period=neg_per+pos_per
        num=self.smooth_num
        return period*num, neg_per*num,pos_per*num


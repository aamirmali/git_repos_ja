import numpy as np
import mce_data
import array_ABS_cfg as config
def read_ascii(filename, data_start=0, comment_chars=[]):
    data = []
    for line in open(filename):
        w = line.split()
        if len(w) == 0 or w[0][0] in comment_chars: continue
        data.append([float(x) for x in w])
    return np.array(data).transpose()


class CheckIvs:

    """This class checks iv data to find the detectors that work
    """
    minlen_nbranch=None
    min_slope=None
    max_slope=None
    darksquid_std_thres=None
    iv_statuses=None
    def __init__ (self,datafile,minlen_nbranch=50,min_slope=1e2,max_slope=1e4,
                  darksquid_std_thres=300,verbose=True):
        mce=mce_data.SmallMCEFile(datafile)
        self.data=mce.Read(row_col=True).data
        #iterate through columns and flip as appropriate
        for col in range(0,self.data.shape[1]):
            self.data[:,col]=config.fb_normalize[col]*self.data[:,col]
	self.bias_data=read_ascii(datafile+'.bias',comment_chars=['<','#'])[0]
	self.bias_step=np.abs(self.bias_data[0]-self.bias_data[1])
        self.nrows=self.data.shape[0]
        self.ncols=self.data.shape[1]
        #initialize self.iv_statuses to nrows*ncols list of None
        self.iv_statuses=[]
        for i in range(self.nrows):
            col_vals=[]
            for j in range(self.ncols):
                col_vals.append(None)
            self.iv_statuses.append(col_vals)
        self.minlen_nbranch=minlen_nbranch
        self.min_slope=min_slope
        self.max_slope=max_slope
        self.darksquid_std_thres=darksquid_std_thres
        self.verbose=verbose

        #John, your coding style is atrocious. 

    def dDac_dbias(self,row,col,restrict=True):
        if restrict==True:
            branch=self.data[row,col,0:self.minlen_nbranch]
        if restrict==False:
            branch=self.data[row,col]
        result=(branch[1:]-branch[:-1])/self.bias_step
        return result
    
    def iv_good(self,row,col):
        whole_data_slope_std=np.std(self.dDac_dbias(row,col,restrict=False))
        slope=np.median(self.dDac_dbias(row,col))
        std_slope=np.std(self.dDac_dbias(row,col))
        if whole_data_slope_std==0:
            self.iv_statuses[row][col]='off'
        elif whole_data_slope_std<self.darksquid_std_thres:
            self.iv_statuses[row][col]='darksquid'
        elif slope<0:
            self.iv_statuses[row][col]='incomplete'
        elif slope>self.min_slope and slope<self.max_slope and std_slope<slope:
            self.iv_statuses[row][col]='good'
        elif slope>self.max_slope:
            self.iv_statuses[row][col]='ramping'
        else:
            self.iv_statuses[row][col]='undefined'
        if self.iv_statuses[row][col]!='good' and self.verbose==True:
            print "Row ",row," Col", col, self.iv_statuses[row][col]
            
    def col_iv_good(self,col):
        for i in range(0,self.nrows):
            self.iv_good(i,col)
    def row_iv_good(self,row):
        for i in range(0,self.ncols):
            self.iv_good(row,i)
    def array_iv_good(self):
        for i in range(0,self.ncols):
            for j in range(0,self.nrows):
                self.iv_good(j,i)

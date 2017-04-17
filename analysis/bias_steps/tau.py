import numpy as np
import matplotlib.pyplot as plt
import code.common.filehandler as fh
import scipy.optimize as opt

class Tau:
    ''' fits for tau from an averaged time stream of steps '''
    data=None
    '''Single tes bias step time stream '''
    samp_freq=None
    '''sampling frequency'''
    def __init__(self, data, samp_freq):
        self.data=data-np.mean(data)
        self.samp_freq=samp_freq
        self.samp_rate=1./samp_freq
    def find_step_index(self):
        tes=self.data
        index_pos=np.where(tes > 0)[0]
        index_neg=np.where(tes < 0)[0]
        return index_pos, index_neg
    def find_step_index2(self):
        tes=self.data
        index_pos=np.where(np.diff(tes) > 100000)[0]
        index_neg=np.where(np.diff(tes) < -100000)[0]
        return index_pos, index_neg
    def avg_steps(self,step_width_max=1,offset_index=80):
        index_pos,index_neg=self.find_step_index()
#        print index_pos, index_neg
        dindex_pos=np.diff(index_pos)
        dindex_neg=np.diff(index_neg)
#        print dindex_pos,dindex_neg
        step_index_pos=np.where(dindex_pos > step_width_max)[0]
        step_index_neg=np.where(dindex_neg > step_width_max)[0]
#        print step_index_pos,step_index_neg
        template_neg=self.data[index_pos[step_index_pos[0]:step_index_pos[1]]]
        template_pos=self.data[index_pos[step_index_neg[0]:step_index_neg[1]]]
        step_len_neg=len(template_neg)
        step_len_pos=len(template_pos)
        print step_len_neg,step_len_pos
        avg_step_pos=np.zeros(step_len_pos)
        avg_step_neg=np.zeros(step_len_neg)
        i=0
        for step in step_index_pos[:-1]:
#            print index_pos[step],index_pos[step]+step_len_neg
            data_offset=self.data[index_pos[step]:index_pos[step]+step_len_neg]
            offset=np.median(data_offset[offset_index:])
            if offset < 0:
                data_neg=data_offset-offset
                avg_step_neg=avg_step_neg+data_neg
            i=i+1
        i=0
        for step in step_index_neg[:-1]:
#            print index_neg[step],index_neg[step]+step_len_pos
            data_offset=self.data[index_neg[step]:index_neg[step]+step_len_pos]
            offset=np.median(data_offset[offset_index])
            if offset > 0:
                data_pos=data_offset-offset
                avg_step_pos=avg_step_pos+data_pos
            i=i+1
        print i
        return avg_step_pos, avg_step_neg
    def avg_steps2(self,step_width_max=1,offset_index=80):
        index_pos,index_neg=self.find_step_index2()
        print index_pos, index_neg
        template=self.data[index_pos[0]:index_pos[1]]
        step_len=len(template)/2
        print step_len
        avg_step_pos=np.zeros(step_len)
        avg_step_neg=np.zeros(step_len)
        i=0
        for step in index_neg[:-1]:
#            print index_pos[step],index_pos[step]+step_len_neg
            data_offset=self.data[step:step+step_len]
            offset=np.median(data_offset[offset_index:])
            if offset < 0:
                data_neg=data_offset-offset
                avg_step_neg=avg_step_neg+data_neg
            i=i+1
        i=0
        for step in index_pos[:-1]:
#            print index_neg[step],index_neg[step]+step_len_pos
            data_offset=self.data[step:step+step_len]
            offset=np.median(data_offset[offset_index])
            if offset > 0:
                data_pos=data_offset-offset
                avg_step_pos=avg_step_pos+data_pos
            i=i+1
        print i
        return avg_step_pos, avg_step_neg


    def tau_fit(self,avg_data,offset=7):   
        time=(np.arange(len(avg_data[offset:]))+offset)*1./self.samp_freq
        def func(A,tau,time):
            res=A*np.exp(-time*tau)
            return res
        def err(x,data,time):
            error=func(x[0],x[1],time)-data
            return error
        xo=[1000,27]
        res=opt.leastsq(err,xo,args=(avg_data[offset:],time))
        param=res[0]
        print param
        return 1.0/param[1]





#fig=plt.figure(1)

#ax=fig.add_subplot(111)


#time_complete=(np.arange(len(tes)))*1./411.

#ax.plot(time_complete,tes)
#ax.plot(tes)


#ax.plot(time_complete,func(param[0],param[1],time_complete),'r')
#ax.plot(time,func(param[0],param[1],time),'g')

#G=66.6
#G=81

#C=G/param[1]

#print 'G (pW/K)=',np.round(G,1)
#print 'C (pJ/K)=',np.round(C,2)

#plt.show()

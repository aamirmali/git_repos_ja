import numpy as np
import matplotlib.pyplot as plt
import code.common.filehandler as fh
import scipy.optimize as opt

#filename='/data/cryo/20130624/det_on_4000_185mK_step_v1'
#filename='/data/cryo/20130624/det_on_5000_192mK_steps_v1'
#filename='/data/cryo/20130624/det_on_2500_100_193mK_step_v1'
filename='/data/cryo/20130624/det_on_2500_50_193mK_step_v1'

data=fh.get_mce_data(filename, row_col=True)

#tes=data[14,2,1056:1256]
#tes=data[2,2,15653:15900]
#tes=data[2,2,1202:1402]
tes=data[2,2,1333:1531]

tes_offset=np.mean(tes[80:])

tes=tes-tes_offset

offset=7

time=(np.arange(len(tes[offset:]))+offset)*1./411.

def func(A,tau,time):
    res=A*np.exp(-time*tau)
    return res

def err(x,data,time):
    error=func(x[0],x[1],time)-data
    return error

xo=[1000,27]
res=opt.leastsq(err,xo,args=(tes[offset:],time))
param=res[0]
print param

fig=plt.figure(1)

ax=fig.add_subplot(111)


time_complete=(np.arange(len(tes)))*1./411.

ax.plot(time_complete,tes)
#ax.plot(tes)


ax.plot(time_complete,func(param[0],param[1],time_complete),'r')
ax.plot(time,func(param[0],param[1],time),'g')

G=66.6
G=81

C=G/param[1]

print 'G (pW/K)=',np.round(G,1)
print 'C (pJ/K)=',np.round(C,2)

plt.show()

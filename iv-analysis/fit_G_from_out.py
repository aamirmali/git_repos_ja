import numpy as np
import matplotlib.pyplot as plt
import filehandler as fh
from test_param import param
import glob
import scipy.optimize as opt
from matplotlib.backends.backend_pdf import PdfPages


dirname='/data/cryo/20150924/'
file_arr_raw=glob.glob(dirname+'iv_*_v1.out')
file_arr=[]
n=4
temp_offset=30
for filename in file_arr_raw:
    temp=int(filename.split('iv_')[1].split('mK')[0])-temp_offset#modified temp
    print temp
    if temp > 100:
        file_arr.append(filename)

def Psat_func(K,Tc,Tb,n=n):
    Psat=K*(Tc**n-Tb**n)
    return Psat
def err(x,temp,Psat):
    error=(Psat_func(x[0],x[1],temp)-Psat)
    return error
xo=[1e-8,0.15]

def G_fit(err_func,xo,temp,Psat):
    res=opt.leastsq(err,xo, args=(temp,Psat))
    param=res[0]
    G=param[0]*n*param[1]**(n-1)
    G150=param[0]*n*0.15**(n-1)
    K=param[0]
    Tc=param[1]
    return K,Tc,G,G150
    


test=param()


ntemps=len(file_arr)

Psat=np.zeros([test.num_rows,test.num_cols,ntemps])
PRn=np.zeros([test.num_rows,test.num_cols,ntemps])
Rtes=np.zeros([test.num_rows,test.num_cols,ntemps])
K=np.zeros([test.num_rows,test.num_cols])
Tc=np.zeros([test.num_rows,test.num_cols])
G=np.zeros([test.num_rows,test.num_cols])
G150=np.zeros([test.num_rows,test.num_cols])
Rn=np.zeros([test.num_rows,test.num_cols])
temps=np.zeros(ntemps)

i=0
for filename in file_arr:
    temps[i]=int(filename.split('iv_')[1].split('mK')[0])-temp_offset#modified temp
    Psat[:,:,i]=fh.IV_data_to_arr(filename,'Psat')
    PRn[:,:,i]=fh.IV_data_to_arr(filename,'PRn')
    Rtes[:,:,i]=fh.IV_data_to_arr(filename,'Rtes')
    i=i+1

fig3=plt.figure(30)

for col in np.arange(test.num_cols):
    for row in np.arange(test.num_rows):
        if Psat[row,col,0] < 50 and Psat[row,col,0] > 0:
            if row >= 0 and col >= 0:
                ax=fig3.add_subplot(2,2,col+1)
                ax.plot(temps,Psat[row,col,:], 'o')
            x=G_fit(err,xo,temps*1e-3,Psat[row,col,:]*1e-12)
            K[row,col]=x[0]
            Tc[row,col]=x[1]
            G[row,col]=x[2]
            G150[row,col]=x[3]
            num=0
            Rn_sum=0
            for i in np.arange(len(file_arr)):
                if PRn[row,col,i] > 0 and PRn[row,col,i] < 100:
                    Rn_sum=Rn_sum+100.*Rtes[row,col,i]/PRn[row,col,i]
                    num=num+1.0
            if num ==0:
                Rn[row_col]=0
            else:
                Rn[row,col]=Rn_sum/num
            print col,row,x
f=open(dirname+'G_20150924.out','w')
fh.printout('kappa_nW/K^4',K*1e9,f)
fh.printout('Tc_K',Tc,f)
fh.printout('G@Tc_nW/K^4',G*1e9,f)
fh.printout('G@150mK_nW/K^4',G150*1e9,f)
fh.printout('Rn_mohms',Rn,f)
f.close()
fig1=plt.figure(1,figsize=(10,8))
ax1=fig1.add_subplot(221)
ax2=fig1.add_subplot(222)
ax3=fig1.add_subplot(223)
ax4=fig1.add_subplot(224)
ax1.set_xlabel('kappa (nW/K^4)')
ax2.set_xlabel('Tc (K)')
ax3.set_xlabel('G@Tc nW/K')
ax4.set_xlabel('G@150mK nW/K')
ax1.hist(K.flatten()*1e9,bins=10,range=(20,35))
ax2.hist(Tc.flatten(),bins=10,range=(0.155,0.199))
ax3.hist(G.flatten()*1e9,bins=10,range=(0.35,0.8))
ax4.hist(G150.flatten()*1e9,bins=10,range=(0.25,0.49))
ax1.set_ylim([0,20])
ax2.set_ylim([0,20])
ax3.set_ylim([0,20])
ax4.set_ylim([0,20])

#pp=PdfPages("/data/cryo/20150730/hist_G_ivs_20150730_v4.pdf")
#pp.savefig(fig1)
#pp.close()
plt.savefig(dirname+"hist_G_ivs_20150924_30mK_Toffset.png")
#plt.show()
print temps
print np.median(K[K > 0])
print np.median(Tc[ Tc > 0])
print np.median(G[ G > 0])
print np.median(G150[ G150 > 0])

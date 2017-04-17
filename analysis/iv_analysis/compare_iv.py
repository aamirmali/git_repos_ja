import numpy as np
import matplotlib.pyplot as plt
import argparse
import iv
import code.common.filehandler as fh
import scipy.optimize as opt
from scipy.interpolate import interp1d

parser=argparse.ArgumentParser(description= 'analyses group of ivs and plots results', formatter_class=argparse.ArgumentDefaultsHelpFormatter,fromfile_prefix_chars='@')

parser.add_argument('--filenames', type=str,nargs='*',help='list of IV filenames to analyze')
parser.add_argument('--row', type=int,  help='row to be analyzed and plotted')
parser.add_argument('--col', type=int,  help='row to be analyzed and plotted')
parser.add_argument('--Rsh', type=float, default=180e-6,  help='shunt value for calibration')
parser.add_argument('--G', type=float, default=65e-12,  help='G guess or known for alpha')
parser.add_argument('--To', type=float, default=195e-3,  help='To guess or know for alpha')
parser.add_argument('--num', type=int, default=10,  help='number of alpha measurments to avarage per bin')
parser.add_argument('--temp', type=float, nargs='*',  help='temperature for each iv file')
parser.add_argument('--index', type=int, default=20,  help='max index for normal branch')
parser.add_argument('--PsatRn', type=float, default=0.8,  help='%Rn where we measure Psat')
parser.add_argument('--polarity', type=float, default=-1,  help='polarity of FB due to wering')
args=parser.parse_args()


filenames=args.filenames
Rsh=args.Rsh
G=args.G
To=args.To
index_normal=args.index
num=args.num
row=args.row
col=args.col
temp=args.temp
Psat_Rn=args.PsatRn
polarity=args.polarity

def running_median(data,num):
    data_med=[]
    for j in np.arange(len(data)/num):
        data_med.append(np.median(data[j*num:(j+1)*num]))
    return data_med

fig=plt.figure(1)
ax1=fig.add_subplot(211)
ax2=fig.add_subplot(212)


data1=fh.get_mce_data(filenames[0],row_col=True)
data2=fh.get_mce_data(filenames[1],row_col=True)
data_tes1=polarity*data1[row,col,:]# negative due to polarite
data_tes2=polarity*data2[row,col,:]# negative due to polarite
db_bias1=np.genfromtxt(filenames[0]+'.bias',skiprows=1)
db_bias2=np.genfromtxt(filenames[0]+'.bias',skiprows=1)
tes1=iv.IV(data_tes1,db_bias1,Rsh)
tes2=iv.IV(data_tes2,db_bias2,Rsh)
Ites1,Vtes1,Rtes1,Ptes1=tes1.IV_calib(index_normal)
Ites2,Vtes2,Rtes2,Ptes2=tes2.IV_calib(index_normal)
ax1.plot(Vtes1,Ites1)
ax1.plot(Vtes2,Ites2)
ax1.set_ylim([0,2*Ites1[0]])
ax2.plot(Ptes1,Rtes1)
ax2.plot(Ptes2,Rtes2)
ax2.set_ylim([0,1.2*Rtes1[0]])
ax2.set_xlim([0,1.2*Ptes1[0]])

fig=plt.figure(2)
ax3=fig.add_subplot(111)

def alpha(G, Tc,P,I,dTb,dV):
    print I, dV
    alpha=G*Tc/P*1/(1+(G*dTb/(I*dV)))
    return alpha

dTb=temp[1]-temp[0]

dItes1=np.diff(Ites1)
index1_turn=np.where(dItes1 > 0)[0][10]
print index1_turn
index1_sc=index1_turn+np.where(dItes1[index1_turn:] < 0)[0][0]
print index1_sc
dItes2=np.diff(Ites2)
index2_turn=np.where(dItes2 > 0)[0][10]
index2_sc=index2_turn+np.where(dItes2[index2_turn:] < 0)[0][0]

Ites1_trans=Ites1[index1_turn:index1_sc]
Vtes1_trans=Vtes1[index1_turn:index1_sc]
Ites2_trans=Ites2[index2_turn:index2_sc]
Vtes2_trans=Vtes2[index2_turn:index2_sc]

spline_Vtes2=interp1d(Ites2_trans,Vtes2_trans,kind=2)

Array_alpha=[]
Array_Rtes=[]
i=0
for I in Ites1_trans:
    if I > np.min(Ites2_trans) and I < np.max(Ites2_trans):
        print i
        Pavg=I*Vtes1_trans[i]
        dV=spline_Vtes2(I)-Vtes1_trans[i]
        Array_alpha.append(alpha(G,To,Pavg,I,dTb,dV))
        Array_Rtes.append(Vtes1_trans[i]/I)
        i=i+1

ax3.plot(Array_Rtes,Array_alpha)


plt.show()

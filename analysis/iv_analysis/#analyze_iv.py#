import numpy as np
import matplotlib.pyplot as plt
import argparse
import iv
import code.common.filehandler as fh
import scipy.optimize as opt
from clean_timestream import Clean

parser=argparse.ArgumentParser(description= 'analyses group of ivs and plots results', formatter_class=argparse.ArgumentDefaultsHelpFormatter,fromfile_prefix_chars='@')

parser.add_argument('--filenames', type=str,nargs='*',help='list of IV filenames to analyze')
parser.add_argument('--title', type=str,default=None,help='title of analysis')
parser.add_argument('--row', type=int,  help='row to be analyzed and plotted')
parser.add_argument('--col', type=int,  help='row to be analyzed and plotted')
parser.add_argument('--Rsh', type=float, default=180e-6,  help='shunt value for calibration')
parser.add_argument('--G_guess', type=float, default=65e-12,  help='G guess or known for alpha')
parser.add_argument('--To_guess', type=float, default=195e-3,  help='To guess or know for alpha')
parser.add_argument('--num', type=int, default=10,  help='number of alpha measurments to avarage per bin')
parser.add_argument('--temp', type=float, nargs='*',  help='temperature for each iv file')
parser.add_argument('--index', type=int, default=20,  help='max index for normal branch')
parser.add_argument('--PsatRn', type=float, default=0.8,  help='%Rn where we measure Psat')
parser.add_argument('--polarity', type=float, default=-1,  help='polarity of FB signal')
parser.add_argument('--biastarget', type=float, default=0,  help='target bias to extract parameters')
parser.add_argument('--ABS',  action='store_true',  help='set to use abs parameters')
parser.add_argument('--plot',  action='store_true',  help='set to use abs parameters')
args=parser.parse_args()


filenames=args.filenames
if args.title != None:
    title=args.title
else:
    title=filenames[0]

Rsh=args.Rsh
G_guess=args.G_guess
To_guess=args.To_guess
index_normal=args.index
num=args.num
row=args.row
col=args.col
temp=args.temp
Psat_Rn=args.PsatRn
target_bias=args.biastarget
lw=5

def running_median(data,num):
    data_med=[]
    for j in np.arange(len(data)/num):
        data_med.append(np.median(data[j*num:(j+1)*num]))
    return data_med

fig=plt.figure(1)
ax1=fig.add_subplot(211)
ax2=fig.add_subplot(212)

fig=plt.figure(3)
ax4=fig.add_subplot(111)
#ax5=fig.add_subplot(312)
#ax6=fig.add_subplot(313)

Psat=np.zeros(len(temp))

i=0
for filename in filenames:
    print filename
    data=fh.get_mce_data(filename,row_col=True)
    data_tes=data[row,col,:]*args.polarity
    clean=Clean()
    data_tes=clean.data_fix_jumps(data_tes)
    db_bias=np.genfromtxt(filename+'.bias',skiprows=1)
    if args.ABS:
        tes=iv.IV(data_tes,db_bias,Rsh,filtgain=1311,Rfb=7080,Rdetb=582)
    else:
        tes=iv.IV(data_tes,db_bias,Rsh)
    Ites,Vtes,Rtes,Ptes,Ibias=tes.IV_calib(index_normal)
    Ibias_target=tes.detbias_dac_to_Ibias(target_bias)
    if Ibias_target > 0:
        index_target=np.where(Ibias < Ibias_target)[0][0]
        print Ibias[index_target],Ibias_target
        print 'Rtes target=',Rtes[index_target]
    else:
        index_target=0
    resp=tes.resp(index_normal)
    ax1.plot(Vtes*1e6,Ites*1e6,linewidth=lw)
    ax1.set_ylim([0,1.2*Ites[0]*1e6])
    ax1.set_ylabel('Ites (uA)')
    ax1.set_xlabel('Vtes (uV)')
    ax1.set_title(title)
    ax2.plot(Ptes*1e12,Rtes*1e3,linewidth=lw)
    ax2.set_ylim([0,1.2*Rtes[0]*1e3])
    ax2.set_xlim([0,1.2*Ptes[0]*1e12])
    ax2.set_xlabel('Ptes (pW)')
    ax2.set_ylabel('Rtes (mOhms)')
#    ax4.set_ylim([0,1.2*Vtes[0]])
    Rnormal=np.mean(Rtes[0:index_normal])
    index_Psat_Rn=np.where(Rtes/Rnormal < Psat_Rn)[0][0]
    Psat[i]=Ptes[index_Psat_Rn]
    i=i+1

    bias_dac_inf=tes.inflection_point(index_normal)
    print 'bias DAC inflection point=',bias_dac_inf
    alpha=tes.alpha(G_guess,To_guess,index_normal)
    Lin=tes.Lin(index_normal)
    print 'alpha target bias=',alpha[index_target]
    print 'Lin target bias=',Lin[index_target]
    resp_avg=running_median(resp,num)
    alpha_avg=running_median(alpha,num)
    Lin_avg=running_median(Lin,num)
    Rtes_avg=np.array(running_median(Rtes[1:],num))
    ax4.plot(Rtes_avg*1e3,alpha_avg,'o')
    ax4.plot(Rtes_avg*1e3,np.ones(len(Rtes_avg))*100,'r')
    ax4.set_xlim([0,1.0e3*Rtes[0]])
    ax4.set_ylim([-50,500])
    ax4.set_ylabel(r"$\alpha$")
    ax4.set_xlabel('Rtes (mOhms)')
    ax4.set_title(title)
#    ax5.plot(Rtes_avg,resp_avg,'o')
#    ax5.set_xlim([0,1.0*Rtes[0]])
#    ax6.plot(Rtes_avg,Lin_avg,'o')
#    ax6.set_xlim([0,1.0*Rtes[0]])

if Psat_Rn != 0:
    fig=plt.figure(2)
    ax3=fig.add_subplot(111)
    ax3.plot(temp,Psat,'o')
    ax3.set_ylim([0,Ptes[0]])
    n=4
    def Psat_func(K,Tc,Tb,n=n):
        Psat=K*(Tc**n-Tb**n)
        return Psat
    def err(x,temp,Psat):
        error=(Psat_func(x[0],x[1],temp)-Psat)
        return error
    xo=[1e-8,0.15]
    res=opt.leastsq(err,xo, args=(np.array(temp),np.array(Psat)))
    param=res[0]
    ax3.plot(temp,Psat_func(param[0],param[1],np.array(temp)))
    G=param[0]*n*param[1]**(n-1)
    G150=param[0]*n*0.15**(n-1)

    print 'row =', row
    print 'Rn =', np.round(Rnormal*1e3,1)
    print 'K (pW/K^n)=', np.round(param[0]*1e12,1)
    print 'Tc (K)=', np.round(param[1],3)
    print 'G@Tc pW/K=', np.round(G*1e12,1)
    print 'G@150mK pW/K=', np.round(G150*1e12,1)


if args.plot:
    plt.show()

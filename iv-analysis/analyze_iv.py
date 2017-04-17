import numpy as np
import matplotlib.pyplot as plt
import argparse
import iv
import filehandler as fh
import scipy.optimize as opt
from clean_timestream import Clean
from matplotlib.backends.backend_pdf import PdfPages


parser=argparse.ArgumentParser(description= 'analyses group of ivs and plots results', formatter_class=argparse.ArgumentDefaultsHelpFormatter,fromfile_prefix_chars='@')

parser.add_argument('--filenames', type=str,nargs='*',help='list of IV filenames to analyze')
parser.add_argument('--title', type=str,default=None,help='title of analysis')
parser.add_argument('--row', type=int,  help='row to be analyzed and plotted')
parser.add_argument('--col', type=int,  help='row to be analyzed and plotted')
parser.add_argument('--Rsh', type=float, default=180e-6,  help='shunt value for calibration')
parser.add_argument('--n', type=float, default=4,  help='power of T for G fit')
parser.add_argument('--G_guess', type=float, default=65e-12,  help='G guess or known for alpha')
parser.add_argument('--To_guess', type=float, default=195e-3,  help='To guess or know for alpha')
parser.add_argument('--num', type=int, default=10,  help='number of alpha measurments to avarage per bin')
parser.add_argument('--temp', type=float, nargs='*',  help='temperature for each iv file')
parser.add_argument('--index', type=int, default=20,  help='max index for normal branch')
parser.add_argument('--PsatRn', type=float, default=0.8,  help='%Rn where we measure Psat')
parser.add_argument('--polarity', type=float, default=-1,  help='polarity of FB signal')
parser.add_argument('--biastarget', type=float,nargs='*',  help='target bias to extract parameters')
parser.add_argument('--ABS',  action='store_true',  help='set to use abs parameters')
parser.add_argument('--mux11d',  action='store_true',  help='set to use mux11d parameters')
parser.add_argument('--blueforsQ',  action='store_true',  help='set to use blueforsQ parameters')
parser.add_argument('--plot',  action='store_true',  help='set to use abs parameters')
parser.add_argument('--saveplot',  type=str,default=None,  help='filepath and name where to save plots')
parser.add_argument('--fit_transition',  action='store_true',  help='set to fit transition')
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
target_bias=np.array(args.biastarget)
lw=5

def running_median(data,num):
    data_med=[]
    if num == 1:
        data_med=data
    else:
        for j in np.arange(len(data)/num):
            data_med.append(np.median(data[j*num:(j+1)*num]))
    return data_med

fig1=plt.figure(1)
ax1=fig1.add_subplot(211)
ax2=fig1.add_subplot(212)

fig3=plt.figure(3)
ax5=fig3.add_subplot(211)
ax4=fig3.add_subplot(212)
#ax5=fig.add_subplot(312)
#ax6=fig.add_subplot(313)

Psat=np.zeros(len(temp))

i=0
for filename in filenames:
    print '\n'
    print '\n'
    print filename
    print 'col=',col,'row=',row
    data=fh.get_mce_data(filename,row_col=True)
    data_tes=data[row,col,:]*args.polarity
    if np.median(np.diff(data_tes[0:index_normal])) > 0:
        data_tes=data_tes*-1
    clean=Clean()
    data_tes=clean.data_fix_jumps(data_tes)
    db_bias=np.genfromtxt(filename+'.bias',skiprows=1)
    if args.ABS:
        tes=iv.IV(data=data_tes,db_bias=db_bias,Rsh=Rsh,filtgain=1311,Rfb=7080,Rdetb=582, index_normal=index_normal, dac_bits=14, M_ratio=8.5, db_bits=16, fb_DAC_volts=1.0, db_DAC_volts=2.5)
    elif args.mux11d:
        tes=iv.IV(data_tes,db_bias,Rsh,filtgain=1218,Rfb=7830,Rdetb=519,M_ratio=25.5,index_normal=index_normal)
    elif args.blueforsQ:
        tes=iv.IV(data_tes,db_bias,Rsh,filtgain=1218.,Rfb=5120.,Rdetb=1292.,M_ratio=25.2,index_normal=index_normal )
# 20140408       tes=iv.IV(data_tes,db_bias,Rsh,filtgain=1218,Rfb=15050,Rdetb=2087,M_ratio=25.5, )
    elif row == 9:
        tes=iv.IV(data_tes,db_bias,Rsh,filtgain=1218.,Rfb=15166.,Rdetb=518.,M_ratio=4.6,index_normal=index_normal)
    else:
        tes=iv.IV(data_tes,db_bias,Rsh,filtgain=1218.,Rfb=15166.,Rdetb=518.,M_ratio=8.5,index_normal=index_normal)
    Ites,Vtes,Rtes,Ptes,Ibias=tes.Ites,tes.Vtes,tes.Rtes,tes.Ptes,tes.Ibias
    resp=tes.resp
    Rnormal=np.mean(Rtes[0:index_normal])
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
    index_Psat_Rn_array=np.where(Rtes/Rnormal < Psat_Rn)[0]
    if len(index_Psat_Rn_array)==0:
        index_Psat_Rn=0
    else:
        index_Psat_Rn=index_Psat_Rn_array[0]

    Psat[i]=Ptes[index_Psat_Rn]

    bias_dac_inf=tes.inflection_point()
    print 'bias DAC inflection point=',bias_dac_inf
    alpha=tes.alpha(G_guess,To_guess)
    Lin=tes.Lin
    resp_avg=running_median(resp,num)
    alpha_avg=running_median(alpha,num)
    Lin_avg=running_median(Lin,num)
    Rtes_avg=np.array(running_median(Rtes[1:],num))
    K=G_guess/4/To_guess**3
    Ttes=(Ptes[1:]/K+temp[i]**4)**0.25
    Ttes_avg=np.array(running_median(Ttes[1:],num))
    ax4.plot(Rtes_avg*1e3,alpha_avg,'o')
    ax4.plot(Rtes_avg*1e3,np.ones(len(Rtes_avg))*100,'r')
    ax4.set_xlim([0,1.0e3*Rtes[0]])
    ax4.set_ylim([-10,110])
    ax4.set_ylabel(r"$\frac{\alpha}{1+\beta}$",fontsize=22)
    ax4.set_xlabel('Rtes (mOhms)')
    ax5.plot(Ttes_avg,Rtes_avg*1e3,'o')
    ax5.set_ylim([0,1.0e3*Rtes[0]])
#    ax5.set_xlim([0.1,0.2])
    ax5.set_xlabel("Ttes (K)")
    ax5.set_ylabel('Rtes (mOhms)')
    ax5.set_title(title)
#    ax5.plot(Rtes_avg,resp_avg,'o')
#    ax5.set_xlim([0,1.0*Rtes[0]])
#    ax6.plot(Rtes_avg,Lin_avg,'o')
#    ax6.set_xlim([0,1.0*Rtes[0]])
    if len(target_bias) > 0:
        Ibias_target=tes.detbias_dac_to_Ibias(target_bias)
        k=0
        for target in Ibias_target:
            index_target=np.where(Ibias < target)[0][0]
            index_target_range=np.arange(num)+index_target-num/2
#            print Ibias[index_target],target
            print '\n'
            print 'bias DAC target=',target_bias[k]
            k=k+1
            print 'Rtes target [mOhms]=',np.round(np.mean(Rtes[index_target_range])*1e3,1)
            print '%Rn target=',np.round(np.mean(Rtes[index_target_range])/Rnormal,2)
            print 'Resp target[nW/A]=',np.round(np.mean(resp[index_target_range]*1e9),1)
            print 'Vtes target[nV]=',np.round(np.mean(Vtes[index_target_range])*1e9,1)
            print 'Ites target[uA]=',np.round(np.mean(Ites[index_target_range])*1e6,1)
            print 'alpha/(1+beta) target bias=',np.round(np.mean(alpha[index_target_range]),1)
            print 'Lin/(1+beta) target bias=',np.round(np.mean(Lin[index_target_range]),1)
    print '\n'
    i=i+1
    
if Psat_Rn != 0:
    fig2=plt.figure(2)
    ax3=fig2.add_subplot(111)
    ax3.plot(temp,Psat,'o')
    ax3.set_ylim([0,Ptes[0]])
    n=args.n
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

    print '\n'
    print 'Rn =', np.round(Rnormal*1e3,1)
    print 'K (pW/K^n)=', np.round(param[0]*1e12,1)
    print 'Tc (K)=', np.round(param[1],3)
    print 'G@Tc pW/K=', np.round(G*1e12,1)

    print 'G@150mK pW/K=', np.round(G150*1e12,1)
    print '\n'

if args.fit_transition:
    tr_fit=tes.fit_transition(plot=True)
    print tr_fit[0][tes.inf_tr:tes.inf_sc]
    print tr_fit[1][tes.inf_tr:tes.inf_sc]


if args.plot:
    plt.show()

if args.saveplot != None:
    iv_filename=args.saveplot+'_IVs.pdf'
    pp=PdfPages(iv_filename)
    pp.savefig(fig1)
    pp.close()
    if Psat_Rn != 0:
        iv_filename=args.saveplot+'_TempvsPsat.pdf'
        pp=PdfPages(iv_filename)
        pp.savefig(fig2)
        pp.close()
    iv_filename=args.saveplot+'_alpha.pdf'
    pp=PdfPages(iv_filename)
    pp.savefig(fig3)
    pp.close()

import numpy as np
import matplotlib.pyplot as plt
import argparse
import code.common.filehandler as fh
import scipy.optimize as opt
import tau

parser=argparse.ArgumentParser(description= 'analyses bias step file', formatter_class=argparse.ArgumentDefaultsHelpFormatter,fromfile_prefix_chars='@')

parser.add_argument('--filenames', type=str,nargs='*',help='list of bias_step filenames to analyze')
parser.add_argument('--title', type=str,default=None,help='list of bias_step filenames to analyze')
parser.add_argument('--row', type=int,  help='row to be analyzed and plotted')
parser.add_argument('--col', type=int,  help='row to be analyzed and plotted')
parser.add_argument('--sampfreq', type=float, default=411,  help='sampling freq of bias step file')
parser.add_argument('--G_guess', type=float, default=65e-12,  help='G guess or known for alpha')
args=parser.parse_args()


filenames=args.filenames
G_guess=args.G_guess
row=args.row
col=args.col
samp_freq=args.sampfreq

if args.title != None:
    title=args.title
else:
    title=filenames[0]


def running_median(data,num):
    data_med=[]
    for j in np.arange(len(data)/num):
        data_med.append(np.median(data[j*num:(j+1)*num]))
    return data_med

fig=plt.figure(1)
ax1=fig.add_subplot(111)
#ax2=fig.add_subplot(212)

tau_up=[]
tau_down=[]


for filename in filenames:
    print filename
    data=fh.get_mce_data(filename,row_col=True)
    data_tes=data[row,col,:]
    tes_tau=tau.Tau(data_tes,samp_freq)
    step_pos,step_neg=tes_tau.avg_steps2()
    ax1.plot(step_pos*1e-6)
    ax1.plot(-step_neg*1e-6)
#    ax2.plot(data_tes-np.mean(data_tes))
    ax1.set_xlim([0,100])
    ax1.set_ylim([-0.1,np.max(step_pos)*1.5e-6])
    ax1.set_ylabel('Ites in DACs 1e-6')
    ax1.set_xlabel('Data sample index (sampling rate '+str(np.round(samp_freq,0))+'Hz)')
    ax1.set_title(title)
    fit_offset=10
    tup=tes_tau.tau_fit(step_pos,offset=fit_offset)
    tdown=tes_tau.tau_fit(-step_neg,offset=fit_offset)
    tau_up.append(tup)
    tau_down.append(tdown)
    print 'UP'
    C=tup*G_guess
    print 'tau (mS)='+str(np.round(tup*1e3,1)) 
    print 'C (pJ/K)='+str(np.round(C*1e12,2)) 
    print 'Down'
    C=tdown*G_guess
    print 'tau (mS)='+str(np.round(tdown*1e3,1)) 
    print 'C (pJ/K)='+str(np.round(C*1e12,2)) 

tau_mean=(np.array(tau_down)+np.array(tau_up))/2
print np.round(np.array(tau_down)*1e3,1), np.round(np.array(tau_up)*1e3,1), np.round(tau_mean*1e3,1)
plt.show()

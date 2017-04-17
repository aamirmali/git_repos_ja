import numpy as np
import matplotlib.pyplot as plt
from demod_filter import demod_filter
import code.common.filehandler as fh
import glob


samp_rate=50e6/100./22./38.

df=demod_filter(25,2.0)
col=2
row=14

fig1=plt.figure(1)
ax1=fig1.add_subplot(111)



inter=np.zeros(131072)
inter2=np.zeros(131072)

files=glob.glob('/data/cryo/20151204/det_on_2000_triangle_scan_call_0.5mms_25hz0.011')
#files=glob.glob('/data/cryo/20151203/det_on_2000_overnight_0.5mms_25hz0.???')
#files=glob.glob('/data/cryo/20151204/det_on_2000_triangle_scan_0.5mms_25hz0.???')
for f in files:
    print f
    data=fh.get_mce_data(f, row_col=True)
    tes=data[row,col,:]-np.mean(data[row,col,:])
    tes2=data[14,col,:]-np.mean(data[14,col,:])
    d_filter, d_fft=df.demod(tes,samp_rate)
    d_filter2, d_fft2=df.demod(tes2,samp_rate)
    min_filter=np.min(d_filter)
    max_filter=np.max(d_filter)
    if min_filter < 500 and max_filter > 2000:
        offset=np.where(d_filter==max_filter)[0]
        x_roll=-offset-131072/2
        print offset, x_roll
        rolled=np.roll(d_filter, x_roll)
        rolled2=np.roll(d_filter2, x_roll)
        inter=inter+rolled
        inter2=inter2+rolled2
        ax1.plot(rolled2)



fig3=plt.figure(3)
ax3=fig3.add_subplot(111)
ax3.plot(d_filter)
#ax3.plot(tes)

half_scan=inter2


freq_band=np.fft.fftfreq(len(half_scan),1./samp_rate)
band=np.fft.fft(half_scan)*np.exp(1j*131072/2/samp_rate*2*np.pi*freq_band)

fig2=plt.figure(2)
ax2=fig2.add_subplot(111)
factor=1/5e-4/2*3e8*1e-9

freq_band=freq_band*factor**1
index_range=np.where(np.logical_and(freq_band > 20, freq_band < 600))[0]
amp_max=np.max(np.real(band[index_range]))
ax2.plot(freq_band[index_range],np.real(band)[index_range]/amp_max)
ax2.plot(freq_band[index_range],np.imag(band)[index_range]/amp_max)
ax2.plot(77*np.ones(2),np.array([1e-4,1]),'r')
ax2.plot(108*np.ones(2),np.array([1e-4,1]),'r')

ax2.set_xlabel('Freq (GHz)')
ax2.set_title('c2r14 W2 20151204')
ax2.set_ylim([-0.2,1])


plt.show()

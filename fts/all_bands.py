import numpy as np
import matplotlib.pyplot as plt
from demod_filter import demod_filter
import code.common.filehandler as fh
import glob


samp_rate=50e6/100./22./38.

df=demod_filter(25,2)
col_best=2
row_best=14
npoints=131072
nrows=22
ncols=4

c0=[0,1,10,11,12,15,19,21]
c1=[1,2,5,6,7,14,15,17,18]
c2=[7,8,10,11,12,14]
c3=[1,2,3,7,8,9,10,11,12,13]

row_arrays=[c0,c1,c2,c3]


fig1=plt.figure(1)
ax1=fig1.add_subplot(111)



inter=np.zeros(npoints)
inter2=np.zeros(npoints)
inter_call=np.zeros([nrows,ncols,npoints])

files=glob.glob('/data/cryo/20151204/det_on_2000_triangle_scan_call_0.5mms_25hz0.???')
#files=glob.glob('/data/cryo/20151203/det_on_2000_overnight_0.5mms_25hz0.???')
#files=glob.glob('/data/cryo/20151204/det_on_2000_triangle_scan_0.5mms_25hz0.???')
for f in files:
    print f
    data=fh.get_mce_data(f, row_col=True)
    tes=data[row_best,col_best,:]-np.mean(data[row_best,col_best,:])
    d_filter, d_fft=df.demod(tes,samp_rate)
    min_filter=np.min(d_filter)
    max_filter=np.max(d_filter)
    print min_filter, max_filter
    if min_filter < 500 and max_filter > 2000:
        offset=np.where(d_filter==max_filter)[0]
        x_roll=-offset-npoints/2
        print offset, x_roll
        for c in [0,1,2,3]:
            rows=row_arrays[c]
            for r in rows:
                tes2=data[r,c,:]-np.mean(data[r,c,:])
                d_filter2, d_fft2=df.demod(tes2,samp_rate)
                rolled2=np.roll(d_filter2, x_roll)
                inter_call[r,c,:]+=rolled2



fig3=plt.figure(3)
ax3=fig3.add_subplot(111)
ax3.plot(np.real(inter_call[row_best,col_best,:]))

np.save('/data/cryo/20151204/interferogram_c2_r14',inter_call[row_best,col_best,:])

fig2=plt.figure(2)
ax2=fig2.add_subplot(111)

freq_band=np.fft.fftfreq(npoints,1./samp_rate)
factor=1/5e-4/2*3e8*1e-9
freq_band=freq_band*factor**1
index_range=np.where(np.logical_and(freq_band > 20, freq_band < 600))[0]
band_avg=freq_band[index_range]*0
for c in np.arange(4):
    rows=row_arrays[c]
    for r in rows:
        half_scan=inter_call[r,c,:]
        band=np.fft.fft(half_scan)*np.exp(1j*npoints/2.0/samp_rate*2*np.pi*freq_band/factor)
        amp_max=np.max(np.real(band)[index_range])
        real=np.real(band)[index_range]/amp_max
        imag=np.imag(band)[index_range]/amp_max
        std=np.std(imag)
        if std < 0.10:
            print 'col=', c,' row=', r, ' std=', std
            ax2.plot(freq_band[index_range],real)
            band_avg+=real
#            ax2.plot(freq_band[index_range],imag)

ax2.plot(77*np.ones(2),np.array([1e-4,1]),'r',lw=3)
ax2.plot(108*np.ones(2),np.array([1e-4,1]),'r',lw=3)

ax2.set_xlabel('Freq (GHz)')
ax2.set_title('c2r14 W2 20151204')
ax2.set_ylim([-0.2,1])

ax1.plot(freq_band[index_range],band_avg/np.max(band_avg))
ax1.plot(77*np.ones(2),np.array([1e-4,1]),'r',lw=3)
ax1.plot(108*np.ones(2),np.array([1e-4,1]),'r',lw=3)

ax1.set_xlabel('Freq (GHz)')
ax1.set_title('c2r14 W2 20151204')
ax1.set_ylim([-0.2,1])

plt.show()

import numpy as np
import matplotlib.pyplot as plt
from demod_filter import demod_filter
import code.common.filehandler as fh
import glob
from scipy import signal
import mce_data


samp_rate=50e6/100./22./38.

df=demod_filter(25,4)
col_best=2
row_best=14
num_points=131072
nrows=22
ncols=4



c0=[0,1,10,11,12,15,19,21]
c1=[1,2,5,6,7,14,15,17,18]
c2=[7,8,10,11,12,14]
c3=[1,2,3,7,8,9,10,11,12,13]

row_arrays=[c0,c1,c2,c3]

if 1 ==0:
    data=mce_data.SmallMCEFile('/data/cryo/20151204/det_on_2000_triangle_scan_call_0.5mms_25hz0.0')
    ctime_init=data.header['runfile_id']

    demod_all=np.array([])
    for i in np.arange(273):
        int_str=str(i/1000.)
        f='/data/cryo/20151204/det_on_2000_triangle_scan_call_0.5mms_25hz'+int_str
        print f
        data=mce_data.SmallMCEFile(f)
        ctime_det=data.header['runfile_id']
        data=fh.get_mce_data(f, row_col=True)
        ctime_diff=ctime_det-ctime_init
        tes=data[row_best,col_best,:]-np.mean(data[row_best,col_best,:])
        d_filter, d_fft=df.demod(tes,samp_rate)
        demod_all=np.concatenate((demod_all,d_filter[0]*np.ones(ctime_diff*samp_rate)))
        demod_all=np.concatenate((demod_all,d_filter))
        ctime_init=ctime_init+np.floor(num_points/samp_rate)+ctime_diff
    np.save('/data/cryo/20151204/all_demod_data_c2_r14',demod_all)




fig1=plt.figure(1)
ax1=fig1.add_subplot(111)

fig2=plt.figure(2)
ax2=fig2.add_subplot(111)

c2r14_inter=np.load('/data/cryo/20151204/interferogram_c2_r14.npy')
c2r14_demod_all=np.load('/data/cryo/20151204/all_demod_data_c2_r14.npy')
c2r14_index_scan=np.load('/data/cryo/20151204/scan_turn_around_index.npy')

#inter=np.zeros(npoints)
#inter2=np.zeros(npoints)
#inter_call=np.zeros([nrows,ncols,npoints])

#files=glob.glob('/data/cryo/20151204/det_on_2000_triangle_scan_call_0.5mms_25hz0.???')
#files=glob.glob('/data/cryo/20151203/det_on_2000_overnight_0.5mms_25hz0.???')
#files=glob.glob('/data/cryo/20151204/det_on_2000_triangle_scan_0.5mms_25hz0.???')


scan_points=170000
offset=00000
x_even=np.zeros(scan_points*2)
x_odd=np.zeros(scan_points*2)



def get_scan_aligned(scan):
    nscan=len(scan)
    full_scan=np.zeros(nscan*2)
    pfit_scan=np.polyfit(np.arange(nscan),scan,3)
    func_scan=np.poly1d(pfit_scan)
    scan_1=(scan-func_scan(np.arange(nscan)))#/func_scan(np.arange(nscan))#div or subtract
    scan_conv=signal.fftconvolve(scan_1,c2r14_inter)
    index_wl=np.where(scan_conv == np.max(scan_conv))[0]
    print index_wl-len(c2r14_inter)/2
    index_wl_final=index_wl-len(c2r14_inter)/2
#    roll_num=scan_points/2-(index_wl-len(c2r14_inter)/2)
#    scan_aligned=np.roll(scan_1,roll_num)
    low_index=nscan-index_wl_final
    high_index=nscan-index_wl_final+nscan
    print low_index
    print high_index
    print len(full_scan[low_index:high_index])
    print len(scan_1)
    full_scan[low_index:high_index]=scan_1
    scan_aligned=full_scan
    return scan_aligned




for i in c2r14_index_scan[0::2]:
    scan=c2r14_demod_all[i+offset:i+offset+scan_points]
    scan_aligned=get_scan_aligned(scan)
    x_even=x_even+scan_aligned
    print 'even', i

for i in c2r14_index_scan[1::2]:
    scan=c2r14_demod_all[i+offset:i+offset+scan_points]
    scan_aligned=get_scan_aligned(scan)
    x_odd=x_odd+scan_aligned
    print 'odd', i


freq_band=np.fft.fftfreq(scan_points*2,1./samp_rate)
factor=1/5e-4/2*3e8*1e-9
freq_band=freq_band*factor**1
index_range=np.where(np.logical_and(freq_band > 5, freq_band < 1200))[0]
band_avg=freq_band[index_range]*0

half_scan=x_even+x_odd[::-1]

band=np.fft.fft(half_scan)*np.exp(1j*scan_points*2/2.0/samp_rate*2*np.pi*freq_band/factor)
amp_max=np.max(np.real(band)[index_range])
real=np.real(band)[index_range]/amp_max
imag=np.imag(band)[index_range]/amp_max


ax2.plot(freq_band[index_range],real)
ax2.plot(freq_band[index_range],imag)

#ax2.plot(77*np.ones(2),np.array([1e-4,1]),'r',lw=3)
#ax2.plot(108*np.ones(2),np.array([1e-4,1]),'r',lw=3)

ax2.set_xlabel('Freq (GHz)')
ax2.set_title('c2r14 W2 20151204')
ax2.set_ylim([-0.2,1])

ax1.plot(half_scan)
#ax1.plot(77*np.ones(2),np.array([1e-4,1]),'r',lw=3)
#ax1.plot(108*np.ones(2),np.array([1e-4,1]),'r',lw=3)

#ax1.set_xlabel('Freq (GHz)')
#ax1.set_title('c2r14 W2 20151204')
#ax1.set_ylim([-0.2,1])

dic_c2r14_fts = {'freq': freq_band[index_range], 'band_real': real, 'band_imag' : imag, 'interferogram': half_scan}

np.save('/data/cryo/20151204/dic_c2r14_fts_full_v2', dic_c2r14_fts)

plt.show()

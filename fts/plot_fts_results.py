import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

samp_rate=50e6/100./22./38.
speed=0.5 # mm/s

filename='/data/cryo/20151204/dic_c2r14_fts_full_v2.npy'

dic=np.load(filename).item()

interferogram=dic['interferogram']
band_real=dic['band_real']
band_imag=dic['band_imag']
freq=dic['freq']

n_inter=len(interferogram)
position_inter=(np.arange(n_inter)-n_inter/2)/samp_rate*speed

num_avg=1
band_avg=np.convolve(band_real, np.ones(num_avg))/num_avg
imag_avg=np.convolve(band_imag, np.ones(num_avg))/num_avg
freq_avg=np.convolve(freq, np.ones(num_avg))/num_avg

index_avg=np.where(np.logical_and(freq_avg[:-num_avg] > 350, freq_avg [:-num_avg]< 700))[0]
print 'Power mean 350-700GHz normalized to max inband=', np.mean(band_avg[:-num_avg][index_avg])/np.max(band_avg[:-1])
print 'Power std 350-700GHz normalized to max inband=', np.std(band_avg[:-num_avg][index_avg])/np.max(band_avg[:-1])
print 'Power error from std imag 350-700GHz normalized=', np.std(imag_avg[:-num_avg][index_avg])/np.max(band_avg[:-1])
print 'max inband', np.max(band_avg[:-1])
print 'num points average', len(index_avg)


index_sum=np.where(np.logical_and(freq_avg[:-num_avg] > 300, freq_avg [:-num_avg]< 600))[0]
index_sum_band=np.where(np.logical_and(freq_avg[:-num_avg] > 77, freq_avg [:-num_avg]< 108))[0]
print 'Power sum 300-600GHz normalized to max inband=', np.sum(band_avg[:-num_avg][index_sum])/np.max(band_avg[:-1])
print 'Power sum 77-108GHz normalized to max inband=', np.sum(band_avg[:-num_avg][index_sum_band])/np.max(band_avg[:-1])


fig1= plt.figure(1,figsize=(18,10))
ax1=fig1.add_subplot(311)
ax2=fig1.add_subplot(312)
ax3=fig1.add_subplot(313)


ax1.plot(position_inter,interferogram/1e5)
ax1.set_title(filename.split('/')[-1])
ax1.set_xlabel('Distance (mm)')
ax1.set_ylabel('Amplitude (a.u)')

ax2.plot(freq,band_real,label='band real')
ax2.plot(freq,band_imag, label='band imag')
ax2.set_xlabel('Frequency (GHz)')
ax2.set_ylabel('Amplitude (max = 1)')
ax3.set_ylim([0,1])
ax3.set_xlim([5,1200])

ax3.plot(freq_avg[:-num_avg],band_avg[:-num_avg]/np.max(band_avg[:-1]),label='band average')
ax3.plot(freq_avg[:-num_avg],imag_avg[:-num_avg]/np.max(band_avg[:-1]),label='imag average')
ax3.plot(freq_avg[:-num_avg],np.zeros(len(freq_avg[:-num_avg])),'--r')
ax3.set_xlabel('Frequency (GHz)')
ax3.set_ylabel('Amplitude (max = 1)')
ax3.set_ylim([-0.025,0.025])
ax3.set_xlim([5,1200])

plt.show()

pdf_file=filename.split('.')[0]+'.pdf'

pp=PdfPages(pdf_file)
pp.savefig(fig1)
pp.close()

import numpy as np
import matplotlib.pyplot as plt


x_all=np.load('/data/cryo/20151204/all_demod_data_c2_r14.npy')
ctime=np.load('/data/cryo/20151204/ctime_fts.npy')
pos=np.load('/data/cryo/20151204/position_fts.npy')

npoints=len(x_all)
samp_rate=50e6/100./22./38.
time_det=np.arange(npoints)/samp_rate

nsec=15
conv=np.zeros(nsec)
for i in np.arange(nsec):
    offset_time=i*1+30
    pos_det_time=np.interp(time_det,ctime-ctime[0]-offset_time,pos)
    conv[i]=np.sum(pos_det_time*x_all)
    print i

conv_max=np.max(conv[i])
print conv_max, np.where(conv == conv_max)

plt.plot(conv)

plt.show()

#offset_time c2_r14 20151204 30+7=37

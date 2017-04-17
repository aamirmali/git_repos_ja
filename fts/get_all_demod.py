import numpy as np
import matplotlib.pyplot as plt
from demod_filter import demod_filter
import code.common.filehandler as fh
import mce_data

samp_rate=50e6/100./22./38.

df=demod_filter(25,2)
col_best=2
row_best=14

data=mce_data.SmallMCEFile('/data/cryo/20151204/det_on_2000_triangle_scan_call_0.5mms_25hz0.0')
ctime_init=data.header['runfile_id']
num_points=131072

demod_all=np.array([])
for i in np.arange(273):
    int_str=str(i/1000.)
#   if i ==0 or i == 100 or i == 200:
#        int_str=str(i/100)
    f='/data/cryo/20151204/det_on_2000_triangle_scan_call_0.5mms_25hz'+int_str
    print f
    data=mce_data.SmallMCEFile(f)
    ctime_det=data.header['runfile_id']
    print ctime_det
    data=fh.get_mce_data(f, row_col=True)
    ctime_diff=ctime_det-ctime_init
    print ctime_diff
    tes=data[row_best,col_best,:]-np.mean(data[row_best,col_best,:])
    d_filter, d_fft=df.demod(tes,samp_rate)
    demod_all=np.concatenate((demod_all,d_filter[0]*np.ones(ctime_diff*samp_rate)))
    demod_all=np.concatenate((demod_all,d_filter))
    ctime_init=ctime_init+np.floor(num_points/samp_rate)+ctime_diff


np.save('/data/cryo/20151204/all_demod_data_c2_r14',demod_all)


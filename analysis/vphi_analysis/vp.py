import numpy as np
import matplotlib.pyplot as plt
import vphi
import code.common.filehandler as fh



filename='/data/cryo/current_data/1376435423/1376435468_RCs_sq1rampc'
filename='/data/cryo/current_data/1376435423/1376435478_RCs_sq1ramptes'
filename='/data/cryo/current_data/1377113706/1377113872_RCs_sq1rampc'
#filename='/data/cryo/current_data/1377113706/1377113981_RCs_sq1ramptes'

data=fh.get_mce_data(filename, row_col=True)
row=6
col=1

for row in np.arange(15):
    sq=vphi.Vphi(data[row,col,:],smooth_num=100)
    plt.plot(sq.smooth_vphi(),'o')
    plt.plot(np.diff(sq.smooth_vphi()),'o')
    period,neg_per,pos_per=sq.find_period()
    print 'row=',row,'period=',period


plt.show()

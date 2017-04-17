import numpy as np
import sqlite3
from clean_timestream import Clean
from ABS_param import ABS_param
import iv
import glob
import filehandler as fh
import os
import sys


ABS=ABS_param()




db=sqlite3.connect('iv_db')

cursor=db.cursor()


#cursor.execute('''ALTER TABLE ivs ADD COLUMN target_bias REAL''') # add target bias
#db.commit()

datedirs=glob.glob('/net/abs-data1/data*/cryo/*')

print len(datedirs)
print datedirs[0]

for datedir in datedirs:
    print datedir
    iv_files=glob.glob(datedir+'/iv_1?????????')
    for iv_file in iv_files:
        ctime=int(iv_file.split('v_')[1])
        print iv_file
        try:
            rec_biases=fh.IV_data_to_arr(iv_file+'.out','rec_biases')
            bias_volts=rec_biases[:,0]*ABS.db_DAC_volts/2**ABS.db_bits/ABS.Rdetb
            for col in np.arange(ABS.num_cols):
                col=int(col)
                target_bias=bias_volts[ABS.bias_lines[col]]
                print target_bias, col, ctime
                cursor.execute('''UPDATE ivs SET target_bias=? WHERE ivs.col=? AND ivs.ctime =? ''',(target_bias, col,ctime))
        except:
             print sys.exc_info() 
#            pass
    db.commit()


db.close()

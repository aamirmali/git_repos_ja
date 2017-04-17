import numpy as np
import sqlite3
from clean_timestream import Clean
from ABS_param import ABS_param
import iv
import glob
import filehandler as fh
import os
import sys
import multiprocessing

missing=np.genfromtxt('/home/jappel/iv_database/missing_ivs_set2.txt')


def db_datedir(datedir_list, ABS, cursor):
    for datedir in datedir_list:
        print datedir
        iv_files=glob.glob(datedir+'/iv_1?????????')
        det_ivs=[]
        for iv_file in iv_files:
            ctime=iv_file.split('v_')[1]
            ind_miss=np.where(missing==int(ctime))[0]
            print ind_miss
            if len(ind_miss) > 0:
                print iv_file
#           try:
                db_bias=np.genfromtxt(iv_file+'.bias',skiprows=1)
                rec_biases=fh.IV_data_to_arr(iv_file+'.out','rec_biases')
                bias_volts=rec_biases[:,0]*ABS.db_DAC_volts/2**ABS.db_bits/ABS.Rdetb
                data=fh.get_mce_data(iv_file,row_col=True)
                print "first col loop start"
                for col in np.arange(ABS.num_cols):
                    Rsh=ABS.Rshunt_cols[col]
                    target_bias=bias_volts[ABS.bias_lines[col]]
                    for row in np.arange(ABS.num_rows):            
#                        print 'col:', col,' row: ', row
                        data_tes=data[row,col,:]
                        if np.median(np.diff(data_tes[0:ABS.index_normal])) > 0:
                            data_tes=data_tes*-1
                        clean=Clean()
                        data_tes=clean.data_fix_jumps(data_tes)
                        tes=iv.IV(data=data_tes,db_bias=db_bias,Rsh=Rsh,filtgain=ABS.filtgain,Rfb=ABS.Rfb,Rdetb=ABS.Rdetb, index_normal=ABS.index_normal, dac_bits=ABS.dac_bits, M_ratio=ABS.M_ratio, db_bits=ABS.db_bits, fb_DAC_volts=ABS.fb_DAC_volts, db_DAC_volts=ABS.db_DAC_volts)
                        Rn=np.median(tes.Rtes[0:ABS.index_normal])
                        Psat=tes.calc_Psat_inter(Rn,PRn_min=0.75,PRn_max=0.85)
                        fit=tes.fit_params()
                        det=(int(ctime),int(col),int(row),Rsh,Rn,Psat,target_bias,fit[0],fit[1],fit[2],fit[3],fit[4],fit[5],fit[6])
                        det_ivs.append(det)
#           except:
#               print sys.exc_info()
#               break
        cursor.executemany('''INSERT INTO ivs(ctime,col,row,rsh,rn,psat,target_bias,fit0,fit1,fit2,fit3,fit4,fit5,fit6) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',det_ivs)
        db.commit()

if __name__ == '__main__':
    ABS=ABS_param()
    db=sqlite3.connect('/home/jappel/iv_database/iv_db_missing',timeout=30.0)
    cursor=db.cursor()
#    cursor.execute('''DROP TABLE ivs''') 
    cursor.execute('''CREATE TABLE ivs(ctime INT, col INT, row INT, rsh REAL, rn REAL, psat REAL, target_bias REAL, fit0 REAL, fit1 REAL, fit2 REAL, fit3 REAL, fit4 REAL, fit5 REAL, fit6 REAL) ''')
    db.commit()
    datedirs1=glob.glob('/net/abs-data1/data/cryo/*')
    datedirs2=glob.glob('/net/abs-data1/data2/cryo/*')
    print len(datedirs1)
    print len(datedirs2)
    jobs = []

    p1 = multiprocessing.Process(target=db_datedir,args=(datedirs1,ABS,cursor))
    p2 = multiprocessing.Process(target=db_datedir,args=(datedirs2,ABS,cursor))


#    p1 = multiprocessing.Process(target=db_datedir,args=(datedirs1[0:85],ABS,cursor))
#    p2 = multiprocessing.Process(target=db_datedir,args=(datedirs1[85:170],ABS,cursor))
#    p3 = multiprocessing.Process(target=db_datedir,args=(datedirs1[170:255],ABS,cursor))

#    p4 = multiprocessing.Process(target=db_datedir,args=(datedirs1[255:340],ABS,cursor))
#    p5 = multiprocessing.Process(target=db_datedir,args=(datedirs1[340:420],ABS,cursor))
#    p6 = multiprocessing.Process(target=db_datedir,args=(datedirs1[420:],ABS,cursor))
#    p7 = multiprocessing.Process(target=db_datedir,args=(datedirs2[0:85],ABS,cursor))
#    p8 = multiprocessing.Process(target=db_datedir,args=(datedirs2[85:],ABS,cursor))
    jobs.append(p1)
    jobs.append(p2)
#    jobs.append(p3)
#    jobs.append(p4)
#    jobs.append(p5)
#    jobs.append(p6)
#    jobs.append(p7)
#    jobs.append(p8)
    p1.start()
    p2.start()
#    p3.start()
#    p4.start()
#    p5.start()
#    p6.start()
#    p7.start()
#    p8.start()
    db.close()

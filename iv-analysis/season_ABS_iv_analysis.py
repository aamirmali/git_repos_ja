import glob
import os
import multiprocessing

def iv_analysis(datedirs):
    for datedir in datedirs:
        print datedir
        ivfiles=glob.glob(datedir+'/iv_1?????????')
        for ivfile in ivfiles:
            os.system('python ABS_iv_analysis.py '+ivfile+' -savedir /home/jappel/time_constant_IV/season_IVs_out2/')

if __name__ == '__main__':
    datedirs1=glob.glob('/net/abs-data1/data/cryo/*')
    datedirs2=glob.glob('/net/abs-data1/data2/cryo/*')
    print len(datedirs1)
    print len(datedirs2)
    jobs = []
    p1 = multiprocessing.Process(target=iv_analysis,args=(datedirs1[0:250],))
    p2 = multiprocessing.Process(target=iv_analysis,args=(datedirs1[250:255],))
    p3 = multiprocessing.Process(target=iv_analysis,args=(datedirs2[0:5],))
    jobs.append(p1)
    jobs.append(p2)
    jobs.append(p3)
    p1.start()
    p2.start()
    p3.start()

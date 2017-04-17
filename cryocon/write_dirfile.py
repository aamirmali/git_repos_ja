import os
import array
import time
import numpy as np

class Dirfile:
    """this class initializes and writes a dirfile for time and resistence of GRT from cryocon"""

    def __init__(self, res_val,curr_k1,curr_k2,pid_error,parent_directory='/data/cryocon/',dfname=None,frame_len=10):
        self.par_dir=parent_directory
        self.frame_len=frame_len
        if dfname==None:
           self.dfname=str(int(time.time()))
        else:
            self.dfname=dfname
        self.dirname=os.path.join(self.par_dir,self.dfname)
        if os.path.isdir(self.dirname):
            raise Exception('Cannot create dirfile %s. Directory already exists.\n' % self.dirname)
        os.mkdir(self.dirname)
        if os.path.isdir('/data/cryocon/curr_cryocon'):
            os.remove('/data/cryocon/curr_cryocon')
        os.symlink(self.dirname,'/data/cryocon/curr_cryocon')
        fmt_file=file(os.path.join(self.dirname,'format'),'w')
        fmt_file.write('time RAW FLOAT64 '+str(self.frame_len)+'\n')
        fmt_file.write('res_cryocon RAW FLOAT64 '+str(self.frame_len)+'\n')
        fmt_file.write('curr_keith1 RAW FLOAT64 '+str(self.frame_len)+'\n')
        fmt_file.write('curr_keith2 RAW FLOAT64 '+str(self.frame_len)+'\n')
        fmt_file.write('pid_error RAW FLOAT64 '+str(self.frame_len)+'\n')
        fmt_file.write('GRT_TEMP LINTERP res_cryocon /home/mce/cryocon/calib_tables/GRT_testdewar.txt \n')
        fmt_file.write('/REFERENCE time\n')
        fmt_file.close()
        self.time_array=array.array('d',[0.0]*self.frame_len)
        self.res_array_cryocon=array.array('d',[0.0]*self.frame_len)
        self.curr_array_keith1=array.array('d',[0.0]*self.frame_len)
        self.curr_array_keith2=array.array('d',[0.0]*self.frame_len)
        self.pid_error_array=array.array('d',[0.0]*self.frame_len)
        self.res_val=res_val
        self.curr_k1=curr_k1
        self.curr_k2=curr_k2
        self.pid_error=pid_error
    def start_daq(self,):
        file_time=file(os.path.join(self.dirname,'time'),'w')
        file_res_cryocon=file(os.path.join(self.dirname,'res_cryocon'),'w')
        file_curr_keith1=file(os.path.join(self.dirname,'curr_keith1'),'w')
        file_curr_keith2=file(os.path.join(self.dirname,'curr_keith2'),'w')
        file_pid_error=file(os.path.join(self.dirname,'pid_error'),'w')
        i=0
        while True:
#            if i==0:
#                start=time.time()
            time.sleep(0.09)
            self.time_array[i]=time.time()
            self.res_array_cryocon[i]=self.res_val[0]
            self.curr_array_keith1[i]=self.curr_k1[0]
            self.curr_array_keith2[i]=self.curr_k2[0]
            self.pid_error_array[i]=self.pid_error[0]
            i += 1
            if i == self.frame_len:
                i = 0
                self.time_array.tofile(file_time)
                self.res_array_cryocon.tofile(file_res_cryocon)
                self.curr_array_keith1.tofile(file_curr_keith1)
                self.curr_array_keith2.tofile(file_curr_keith2)
                self.pid_error_array.tofile(file_pid_error)
                file_time.flush()
                file_res_cryocon.flush()
                file_curr_keith1.flush()
                file_curr_keith2.flush()
                file_pid_error.flush()
#                stop=time.time()
#                print 'time_frame=',stop-start

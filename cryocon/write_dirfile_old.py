import os
import array
import cryocon
import keithley
import time
import numpy as np

class Dirfile:
    """this class initializes and writes a dirfile for time and temp from cryocon"""

    def __init__(self, parent_directory='/data/cryocon/',dfname=None,frame_len=10):
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
        fmt_file=file(os.path.join(self.dirname,'format'),'w')
        fmt_file.write('time RAW FLOAT64 '+str(self.frame_len)+'\n')
        fmt_file.write('temp_cryocon RAW FLOAT64 '+str(self.frame_len)+'\n')
        fmt_file.write('time_keith1 RAW FLOAT64 '+str(self.frame_len)+'\n')
        fmt_file.write('time_keith2 RAW FLOAT64 '+str(self.frame_len)+'\n')
        fmt_file.write('/REFERENCE time\n')
        fmt_file.close()
        self.time_array=array.array('d',[0.0]*self.frame_len)
        self.temp_array_cryocon=array.array('d',[0.0]*self.frame_len)
        self.time_array_keith1=array.array('d',[0.0]*self.frame_len)
        self.time_array_keith2=array.array('d',[0.0]*self.frame_len)
        self.cc=cryocon.Cryocon()
        self.keith1=keithley.Keithley('Keithley1')
        self.keith2=keithley.Keithley('Keithley2')
        self.pid=np.zeros(1)
    def start_daq(self):
        file_time=file(os.path.join(self.dirname,'time'),'w')
        file_temp_cryocon=file(os.path.join(self.dirname,'temp_cryocon'),'w')
        file_time_keith1=file(os.path.join(self.dirname,'time_keith1'),'w')
        file_time_keith2=file(os.path.join(self.dirname,'time_keith2'),'w')
        self.cc.connect()
        self.keith1.reset_time()
        self.keith2.reset_time()
        i=0
        while True:
            self.time_array[i]=time.time()
            try:
                temp_cc=float(self.cc.temp().split('\r')[0])
            except ValueError:
                temp_cc=self.temp_array_cryocon[0]
            else:
                self.temp_array_cryocon[i]=temp_cc
            self.time_array_keith1[i]=float(self.keith1.time().split('\n')[0])
            self.time_array_keith2[i]=float(self.keith2.time().split('\n')[0])
            self.pid[0]=self.temp_array_cryocon[i]
            i += 1
            if i == self.frame_len:
                i = 0
                self.time_array.tofile(file_time)
                self.temp_array_cryocon.tofile(file_temp_cryocon)
                self.time_array_keith1.tofile(file_time_keith1)
                self.time_array_keith2.tofile(file_time_keith2)
                file_time.flush()
                file_temp_cryocon.flush()
                file_time_keith1.flush()
                file_time_keith2.flush()

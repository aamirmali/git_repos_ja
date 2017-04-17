#!/usr/bin/python
import time
from daemon import runner
import write_dirfile
import pid_cryocon_keithley
import cryocon
import keithley
import threading
import param_file
import numpy as np


class start_daq(threading.Thread):
    def __init__(self,res_val,curr_keith1,curr_keith2,pid_value):
        threading.Thread.__init__(self)
        self.df=write_dirfile.Dirfile(res_val,curr_keith1,curr_keith2,pid_value)
    def run(self):
        self.df.start_daq()
        return 0
class start_cryocon(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.cc=cryocon.Cryocon()
    def run(self):
        self.cc.connect()
        self.cc.daq_cc()
        return 0
class start_keith(threading.Thread):
    def __init__(self,keithley_name,res_val=None,sp=0,P=20,I=10,D=0.1,factor=2e-7,num=10):
        threading.Thread.__init__(self)
        self.keith=keithley.Keithley(keithley_name)
        self.sp=sp
        self.P=P
        self.I=I
        self.D=D
        self.res_val=res_val
        self.factor=factor
        self.num=num

    def run(self):
        if self.res_val == None:
            self.keith.daq_keith()
        else:
            self.keith.daq_pid_keith(self.res_val,setpoint=self.sp,P=self.P,I=self.I,D=self.D,factor=self.factor,num=self.num)
        return 0
class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/tmp/tempservo_to_dirfile_v2.pid'
        self.pidfile_timeout = 5
        self.file_tempservo = '/data/cryocon/servo_param.p'
    def run(self):
        param=param_file.get_params(self.file_tempservo)
        T1=start_cryocon()
        T2=start_keith('Keithley1',res_val=T1.cc.res_val,sp=param.sp_res,P=param.P,I=param.I,D=param.D,factor=param.factor,num=param.num)
        T3=start_daq(T1.cc.res_val,T2.keith.curr,np.zeros(1),T2.keith.pid_value)
        T1.daemon=True
        T2.daemon=True
        T3.daemon=True
        try:
            T1.start()
            T2.start()
            T3.start()
        except:
            print "Error: unable to start thread"
        while 1:
            time.sleep(0.001)
            pass

app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()

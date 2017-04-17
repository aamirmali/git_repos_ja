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
    def __init__(self,res_val,curr_keith1,curr_keth2,pid_value):
        threading.Thread.__init__(self)
        self.df=write_dirfile.Dirfile(res_val,curr_keith1,curr_keth2,pid_value)
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
class ramp_keith(threading.Thread):
    def __init__(self,keithley_name,ramp_target,curr_range=4.5,max_step=0.00025,time_step=0.1):
        threading.Thread.__init__(self)
        self.keith=keithley.Keithley(keithley_name,curr_range=curr_range)
        self.ramp_target=ramp_target
        self.max_step=max_step
        self.time_step=time_step
    def run(self):
        self.keith.set_curr_amps(self.ramp_target,max_step=self.max_step,time_step=self.time_step)
        return 0
class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/tmp/tempservo_to_dirfile_v2.pid'
        self.pidfile_timeout = 5
        self.file_tempservo = '/data/cryo/cryocon/servo_param.p'
    def run(self):
        T1=start_cryocon()
        T2=ramp_keith('Keithley1',0)
        T4=ramp_keith('Keithley2',0)
        T3=start_daq(T1.cc.res_val,T2.keith.curr,T4.keith.curr,T2.keith.pid_value)
        T1.daemon=True
        T2.daemon=True
        T3.daemon=True
        T4.daemon=True
        try:
            T1.start()
            T2.start()
            T3.start()
            T4.start()
        except:
            print "Error: unable to start thread"
        while 1:
            time.sleep(0.001)
            pass

app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()

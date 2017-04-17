#!/usr/bin/python
import time
from daemon import runner
import write_dirfile
import pid_cryocon_keithley
import cryocon
import keithley
import threading

#sp_res=7022.44#100mK
#sp_res=4968.37#110mK.
#sp_res=3752.29#120mK.
#sp_res=4251.76#115mK.
#sp_res=4351.657#114mK.
sp_res=1845.6162#150mK.
curr_range=1
P=10.
I=1
D=1.0
factor=0.5e-7
num=600

class printtest(threading.Thread):
    def __init__(self,temp):
        threading.Thread.__init__(self)
        self.temp=temp
    def run(self):
        while True:
            t=time.time(),'\n'
            print self.temp
            time.sleep(10)
        return 0 
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
    def __init__(self,keithley_name,res_val=None,sp=sp_res,P=P,I=I,D=D,factor=factor,num=num):
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
    def run(self):
        T1=start_cryocon()
        T2=start_keith('Keithley1',res_val=T1.cc.res_val)
#        T2=start_keith('Keithley1')
#        T3=start_keith('Keithley2')
        T4=start_daq(T1.cc.res_val,T2.keith.curr,T2.keith.curr,T2.keith.pid_value)
        T1.daemon=True
        T2.daemon=True
#        T3.daemon=True
        T4.daemon=True
        try:
            T1.start()
            T2.start()
#            T3.start()
            T4.start()
        except:
            print "Error: unable to start thread"
        while 1:
            time.sleep(0.001)
            pass

app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()

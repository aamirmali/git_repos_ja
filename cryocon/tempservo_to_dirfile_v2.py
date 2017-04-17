#!/usr/bin/python
import time
from daemon import runner
import write_dirfile
import pid_cryocon_keithley
import threading

sp_res=7022.44#100mK

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
    def __init__(self):
        threading.Thread.__init__(self)
        self.df=write_dirfile.Dirfile()
    def run(self):
        self.df.start_daq()
        return 0
class start_pid(threading.Thread):
    def __init__(self,res_val,sp=sp_res,p=20,i=1,d=0.1):
        threading.Thread.__init__(self)
        self.PID=pid_cryocon_keithley.PID(res_val,setpoint=sp,P=p,I=i,D=d)
    def run(self):
        self.PID.start_PID()
        return 0
class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/tmp/tempservo_to_dirfile_v2.pid'
        self.pidfile_timeout = 5
    def run(self):
        T1=start_daq()
        T3=start_pid(T1.df.pid)
#        T2=printtest(T1.df.temp_array_cryocon)
        T1.daemon=True
        T3.daemon=True
#        T2.daemon=True
        try:
            T1.start()
#            T2.start()
            T3.start()
        except:
            print "Error: unable to start thread"
        while 1:
            time.sleep(0.01)
            pass

app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()

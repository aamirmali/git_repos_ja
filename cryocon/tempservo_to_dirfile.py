#!/usr/bin/python
import time
from daemon import runner
import write_dirfile_only_cryocon
import thread

def printtest(temps):
    while True:
        t=time.time(),'\n'
        print temps
        time.sleep(4)
    return 0 


class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/tmp/tempservo_to_dirfile.pid'
        self.pidfile_timeout = 5
    def run(self):
        df=write_dirfile_only_cryocon.Dirfile()
#        df.start_daq()
        try:
            thread.start_new_thread(printtest,(df.temp_array_cryocon,))
            thread.start_new_thread(df.start_daq,())
        except:
            print "Error: unable to start thread"
        while 1:
            time.sleep(0.01)
            pass
app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()

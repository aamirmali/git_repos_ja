#!/usr/bin/python
import time
from daemon import runner
import cryocon

class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/tmp/cryocon_to_file.pid'
        self.pidfile_timeout = 5
    def run(self):
        cc=cryocon.Cryocon()
        cc.connect()
        f=open("/data/cryocon/temperature.txt","w")
        start=time.time()
        while True:
            data=cc.temp()
            f.write(data.split('\r')[0]+' ')
            f.write(str(time.time()-start)+'\n')
        f.close()
        cc.close()

app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()

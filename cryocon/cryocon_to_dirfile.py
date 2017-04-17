#!/usr/bin/python
import time
from daemon import runner
import write_dirfile


class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/tmp/cryocon_to_dirfile.pid'
        self.pidfile_timeout = 5
    def run(self):
        df=write_dirfile.Dirfile()
        df.start_daq()
app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()

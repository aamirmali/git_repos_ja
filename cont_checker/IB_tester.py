import Gpib
import time


class IB_tester:
    '''class to control MCE IB tster card '''
    def __init__(self,gpib_config_name='IB_tester', sl=0.0):
        self.inst=Gpib.Gpib(gpib_config_name)
        self.sl=sl

    def identify(self, idn='V'):
        self.inst.write(idn)
        time.sleep(self.sl)
        card=self.inst.read()
        time.sleep(self.sl)
        return card
    def reset(self, res='R'):
        self.inst.write(res)
        time.sleep(self.sl)
        return 'IB tester reset'
    def slot(self, s='S'):
        self.inst.write(s)
        time.sleep(self.sl)
        slot=self.inst.read()
        time.sleep(self.sl)
        return slot
    def neg_pin(self, pin,neg=''):
        command=neg+pin
        self.inst.write(command)
        time.sleep(self.sl)
        return command
    def pos_pin(self, pin,pos=''):
        command=pos+pin
        self.inst.write(command)
        time.sleep(self.sl)
        return command

import Gpib
import time

class HP_multimeter:
    '''class to control HP multimeter '''
    def __init__(self,gpib_config_name='HP_multimeter',sl=0.0):
        self.inst=Gpib.Gpib(gpib_config_name)
        self.sl=sl

    def identify(self, idn='*IDN?'):
        self.inst.write(idn)
        time.sleep(self.sl)
        card=self.inst.read()
        time.sleep(self.sl)
        return card

    def resistance(self, command='MEAS:RES?', value=1000000, resolution=1):
        com=command+' '+str(value)+','+str(resolution)
        self.inst.write(com)
        time.sleep(self.sl)
        R=self.inst.read()
        time.sleep(self.sl)
        return R

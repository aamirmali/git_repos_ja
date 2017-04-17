import numpy as np
import Gpib
import time
import pid_cryocon_keithley

class Keithley:
    """class that intitializes and controls a keithley current/voltage supply """
    name=None
    """name of keithley in gpib_conf"""
    def __init__(self,name):
        self.name=name
        self.inst=Gpib.Gpib(name)
        self.curr=np.zeros(1)
        self.pid_value=np.zeros(1)
        self.curr_range=0
        self.update_curr_range()
    def write(self,message):
        self.inst.write(message)
        return 0
    def read(self):
        data=self.inst.read()
        return data
    def idn(self, comm='*IDN?\n'):
        self.write(comm)
        data=self.read()
        return data
    def time(self, comm=':syst:time?'):
        self.write(comm)
        data=self.read()
        return data
    def reset_time(self, comm=':syst:time:res'):
        self.write(comm)
        return 0
    def output_status(self):
        self.write(":OUTP?")
        output=int(self.read().split('\n')[0])
        return output
    def output_on(self):
        '''expect voltage and current to be zero before turning on'''
        output=self.output_status()
        if output==0: #off
            self.write(":SOUR:VOLT:LEV 0")
            self.write(":SOUR:CURR:LEV 0")
            self.write(":OUTP ON")
            print "OUTPUT turned on"
        if output==1: #on
            print "OUTPUT already on"
        return 0 
    def output_off(self):
        '''expect current and voltage to have been ramped to zerobefore turning off'''
        output=self.output_status()
        if output==0: #off
            print "OUTPUT already off"
        if output==1: #on
            self.write(":FORM:ELEM CURR")
            self.write(":READ?")
            curr=float(self.read().split('\n')[0])
            if curr < 0.0025:
                self.set_curr_amps(0)
                self.write(":OUTP OFF")
                print "OUTPUT turned off"
            else:
                print "Current %s greater than 0.0025 Amps, please ramp current to zero before turning output off"%str(curr)
        return 0
    def init_curr_source_measure(self,new_curr_range):
        output=self.output_status()
        print output
        if output ==0:
            self.write("*RST")
            self.write(":SOUR:FUNC CURR")
            self.write(":SOUR:CURR:MODE FIXED")
            self.write(":SOUR:CURR:RANGE %s"%new_curr_range)
            self.write(":SOUR:CURR:LEV 0")
            self.write(":SOUR:VOLT:PROT 2")
            self.write(":SENSE:VOLT:PROT 2")
            self.write(":SENSE:FUNC 'CURR'")
            self.write(":FORM:ELEM CURR")
        if output ==1:
            print "Output on, will not reinizialize keithley "
        return 0
    def print_curr(self):
        output=self.output_status()
        if output==1: #on
            self.write(":FORM:ELEM CURR")
            self.write(":READ?")
            curr=self.read().split('\n')[0]
            print "CURRENT=",curr
        if output==0: #off
            print "OUTPUT turned off"
        return 0
    def check_output_on(self):
        output=self.output_status()
        if output==0: #off
            print "OUTPUT is off"
            return output
        if output==1: #on
            print "OUTPUT is on"
            return output
    def get_curr(self):
        self.write(":READ?")
        curr=float(self.read().split('\n')[0])
        return curr
    def print_volt(self):
        output=self.output_status()
        if output==1: #on
            self.write(":FORM:ELEM VOLT")
            self.write(":READ?")
            volt=self.read().split('\n')[0]
            print "VOLTAGE=",volt
        if output==0: #off
            print "OUTPUT turned off"
        return 0
    def update_curr_range(self):
        self.write(":SOUR:CURR:RANGE?")
        curr_range=float(self.read().split('\n')[0])
        self.curr_range=curr_range
        return 0
    def check_curr_range(self,value,max_buffer=0.00005):
        if np.abs(value) >= self.curr_range: 
            value=np.sign(value)*(self.curr_range-max_buffer)
            print "value above current range"
        return value
    def set_curr_amps(self,value,max_step=0.0005,time_step=0.1):
        value=self.check_curr_range(value)
        self.write(":SOURCE:CURR:LEV?")
        curr_lev=float(self.read().split('\n')[0])
        diff=value-curr_lev
        num_steps=int(np.floor(np.abs(diff)/max_step))        
        if num_steps > 0:
            for i in range(num_steps):
                if diff > 0 :
                    step_value=curr_lev+max_step*(i+1)
                elif diff < 0:
                    step_value=curr_lev-max_step*(i+1)
                self.write(":SOURCE:CURR:LEV %s"%step_value)
                self.curr[0]=step_value
                time.sleep(time_step)
            self.write(":SOURCE:CURR:LEV %s"%value)
            self.curr[0]=value
        elif num_steps == 0:
            self.write(":SOURCE:CURR:LEV %s"%value)
            self.curr[0]=value
        return 0
    def daq_keith(self):
        while True:
            time.sleep(0.1)
            self.curr[0]=self.get_curr()
        return 0
    def daq_pid_keith(self, res_val, setpoint=0,P=0,I=0,D=0,factor=1e-9,num=10,max_step=0.001,time_step=0.1):
##does three thing, read current, then calculates pid value to apply form res_val, applies current feedback, start loop again
        self.curr[0]=self.get_curr() #1
        pid=pid_cryocon_keithley.PID(res_val,setpoint=setpoint,P=P,I=I,D=D,factor=factor)
        err_buf=np.zeros(num)
        err_buf[:]=pid.get_error()
        previous_value=self.get_curr()
        time.sleep(4)
        while True:
            time.sleep(0.001)
            self.curr[0]=self.get_curr() #1
            for i in range(num-1):
                err_buf[i+1]=err_buf[i]
            err_buf[0]=pid.get_error()
            delta_value=pid.calc_PID(err_buf)
            if np.abs(delta_value) > max_step:
                delta_value=np.sign(delta_value)*max_step
            self.pid_value[0]=delta_value #2
            value=previous_value+delta_value
            value=self.check_curr_range(value)
            if value < 0:
                value=0
            self.write(":SOURCE:CURR:LEV %s"%value)
            previous_value=value
            time.sleep(time_step)
        return 0
    def set_curr_zero_output_off(self):
        self.set_curr_amps(0)
        self.output_off()

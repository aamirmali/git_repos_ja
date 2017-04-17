import numpy as np

class files:
    '''class that reads the continuity pinout file, and writes the continuity check file '''
    def __init__(self, filename,pinfile):
        self.filename=filename
        self.pinfile=pinfile
        self.pos_pins=[]
        self.neg_pins=[]
        self.slot_pins=[]
        self.name_pins=[]
        
    def read_pins(self):
        fpins=open(self.pinfile,'r')
        is_valid=0
        while not is_valid:
            line=fpins.readline()
            if line=='':
                is_valid=1
            else:
                slot,pin_pos,pin_neg,pin_name=line.split()
                self.slot_pins.append(slot)
                self.name_pins.append(pin_name)
                self.pos_pins.append(pin_pos)
                self.neg_pins.append(pin_neg)
        fpins.close()
        
    def save_cont_check(self,resistances):
         f=open(self.filename,'w')
         for i in np.arange(len(resistances)):
             if resistances[i] == '###':
                 line=[self.slot_pins[i],' ',self.pos_pins[i],' ',self.neg_pins[i],' ',self.name_pins[i],' ',resistances[i],' ','\n']
             else:
                 line=[self.slot_pins[i],' ',self.pos_pins[i],' ',self.neg_pins[i],' ',self.name_pins[i],' ',"{0:.3e}".format(float(resistances[i])),' ','\n']
             f.writelines(line)
         f.close()


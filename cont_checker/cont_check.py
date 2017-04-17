import numpy as np
from IB_tester import IB_tester
from HP_multimeter import HP_multimeter
import cont_files
import argparse

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'

def cont_check_slot(HP, IB, slot, slot_pins,name_pins,pos_pins,neg_pins,resistances,res):
    num=len(slot_pins)
    for i in np.arange(num):
        if slot_pins[i]==slot:
            IB.neg_pin(neg_pins[i])
            IB.pos_pin(pos_pins[i])
            resistances[i]=HP.resistance(resolution = res).split()[0]
            if float(resistances[i]) > 100000: 
                print slot_pins[i],pos_pins[i],neg_pins[i],name_pins[i],FAIL+"{0:.5e}".format(float(resistances[i]))+ENDC
            if float(resistances[i]) < 100000: 
                print slot_pins[i],pos_pins[i],neg_pins[i],name_pins[i],OKGREEN+"{0:.5e}".format(float(resistances[i]))+ENDC



parser=argparse.ArgumentParser(description= 'Run mce continuity check', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('filename', help='Name of file where continuity results are saved' )
parser.add_argument('--pinfile', default='mce_cont_pins.txt', help='Name of file whereto find  the pin mapping for the continuity check' )
parser.add_argument('--res', type=float, default=0.1, help='minimum resolution of resistance measurements, default res=0.1ohm' )

args=parser.parse_args()


IB=IB_tester()
HP=HP_multimeter()

f=cont_files.files(args.filename,args.pinfile)
f.read_pins()
res=args.res

slot_pins=f.slot_pins
num_checks=len(slot_pins)
name_pins=f.name_pins
pos_pins=f.pos_pins
neg_pins=f.neg_pins
resistances=[]
for i in np.arange(num_checks):
    resistances.append('###')

is_valid=0
while not is_valid:
    choice = raw_input('Enter you choice [c to continue with next slot, e to end and save] =')
    print choice
    if choice == 'c':
        slot=IB.slot().split()[0]
        print 'slot=',slot
        cont_check_slot(HP,IB,slot,slot_pins,name_pins,pos_pins,neg_pins,resistances,res)
    elif choice == 'e':
        f.save_cont_check(resistances)
        is_valid=1
    else:
        print choice+' is not a valid choice, try again'





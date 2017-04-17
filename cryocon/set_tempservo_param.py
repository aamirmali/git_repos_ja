import numpy as np
import argparse
import param_file
import res_to_temp


parser=argparse.ArgumentParser(description= 'set cryocon-keithley temperature servo param', formatter_class=argparse.ArgumentDefaultsHelpFormatter,fromfile_prefix_chars='@')

parser.add_argument('--filename', type=str,default='/data/cryocon/servo_param.p',help='file name of pickled file where params are saved, check that it agrees with file used by daemon')
parser.add_argument('--servotemp', type=float, default=0.100,  help='shunt value for calibration')
parser.add_argument('--P', type=float, default=10,  help='Proportional term of feedback')
parser.add_argument('--I', type=float, default=1.0,  help='Integral term of feedback')
parser.add_argument('--D', type=int, default=1.0,  help='Differential term of feedbak')
parser.add_argument('--factor', type=float, default=0.5e-7,  help='temperature for each iv file')
parser.add_argument('--num', type=int, default=600,  help='number of samples that are averaged to multiply I')
parser.add_argument('--info',  action='store_true',  help='prints to screen current param settings, and  makes NO! changes to file')
args=parser.parse_args()


grt=res_to_temp.Res2temp('/home/mce/cryocon/calib_tables/GRT_testdewar.txt')
if args.filename:
    par=param_file.get_params(args.filename)
    sp_res=grt.get_res(args.servotemp)
    if not args.info:
        print "servo temp=",args.servotemp
        print "servo resistance=",sp_res
        par.sp_res=sp_res
        par.P=args.P
        par.I=args.I
        par.D=args.D
        par.factor=args.factor
        par.num=args.num
        param_file.write_params(args.filename,par)
    else:
        print "servo resistance=",par.sp_res
        print "P=",par.P
        print "I=",par.I
        print "D=",par.D
        print "factor=",par.factor
        print "num=",par.num
else:
    sp_res=grt.get_res(args.servotemp)
    par=param_file.Params(sp_res,args.P,args.I,args.D,args.factor,args.num)
    param_file.write_params(args.filename,par)
    print "made new param pickle file"

if args.info:
    grt=res_to_temp.Res2temp('/home/mce/cryocon/calib_tables/GRT_testdewar.txt')
    sp_res=grt.get_res(args.servotemp)


import sys
import argparse
import numpy as np
from stepanalyzer import StepAnalyzer
from code.common import filehandler
#set constants
try:
    import array_ABS_cfg as config
    dac_bits=config.fb_DAC_bits
    Rfb=config.Rfb
    M_ratio=config.M_ratio
except ImportError:
    dac_bits=14
    Rfb=7084
    M_ratio=8.5


def handle_cal(args):
    #handler for subcommand "calibrate"
    #read in data; make sure it's a 3D array
    data=filehandler.get_mce_data(args.filename, row_col=True)
    if len(data.shape)!=3:
        print "Data is not three dimensional!"
        sys.exit(1)
    nrows=data.shape[0]
    ncols=data.shape[1]
    #Check which mode the program is in; that is, check whether user gave
    #STEPSIZE CALFILE DATAFILE, or IV0 IV_HEATER DATAFILE. Respond 
    #appropriately.
    try:
        stepsize=float(args.arg1)
        calfile=args.arg2
        diff_biases=filehandler.IV_data_to_arr(calfile,"Power_per_Dac")
        if len(diff_biases)==0:
            print calfile,"is invalid!"
            sys.exit(1)
        if data.shape[0:2] != diff_biases.shape:
            print "Data is not of same dimension as calibration file",calfile
            sys.exit(1)
        diff_biases *= stepsize
    except ValueError:
        #means 1st argument is not a number
        iv0=args.arg1
        iv_heater=args.arg2
        pSat_control=1e-12*filehandler.IV_data_to_arr(iv0,"Bias_Power")
        if len(pSat_control)==0:
            print iv0,"is invalid!"
            sys.exit(1)
        pSat_heater=1e-12*filehandler.IV_data_to_arr(iv_heater,"Bias_Power")
        if len(pSat_heater)==0:
            print iv_heater,"is invalid!"
            sys.exit(1)
        if data.shape[0:2] != pSat_control.shape:
            print "Data is not of the same dimension as bias powers in",iv0
            sys.exit(1)
        if data.shape[0:2] != pSat_heater.shape:
            print "Data is not of the same dimension as bias powers"\
                " in",iv_heater
            sys.exit(1)
        diff_biases=pSat_control-pSat_heater
        #Traverse pSat_control and pSat_heater; if a 0 entry exists in either 
        #file, set corresponding entry in diff_biases to 0 (invalid)
        for row in range(nrows):
            for col in range(ncols):
                if pSat_control[row][col]==0 or pSat_heater[row][col]==0:
                    diff_biases[row][col]=0
    amplitudes=np.zeros((nrows,ncols))
    quartile_ranges=np.zeros((nrows,ncols))
    data_qualities=np.zeros((nrows,ncols))
    responsivities=np.zeros((nrows,ncols))
    periods=np.zeros((nrows,ncols))
    num_amplitudes=np.zeros((nrows,ncols))
    #printout("step_quality",data_qualities)
    print "User input read-in successful. Beginning computation."
    for col in range(ncols):
        print "On col",col
        for row in range(nrows):
            single_data=data[row][col]
            x=StepAnalyzer(single_data,verbose=False)
            amplitude=x.get_med_amplitude()
            quartile_range=x.get_quartile_amplitude()
            method_used=x.get_method_used()
            data_quality=0
            if method_used=='ramping' or method_used=='noise' \
                    or method_used=='off':
                data_quality=0
            elif method_used=='std':
                data_quality=1
            elif method_used=='cross-corr' and x.crosscorr_error>0:
                data_quality=2
            elif method_used=='cross-corr' and x.crosscorr_error==0:
                data_quality=3
            elif method_used=='best':
                data_quality=4
            data_qualities[row][col]=data_quality
            if amplitude!=None:
                amplitudes[row][col]=amplitude
                if diff_biases[row][col]>0:
                    responsivities[row][col]=diff_biases[row][col]/amplitude
            if quartile_range!=None and amplitude!=None:
                quartile_ranges[row][col]=quartile_range/amplitude
            if (method_used=='best' or method_used=='cross-corr') and\
                    x.period!=None:
                periods[row][col]=x.period
                num_amplitudes[row][col]=len(x.amplitudes)
    to_amps=1./filtgain*1./2**dac_bits*(1./50)/(1./Rfb+1./50)/(M_ratio*Rfb)
    to_dac=1./filtgain
    f=args.filename #destination file
    filehandler.printout("step_quality",data_qualities,f)
    filehandler.printout("step_amplitude(A)",amplitudes*to_amps,f)
    filehandler.printout("amplitude_quartile_range(fraction)",
                         quartile_ranges,f)
    filehandler.printout("responsivity(W/Dac)",responsivities/to_dac,f)
    filehandler.printout("responsivity(W/A)",responsivities/to_amps,f)
    filehandler.printout("period(indices)",periods,f)
    filehandler.printout("num_amplitudes",num_amplitudes,f)


def handle_analyze(args):
    #handler for subcommand 'analyze'
    data=filehandler.get_mce_data(args.filename, row_col=True)
    nrows=data.shape[0]
    ncols=data.shape[1]
    for col in range(0,ncols):
        for row in range(0,nrows):
            single_data=data[row][col]
            x=StepAnalyzer(single_data,verbose=False)
            method_used=x.get_method_used()
            data_quality=''
            if method_used=='ramping':
                data_quality='ramping'
            elif method_used=='noise':
                data_quality='noise'
            elif method_used=='off':
                data_quality='off'
            elif method_used=='std':
                data_quality='poor'
            elif method_used=='cross-corr' and x.crosscorr_error>0:
                data_quality='ok'
            elif method_used=='cross-corr' and x.crosscorr_error==0:
                data_quality='good'
            elif method_used=='best':
                data_quality='excellent'
            else:
                assert(False)
            print "*col",col,"row",row,data_quality

    
def handle_diff(args):
    #handler for subcommand 'diff'
    if args.step_size<=0:
        print "invalid step size!"
        sys.exit(1)
    #factor of 1e-12 to convert from pW to W
    pSat_control=1e-12*filehandler.IV_data_to_arr(args.iv0,"Bias_Power")
    pSat_heater=1e-12*filehandler.IV_data_to_arr(args.ivN,"Bias_Power")
    if pSat_control.shape != pSat_heater.shape:
        print "Dimensions of data in IV .out files don't match!"
        sys.exit(1)
    diff_power=pSat_control-pSat_heater
    diff_power_per_step=diff_power/float(args.step_size)
    #If an element in either pSat_control or pSat_heater is invalid (0),
    #corresponding entry in diff_power_per_step should also be invalid (0)
    for row in range(pSat_control.shape[0]):
        for col in range(pSat_control.shape[1]):
            if pSat_control[row][col]==0 or pSat_heater[row][col]==0:
                diff_power_per_step[row][col]=0
    #Now write result to file
    if args.filename==None:
        filehandler.printout("Power_per_Dac(W/Dac)",diff_power_per_step,
                             sys.stdout)
    else:
        with open(args.filename,'w') as f:
            filehandler.printout("Power_per_Dac(W/Dac)",diff_power_per_step,f)


parser=argparse.ArgumentParser(description='Master script for all heater'\
                                   ' block analysis. Use subcommands.')
subparsers=parser.add_subparsers(title='Subcommands',
                                 description='To get help for subcommand foo,'\
                                     ' run python %(prog)s foo -h')
cal_description='Writes a .out file of heater data'
calparse=subparsers.add_parser('calibrate',help=cal_description,
                               description=cal_description,
                               usage=
                               '%(prog)s [options] STEPSIZE CALFILE DATAFILE'\
                               '\n  or %(prog)s [options] '\
                               'IV0 IV_HEATER DATAFILE')
calparse.add_argument('-f','--filename',type=argparse.FileType('w'),
                    default=sys.stdout,
                    help='destination file. Default stdout.')
calparse.add_argument('arg1',metavar='ARG1',
                    help='Either the size of the heater blocks, '\
                    'or the IV .out file with no heater blocks')
calparse.add_argument('arg2',metavar='ARG2',
                    help='Either the calibration file containing power/Dac'\
                    ' information, or the IV .out file with heater blocks')
calparse.add_argument('datafile',metavar='DATAFILE',
                    help='the detector data to be used')
calparse.set_defaults(func=handle_cal)
analyzer_description='analyzes a data file, printing out the heater block'\
    ' quality for each detector.'
anparse=subparsers.add_parser('analyze',help=analyzer_description,
                              description=analyzer_description)
anparse.add_argument('filename',help='file to analyze')
anparse.set_defaults(func=handle_analyze)
diff_description='Write file with bias power per step size info'
diffparse=subparsers.add_parser('diff',help=diff_description,
                                description=diff_description)
diffparse.add_argument('-f','--filename',
                       help='destination file. Default stdout.')
diffparse.add_argument('step_size',metavar='STEPSIZE',type=int,
                    help='amount of power applied to heaters')
diffparse.add_argument('iv0',metavar='IV0',
                       help='.out file with no heater steps')
diffparse.add_argument('ivN',metavar='IVN',help='.out file with heater steps')
diffparse.set_defaults(func=handle_diff)
args=parser.parse_args()
args.func(args)

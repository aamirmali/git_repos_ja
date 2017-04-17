"""This module is a stand-alone program that plots the power spectrum and/or
timestream of a given data file.  Run python prog_name -h, or read the source
code, for detailed help."""
import sys
import argparse
import numpy as np
from spectrumanalyzer import SpectrumAnalyzer
import code.common.filehandler as fh
parser=argparse.ArgumentParser(description=
                               'Plots the power spectra and/or timestreams'\
                                   ' of specified detectors',
                               formatter_class=
                               argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-r','--rows',type=int,nargs='*',
                    help='rows to be plotted. Can specify more than 1 with'\
                        'space-delimited list. Leave out to indicate all rows')
parser.add_argument('-c','--cols',type=int,nargs='*',
                    help='columns to be plotted. Can specify more than 1 with'\
                        'space-delimited list. Leave out to indicate all cols')
parser.add_argument('-p','--plot',choices=['timestream','psd','both','none'],
                    default='both',help='what to plot')
parser.add_argument('--nfft',type=int, default=1024,
                    help='number of datapoints used in each block for FFT')
parser.add_argument('--ivfile',help='specify an IV .out file. Causes program '\
                        'to convert all PSDs to W/rtHz')
parser.add_argument('--subtract-mean',action='store_true',
                    help='if set, subtracts mean before plotting timestream')
parser.add_argument('--format',help='format for PSD axes',default='semilogy',
                    choices=['loglog','semilogx','semilogy','linear'])
parser.add_argument('-e','--exclude-bad-cols',type=int,nargs='*',metavar='COL',
                    help='The columns to exclude. If no argument is given,'\
                        ' excludes all columns from 4 to 15 inclusive.')
parser.add_argument('--samp-freq',type=float,default=200,
                    help='samping frequency')
parser.add_argument('--filtgain',type=float,default=1311,
                    help='sets the filter gain')
parser.add_argument('--M-ratio',type=float,default=8.5,help='sets the M ratio')
parser.add_argument('--dac-bits',type=int,default=14,
                    help='sets number of bits in DAC output')
parser.add_argument('--Rfb',type=float,default=7084,help='sets Rfb')
parser.add_argument('--mapfile',default=None,nargs='?',const='mce_pod_map.txt',
                    help='if set, uses mapfile to only plot detectors that'\
                        ' correspond to a TES. If an argument is given, uses '\
                        'that argument as map file; if not, uses default of '\
                        'mce_pod_map.txt')
parser.add_argument('--psd-min',type=float,
                    help='If plotting waterfall PSD, all values below this'\
                        ' are considered invalid. If plotting normal PSD, this'\
                        ' becomes lower limit of y axis.')
parser.add_argument('--psd-max',type=float,
                    help='If plotting waterfall PSD, all values above this'\
                        ' are considered invalid. If plotting normal PSD, this'\
                        ' becomes upper limit of y axis.')
parser.add_argument('--waterfall-row',action='store_true',
                    help='if plotting waterfall, make plot row dominated')
parser.add_argument('--print-special',choices=['darks','squids','ramping'])
parser.add_argument('--write-amplitudes',nargs=3,
                    metavar=('FREQ','HALFSIZE','FILE'),
                    help='writes out the mean of the points between'\
                        ' FREQ-HALFSIZE Hz and FREQ+HALFSIZE Hz to FILE, in'\
                        ' the format of a .out file. Outputs both the'\
                        ' amplitudes themselves, and their log. Bad cols,'\
                        ' as well as detectors with amplitudes <=0, will be'\
                        ' indicated with a 0')
parser.add_argument('-i','--invert-filter-of-type',type=int,choices=[1,2,3,255],
                    help='If used, undos effect of integrated Butterworth'\
                        ' filter of the specified type. If type is 255,'\
                        '--filter-params must be used.')
parser.add_argument('--filter-params',nargs=7,type=float,
                    metavar=('REAL_SAMP_FREQ','b11','b12','b21','b22','k1',
                             'k2'),
                    help='the filter parameters. Can only be used if '\
                        'invert-filter-of-type is specified and set to 255. '\
                        'real_samp_freq is the actual sample frequency of the'\
                        ' timestream, in Hertz.')
parser.add_argument('--fontsize',type=int,help='changes the font size of all'\
                        ' text')
parser.add_argument('--fontweight',help='changes the weight of all text.  Can'\
                        ' be a numeric value from 0-1000 or one of the'\
                        ' following: ultralight, light, normal, regular,'\
                        ' book, medium, roman, semibold, demibold, demi,'\
                        ' bold, heavy, extra bold, black')
parser.add_argument('--grid',action='store_true',help='whether to plot a mesh'\
                        ' grid overlay')
parser.add_argument('--hide-legend',action='store_true',
                    help='hides the legend on all graphs')
parser.add_argument('--save',action='store_true',
                    help="saves to file instead of showing. Files are saved"\
                        " to the directory filename+'_data'")
parser.add_argument('filename',help='the data file to analyze')
args=parser.parse_args()
#verify arguments, set parameters
plot_psds=True
plot_timestream=True
use_mapfile=False
bad_cols=None
filter_params=None #dictionary, not list (unlike args.filter_params)
if args.plot=='timestream':
    plot_psds=False
elif args.plot=='psd':
    plot_timestream=False
elif args.plot!='both' and args.plot!='none':
    assert(False)
if args.subtract_mean and args.plot=='psd':
    print "Not plotting timestream, so ignoring --subtract-mean"
if args.subtract_mean and args.rows==None and args.cols==None:
    print "can't plot timestream; ignoring subtract_mean"
if args.mapfile != None:
    use_mapfile=True
if args.exclude_bad_cols != None:
    if len(args.exclude_bad_cols)==0:
        #no argument given, so use default range
        bad_cols=range(4,16)
    else:
        bad_cols=args.exclude_bad_cols
if args.rows==None and args.cols==None and \
        (args.format!='linear' and args.format!='semilogy'):
    print "Only linear and semilogy supported for waterfall plot!"
    sys.exit(1)
if (args.rows!=None or args.cols!=None) and args.waterfall_row:
    print "Ignoring option --waterfall-row; not applicable"
if args.invert_filter_of_type==1 or args.invert_filter_of_type==2 or args.invert_filter_of_type==3:
    filter_params={'type':args.invert_filter_of_type,'real_samp_freq':None,
                       'b11':None,'b12':None,'b21':None,'b22':None,'k1':None,
                       'k2':None}
elif args.invert_filter_of_type==255:
    if args.filter_params==None:
        print "Must specify filter parameters!"
        sys.exit(1)
    filter_params=dict()
    filter_params['type']=255
    filter_params['real_samp_freq']=args.filter_params[0]
    filter_params['b11']=args.filter_params[1]
    filter_params['b12']=args.filter_params[2]
    filter_params['b21']=args.filter_params[3]
    filter_params['b22']=args.filter_params[4]
    filter_params['k1']=args.filter_params[5]
    filter_params['k2']=args.filter_params[6]
if args.write_amplitudes != None:
    #check to make sure first two arguments are valid floating point nums
    try:
        float(args.write_amplitudes[0])
        float(args.write_amplitudes[1])
    except ValueError:
        print "Invalid frequency and/or halfsize for --print-amplitudes!"
        sys.exit(1)

#execute
data=fh.get_mce_data(args.filename, row_col=True)
#verify bad_cols. Are all column numbers valid?
if args.exclude_bad_cols != None:
    for i in range(len(bad_cols)):
        if bad_cols[i] < 0 or bad_cols[i] >= data.shape[1]:
            print "exclude-bad-cols received invalid column!"
            sys.exit(1)
finder=SpectrumAnalyzer(data,NFFT=args.nfft,ivfile=args.ivfile,
                        use_mapfile=use_mapfile,mapfile=args.mapfile,
                        bad_cols=bad_cols,subtract_mean=args.subtract_mean,
                        sampling_freq=args.samp_freq,filtgain=args.filtgain,
                        M_ratio=args.M_ratio,dac_bits=args.dac_bits,
                        Rfb=args.Rfb,filter_params=filter_params)
if args.print_special=='darks':
    finder.print_specs(finder.dark_detectors)
elif args.print_special=='squids':
    finder.print_specs(finder.dark_squids)
elif args.print_special=='ramping':
    finder.print_specs(finder.ramping_detectors)
if args.write_amplitudes!=None:
    freq=float(args.write_amplitudes[0])
    halfsize=float(args.write_amplitudes[1])
    f=open(args.write_amplitudes[2],'w')
    all_amps=finder.get_all_avg_strength(freq,halfsize)
    all_amps_log=np.zeros(all_amps.shape)
    #go through returned amplitudes, looking for invalid entries and taking
    #the log of valid ones
    for i in range(len(all_amps.flat)):
        if all_amps.flat[i]<=0:
            all_amps.flat[i]=0
        else:
            all_amps_log.flat[i]=np.log10(all_amps.flat[i])
    formatstring='power_at_'+str(freq)+"_Hz"
    if args.ivfile==None:
        formatstring+='(A^2/Hz)'
    else:
        formatstring+='(W/rtHz)'
    fh.printout('linear_'+formatstring,all_amps,f)
    fh.printout('log_'+formatstring,all_amps_log,f)
    f.close()
if args.plot=='none':
    sys.exit(1)
#set up dictionary of common args. psd_min and psd_max aren't needed when
#plotting timestreams, but no harm in passing them anyways (they get ignored)
common_args = {'plot_format':args.format, 'psd_min': args.psd_min,
               'psd_max':args.psd_max,'fontsize':args.fontsize,
               'fontweight':args.fontweight,'plot_grid':args.grid,
               'hide_legend':args.hide_legend}
if args.rows==None and args.cols==None:
    if args.waterfall_row==True:
        domination='row'
    else:
        domination='col'
    finder.plot_waterfall(domination=domination,**common_args)
elif args.rows!=None and args.cols!=None:
    #plot for every row/col combination; PSDs first, then timestreams
    title_suffix=' of rows '+str(args.rows)+', cols '+str(args.cols)
    for row in args.rows:
        for col in args.cols:
            finder.plot_result(row=row,col=col,
                               plot_psds=plot_psds, plot_timestream=False,
                               new_figure=False,title='PSDs'+title_suffix,
                               **common_args)
    if plot_timestream and plot_psds:
        finder.new_fig()
    for row in args.rows:
        for col in args.cols:
            finder.plot_result(row=row,col=col,
                               plot_psds=False,plot_timestream=plot_timestream,
                               new_figure=False,
                               timestream_title='Timestreams'+title_suffix,
                               **common_args)
elif args.rows!=None and args.cols==None:
    #user has indicated many rows but no column; plot rows
    for row in args.rows:
        #first plot PSDs, if appropriate
        finder.plot_result(row=row,plot_psds=plot_psds,
                       plot_timestream=False,new_figure=False,
                           title='PSDs of rows '+str(args.rows),
                           n_legend_cols=len(args.rows),
                           **common_args)
    if plot_timestream and plot_psds:
        finder.new_fig()
    #now plot timestreams, if appropriate
    for row in args.rows:
        finder.plot_result(row=row,plot_psds=False,
                           plot_timestream=plot_timestream,new_figure=False,
                           timestream_title=
                           'Timestreams of rows '+str(args.rows),
                           n_legend_cols=len(args.rows),
                           **common_args)
elif args.rows==None and args.cols!=None:
    #user has indicated many columns but no row; plot columns
    for col in args.cols:
        #first plot PSDs, if appropriate
        finder.plot_result(col=col,plot_psds=plot_psds,
                           plot_timestream=False,new_figure=False,
                           title='PSDs of cols '+str(args.cols),
                           n_legend_cols=len(args.cols), **common_args)
    if plot_psds and plot_timestream:
        finder.new_fig()
    for col in args.cols:
        #now plot timestreams, if appropriate
        finder.plot_result(col=col,plot_psds=False,
                           plot_timestream=plot_timestream,new_figure=False,
                           timestream_title=
                           'Timestreams of cols '+str(args.cols),
                           n_legend_cols=len(args.cols),
                           **common_args)
else:
    #user input check should guarantee against this condition
    assert(False)
if args.save==True:
    finder.show(args.filename+'_graphs')
else:
    finder.show()

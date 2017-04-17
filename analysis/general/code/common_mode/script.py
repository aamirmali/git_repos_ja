"""This command-line interface uses common_plotter.py to plot the common modes
of all columns, as well as the common mode of the data as a whole."""
import argparse
import numpy as np
import sys
import os
from python import mce_data
from common_plotter import CommonPlotter

parser=argparse.ArgumentParser(
    description='Plots the common mode of columns, as well as that of all the'\
        '  data combined. Unless otherwise specified, saves plots to the'\
        ' current directory',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    fromfile_prefix_chars='@')
parser.add_argument('--flipper',nargs='*',type=int,
                    help="Flips columns by multiplying column i's data by the"\
                        " ith argument. Must give one argument for each"\
                        " column of data.")
parser.add_argument('-n','--normalize',action='store_true',
                    help='normalizes each timestream before adding it to the'\
                        ' common mode')
parser.add_argument('-s','--show',action='store_true',
                    help='show the plots, instead of saving them')
parser.add_argument('-p','--plot',choices=['timestream','psd','both'],
                    default='both',help='what to plot')
parser.add_argument('--overplot',action='store_true',
                    help='plots different columns on the same graph')
include_parser=parser.add_mutually_exclusive_group()
include_parser.add_argument('-i','--include-cols',type=int,nargs='*',
                            metavar='COL',
                            help='if this option is used, includes only the'\
                                ' specified columns.')
include_parser.add_argument('-e','--exclude-cols',type=int,nargs='*',
                            metavar='COL',
                            help='if this option is used, excludes only the'\
                                ' specified columns. If no arguments are'\
                                ' given, excludes cols 4-15 inclusive.')
parser.add_argument('-o','--omit-common-all',action='store_true',
                    help='avoid plotting the common mode of all data')
parser.add_argument('--directory',default='.',
                    help="specify a directory to save to. If it doesn't"\
                        " exist, it will be created.")
parser.add_argument('--nfft',type=int, default=1024,
                    help='number of datapoints used in each block for FFT')
parser.add_argument('--format',help='format for PSD axes',default='semilogy',
                    choices=['loglog','semilogx','semilogy','linear'])
parser.add_argument('--samp-freq',type=float,default=399,
                    help='samping frequency')
parser.add_argument('--filtgain',type=float,default=1218,
                    help='sets the filter gain')
parser.add_argument('--M-ratio',type=float,default=8.5,help='sets the M ratio')
parser.add_argument('--dac-bits',type=int,default=14,
                    help='sets number of bits in DAC output')
parser.add_argument('--Rfb',type=float,default=7084,help='sets Rfb')
parser.add_argument('filename',help='the data file to analyze')
args=parser.parse_args()
#read in data, verify user arguments
conversion=1./args.filtgain/2**args.dac_bits*(1./50)/(1./args.Rfb+1./50)/(args.M_ratio*args.Rfb)
mce=mce_data.SmallMCEFile(args.filename)
data=mce.Read(row_col=True).data*conversion
nrows=data.shape[0]
ncols=data.shape[1]
if args.flipper != None:
    if len(args.flipper) != ncols:
        print "Too many or too few arguments for --flipper!"
        sys.exit(1)
    for col in range(ncols):
        data[:,col] *= args.flipper[col]
include_col=np.ones(ncols)>0 #initialize to True
if args.include_cols != None:
    include_col=np.zeros(ncols) > 1 #initialize mask to False
    for col in args.include_cols:
        if col >= ncols:
            print "One or more columns for --include-cols is out of range!"
            sys.exit(1)
        include_col[col]=True
if args.exclude_cols != None:
    if len(args.exclude_cols)==0: to_exclude=range(4,16)
    else: to_exclude=args.exclude_cols
    for col in to_exclude:
        if col>= ncols:
            print "One or more columns to be excluded is out of range!"
            sys.exit(1)
        include_col[col]=False
if args.format != 'linear' and args.plot=='timestream':
    print "Ignoring --format; cannot be specified for timestreams"
#initialize save_dir to appropriate directory (None if the user doesn't want
#to save)
if args.show:
    save_dir=None
else:
    save_dir=args.directory
if save_dir != None and not os.path.exists(save_dir):
    os.makedirs(save_dir)
#execute
plotter=CommonPlotter(data,include_col=include_col,normalize=args.normalize)
if args.plot == 'timestream' or args.plot=='both':
    plotter.plot_timestreams(save_dir=save_dir,overplot=args.overplot)
    if args.omit_common_all==False:
        plotter.new_fig()
        plotter.plot_timestream_all(save_dir)
if args.plot=='both':
    plotter.new_fig()
if args.plot=='psd' or args.plot=='both':
    plotter.plot_psds(NFFT=args.nfft,sampling_freq=args.samp_freq,
                      plot_format=args.format,save_dir=save_dir,
                      overplot=args.overplot)
    if args.omit_common_all==False:
        plotter.new_fig()
        plotter.plot_psd_all(save_dir=save_dir,sampling_freq=args.samp_freq,
                             NFFT=args.nfft,plot_format=args.format)
if args.show:
    plotter.show()

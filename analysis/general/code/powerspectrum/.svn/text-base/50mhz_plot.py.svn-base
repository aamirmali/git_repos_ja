"""This module is a stand-alone program that takes a directory with 50MHz data
files, and plots a waterfall PSD of all files. The files must follow the form
'*rc(r)_col(c), where (r) must be between 0 and 3, 'and (c) must be between 0
and 7, both inclusive. Any files that don't follow this format are ignored.
For additional help, run with -h."""
import glob
import sys
import os
import argparse
from python import mce_data
from find_spectrum import SpectrumAnalyzer
import numpy as np
def load_arr(directory,n_rcs=4,cols_per_rc=8):
    #This function reads in all files in directory of the format *rc(r)_col(c),
    #where (r) is an integer between 0 and n_rcs and (c) is an integer from
    #0 to cols_per_rc, including 0 but not the upper bound.  The data must be
    #of dimension 1x1xn.  Returns the data in an array of dimension 
    #1 x num_files x n, or None if the data could not be read in.
    all_data=[[]]
    for i in range(n_rcs):
        for j in range(cols_per_rc):
            datafile='*rc'+str(i)+'_col'+str(j)
            #0th element because return result is a list with 1 element
            datafile=glob.glob(os.path.join(directory,datafile))
            if len(datafile) != 0:
                datafile=datafile[0]
                mce=mce_data.SmallMCEFile(datafile)
                data=mce.Read(row_col=True).data
                if len(data.shape)!=3:
                    print "Data must be 3D!"
                    return None
                if data.shape[0]!=1 or data.shape[1]!=1:
                    print "Data must be of form 1x1xn!"
                    return None
                all_data[0].append(data[0][0])
    if len(all_data)==0:
        print "No data read in!"
        return None
    return np.array(all_data)

#Main
parser=argparse.ArgumentParser(description=
                               'Plots waterfall PSD of 50MHz data in all'\
                                   'files of a directory.')
parser.add_argument('directory',
                    help='the data directory. Its files must follow the form'\
                        '*rc(r)_col(c), where (r) must be between 0 and 3,'\
                        'and (c) must be between 0 and 7, both inclusive.')
parser.add_argument('--nfft',type=int,default=1024,
                    help='number of datapoints used in each block for FFT')
parser.add_argument('--col-divisions',type=int,default=10,
                    help='spacing between labels on column axis. Default 10.')
args=parser.parse_args()
all_data=load_arr(args.directory)
if all_data==None:
    sys.exit(1)
finder=SpectrumAnalyzer(all_data,sampling_freq=5e7,use_mapfile=False,
                        NFFT=args.nfft)
finder.plot_waterfall(col_divisions=args.col_divisions)
finder.show()

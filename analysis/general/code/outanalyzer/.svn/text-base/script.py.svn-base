"""This command-line interface takes a .out file and a search string, and
for each column, prints out statistics along with drawing a histogram. It also
does this for the dataset as a whole."""
import os
import sys
import numpy as np
import argparse
import matplotlib.pyplot as plt
import code.common.filehandler as fh

parser=argparse.ArgumentParser(
    description="Analyzes a .out file and, for each column, prints out"\
        " statistics along with drawing a histogram. Also does this for the"\
        " dataset as a whole.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('filename',help="the .out file to be analyzed")
parser.add_argument('search_string',help='string used to identify which'\
                        ' property in the file should be used')
parser.add_argument('-s','--save',metavar='DIRECTORY',const='.',nargs='?',
                    help="saves all plots and results, instead of plotting"\
                        " them and printing them to stdout. If an argument is"\
                        " specified, saves to that directory, creating it if"\
                        " it doesn't exist. Otherwise, uses the current"\
                        " directory. The text results file is called"\
                        " stats_results; the histograms are hist_col1.png,"\
                        " hist_col2.png, etc.")
parser.add_argument('-b','--bins',type=int,default=10,
                    help='the number of bins to use in the histograms.')
parser.add_argument('-p','--plot',type=int,default=0,
                    help='set to 1 to plot histograms')
parser.add_argument('--exclude-cols',type=int,nargs='*',metavar='COL',
                    help='The columns to exclude. If no argument is given,'\
                        ' excludes all columns from 4 to 15 inclusive.')
args=parser.parse_args()

#process arguments
data=fh.IV_data_to_arr(args.filename,args.search_string)
if data==None:
    print "Your search_string returned no data!"
    sys.exit(1)
if args.save != None:
    save_dir=args.save
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    results_path=os.path.join(save_dir,'stats_results')
    f=open(results_path,'w')
else:
    #print to standard out by default
    f=sys.stdout
bad_cols=[]
if args.exclude_cols != None and len(args.exclude_cols)==0:
    #user specified --exclude-cols without any arguments
    bad_cols=range(4,16)
elif args.exclude_cols != None and len(args.exclude_cols)>0:
    bad_cols=args.exclude_cols

#start printout
f.write(args.search_string+" for "+args.filename+'\n')
#first, print out summary of all data
all_data=[]
for row in range(data.shape[0]):
    for col in range(data.shape[1]):
        if col not in bad_cols:
            all_data.append(data[row][col])
f.write('Mean for all data: '+str(np.mean(all_data))+'\n')
f.write('STD for all data: '+str(np.std(all_data))+'\n')
f.write('Median for all data: '+str(np.median(all_data))+'\n')
if args.plot==1:
    plt.hist(all_data,bins=args.bins)
    plt.title(args.search_string+' for all data')
for col in range(data.shape[1]):
    if col in bad_cols:
        continue
    col_data=data[:,col]
    f.write('Col '+str(col)+' mean: '+str(np.mean(col_data))+'\n')
    f.write('Col '+str(col)+' std: '+str(np.std(col_data))+'\n')
    f.write('Col '+str(col)+' median: '+str(np.median(col_data))+'\n')
    f.write('\n')
    if args.plot==1:
        plt.figure()
        plt.hist(col_data,bins=args.bins)
        plt.title(args.search_string+" for col "+str(col))
    if args.save != None:
        filename=os.path.join(args.save,'hist_col'+"%02i"%col+'.png')
        plt.savefig(filename)
if args.save==None:
    if args.plot==1:
        plt.show()

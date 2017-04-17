"""This is a command-line interface for using draw_ellipses."""
import sys
import argparse
import matplotlib.pyplot as plt
from prettythingsdrawer import PrettyThingsDrawer

#collect arguments
parser=argparse.ArgumentParser(
    description="Plots detector array, with each detector's properties color-"\
        "coded.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('file',help='file containing detector data, in the format'\
                        'of .out files.')
parser.add_argument('search_string',help='string used to identify which'\
                        ' property in the file should be used')
parser.add_argument('probe',choices=('A','B','AB'),
                    help='chooses which probe should be used. Note that if AB'\
                        ' is specified, --other-data cannot be used. Also'\
                        ' note that if AB is specified, A ellipses are'\
                        ' horizontal; B ellipses are vertical')
parser.add_argument('--frequency',default=145,type=int,
                    help='specifies which frequency to search for in '\
                        'beam centers file.')
parser.add_argument('--mapfile',default='code/ellipsesdrawer/mce_pod_map.txt',
                    help="set custom map file, containing the correspondance"\
                        " between row/col format and pod/feed/probe format."\
                        " The first line of the map file is discarded. The"\
                        " remaining lines' columns must be in the following"\
                        " order: pod #, feed #, MCE col (starting from 0),"\
                        " MCE row for probe A (starting from 1), and MCE row"\
                        " for probe B (starting from 1)")
parser.add_argument('--angle-file',help="use this file to specify angles of"\
                        " the ellipses. The first line is discarded. The"\
                        " remaining lines' 3rd and 4th columns must be probe"\
                        " A's angle and probe B's angle, respectively. The"\
                        " file must be ordered: the 2nd line must be for pod"\
                        " 1 feed 1, the 3rd for pod 1 feed 2, etc.")
parser.add_argument('-o','--other-data',nargs=3,
                    metavar=('FILE','SEARCH_STRING','PROBE'),
                    help='plots other set of data. Arguments should be in'\
                        'exactly the same order and format as the main'\
                        'positional arguments of this program. other-data is '\
                        'represented as vertical ellipses; the original data '\
                        'is represented as horizontal ellipses.')
converter=parser.add_mutually_exclusive_group()
converter.add_argument('--set-clim',nargs=2,type=float,
                       metavar=('LOWER','UPPER'),
                       help='sets the lower and upper color limits.')
converter.add_argument('-t','--threshold',
                       nargs='+',metavar='THRES',type=float,
                       help="thresholds the data. The thresholds must be in"\
                           " order, from lowest to highest. Data points are"\
                           " assigned discrete values depending on which"\
                           " interval they fall under. There's no need to"\
                           " know what these values are, because an"\
                           " informative legend will be created.")
converter.add_argument('--min-max',nargs=2,type=float,metavar=('MIN','MAX'),
                    help='If specified, sets everything below min to min, and'\
                        ' above max to max.')
parser.add_argument('--title',help='manually set the title')
parser.add_argument('--cbar-label',default='label',help='manually set the colorbar label')
parser.add_argument('--fontsize',type=int,help='set the font size of title')
parser.add_argument('--fontweight',
                    help='set font weight of title. Valid options: 0-1000, or'\
                        ' ultralight, light, normal, regular, book, medium, '\
                        'roman, semibold, demibold, demi, bold, heavy, extra'\
                        ' bold, black')
parser.add_argument('--save',metavar='FILENAME',nargs='?',
                    const='ellipses_plot.png',
                    help='Saves graph instead of showing it on screen. If an '\
                        'argument is specified, saves to that file. If not,'\
                        ' saves to %(const)s in current directory.')
args=parser.parse_args()
#validate arguments                 
if args.probe=='AB' and args.other_data != None:
    print "Both probe=AB and --other-data were specified! Can only use one"
    sys.exit(1)
if args.other_data != None:
    probe=args.other_data[2]
    if probe != 'A' and probe != 'B':
        print "Probe for --other-data must be either A or B!"
        sys.exit(1)
if args.set_clim != None and args.set_clim[0]>=args.set_clim[1]:
    print "Lower limit greater than or equal to upper limit for --set-clim!"
    sys.exit(1)
if args.min_max != None and args.min_max[0]>=args.min_max[1]:
    print "Lower limit greater than or equal to upper limit for --min-max!"
    sys.exit(1)
if args.threshold != None:
    for i in range(len(args.threshold)-1):
        if args.threshold[i+1]<=args.threshold[i]:
            print "--threshold arguments invalid!"
            sys.exit(1)
#execute
drawer=PrettyThingsDrawer(
    map_file=args.mapfile,frequency=args.frequency,
    beam_centers_file='code/ellipsesdrawer/beamCenters.txt',
    angle_file=args.angle_file)
#Basic arguments to draw_ellipses. Code further down modifies this dictionary
#before passing to to draw_ellipses.
ellipses_args={'raw_data_file':args.file,
               'search_string':args.search_string,'A_or_B':args.probe,
               'angle':0,'major_axis':20,'minor_axis':6,
               'title':args.title,'fontsize':args.fontsize,
               'fontweight':args.fontweight}
if args.angle_file != None:
    ellipses_args['angle'] = None
if args.min_max != None:
    ellipses_args['convert']='normal'
    ellipses_args['min_val']=args.min_max[0]
    ellipses_args['max_val']=args.min_max[1]
if args.set_clim != None:
    clim=(args.set_clim[0],args.set_clim[1])
    ellipses_args['colorbar_lim']=clim
if args.threshold != None:
    nthres=len(args.threshold)
    def threshold(x):
        #return first i for which x<=args.threshold[i]. If no such i exists,
        #return len(args.threshold). This way, if the thresholds are 0,1,and 2,
        #the 0 will be x<=0, 1 is 0<x<=1, 2 is 1<x<=2, and 3 is x>2
        for i in range(nthres):
            if x<=args.threshold[i]:
                return i
        return len(args.threshold)
    #now build up the legend using the rules used for threshold(x)
    legend=dict()
    for i in range(nthres):
        if i==0:
            key = '<= '+str(args.threshold[0])
        else:
            key = '> '+str(args.threshold[i-1])+', <= '+str(args.threshold[i])
        legend[key]=i
    legend['> '+str(args.threshold[nthres-1])]=nthres
    ellipses_args['convert']='function'
    ellipses_args['function']=threshold
    ellipses_args['legend']=legend
#check for 3 cases: plotting 1 set of data, plotting both A and B probes for a
#single set of data, and plotting 2 different sets of data (specified using
#--other-data)
if args.probe !='AB' and args.other_data==None:
    drawer.draw_ellipses(**ellipses_args)
elif args.probe=='AB':
    ellipses_args['A_or_B']='A'
    drawer.draw_ellipses(**ellipses_args)
    if args.angle_file==None:
        ellipses_args['angle']=90
    ellipses_args['A_or_B']='B'
    ellipses_args['new_figure']=False
    ellipses_args['combine_colorbar']=True
    ellipses_args['cbar_label']=args.cbar_label
    if ellipses_args['title']==None:
        ellipses_args['title']=args.search_string+" of "+"A and B in "+args.file
    drawer.draw_ellipses(**ellipses_args)
elif args.other_data != None:
    drawer.draw_ellipses(**ellipses_args)
    ellipses_args['raw_data_file']=args.other_data[0]
    ellipses_args['search_string']=args.other_data[1]
    ellipses_args['A_or_B']=args.other_data[2]
    if args.angle_file==None:
        ellipses_args['angle']=90
    ellipses_args['combine_colorbar']=True
    ellipses_args['cbar_label']=args.search_string+"/"+args.other_data[1]
    ellipses_args['new_figure']=False
    drawer.draw_ellipses(**ellipses_args)

#ellipses_args is no longer equal to its original value! Should no longer be
#used

if args.save != None:
    plt.savefig(args.save)
else:
    plt.show()

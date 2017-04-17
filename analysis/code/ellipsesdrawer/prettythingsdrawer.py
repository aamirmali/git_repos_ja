import sys
import numpy as np
import matplotlib
from matplotlib import mpl
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from matplotlib.collections import EllipseCollection
from operator import itemgetter
from code.common import filehandler
from code.common import drawer

class PrettyThingsDrawer:
    map_file=None
    '''filename of file that maps MCE's rows/cols to pod-feed format'''
    beam_centers_file=None
    '''file indicating where beam centers are'''
    angle_file=None
    '''file indicating what each detector's angle is'''
    frequency=None
    '''frequency to search for in beam centers file'''
    beam_centers_Ax=np.array([])
    '''1D array of x coordinates of all probe A beam centers'''
    beam_centers_Ay=np.array([])
    '''1D array of y coordinates of all probe A beam centers'''
    beam_centers_Bx=np.array([])
    '''1D array of x coordinates of all probe B beam centers'''
    beam_centers_By=np.array([])
    '''1D array of y coordinates of all probe B beam centers'''
    curr_ellipses=None
    '''most recent ellipse collection drawn by TransDisplay'''

    def __init__(self,map_file='code/ellipsesdrawer/mce_pod_map.txt',
                 beam_centers_file='code/ellipsesdrawer/beamCenters.txt',
                 angle_file=None,
                 frequency=145):
        """Initializes class. map_file is the mapping between MCE's row-column
        format and the pod-feed format. beam_centers_file should contain the
        positions of the beam centers."""
        self.map_file=map_file
        self.frequency=frequency
        self.beam_centers_file=beam_centers_file
        self.angle_file=angle_file
        self.set_beam_centers()
    
    def modify_data(self,formatted_data,min_val=0,max_val=1,convert='nochange', 
                    function = 0):
        """Modifies data.  If convert is 'nochange', changes nothing.  If it is
        'normal', values higher than max_val changed to max_val; similarly for
        min_val.  If it's 'floor' or 'ceiling', all data either smaller than
        min_val or larger than max_val are changed to min_val or max_val,
        respectively.  If convert is 'function', the data will be changed
        according to function.  

        Returns the modified data."""
        if convert=='nochange': pass
        elif convert=='normal':
            for i in range(0,len(formatted_data)):
                if formatted_data[i]<min_val: formatted_data[i]=min_val
                if formatted_data[i]>max_val: formatted_data[i]=max_val
        elif convert=='floor':
            for i in range(0,len(formatted_data)):
                if formatted_data[i]<min_val or formatted_data[i]>max_val:
                    formatted_data[i]=min_val
        elif convert=='ceiling':
            for i in range(0,len(formatted_data)):
                if formatted_data[i]<min_val or formatted_data[i]>max_val:
                    formatted_data[i]=max_val
        elif convert =='function':
            try:
                for i in range(0, len(formatted_data)):
                    formatted_data[i]=function(formatted_data[i])
            except TypeError:
                print "Today is Friday, Friday. Partying, partying, yeah!"
                print "You must be drunk because your function is invalid."
                print "Data is not modified."
        else: print convert,"is an invalid convert string. Data will not be"\
                " restricted."
        return formatted_data


    def get_angles(self,A_or_B):
        """Returns angles in self.angle_file, of either probe A or B.  Assumes
        the file lists the detectors in order: pod #1 feed #1 first, pod #1
        feed #2 second, etc. Also assumes that the data starts on the second
        line, that tesA angle is in the 3rd column, and that tesB angle is in
        the 4th"""
        if A_or_B != 'A' and A_or_B != 'B':
            raise ValueError("A_or_B must be either A or B!")
        angles=[]
        with open(self.angle_file) as f:
            line=f.readline() #first line discarded
            line=f.readline()
            while line != "":
                split_line=line.split()
                if A_or_B=='A':
                    angles.append(float(split_line[2]))
                else:
                    angles.append(float(split_line[3]))
                line=f.readline()
        return angles


    def set_beam_centers(self):
        """Sets the class attributes. Should only be called by __init__."""
        with open(self.beam_centers_file) as f:
            line=f.readline() #first line discarded
            line=f.readline()
            Ax,Ay,Bx,By=[],[],[],[]
            while line != "":
                split_line=line.split()
                if int(split_line[2])==self.frequency:
                    #Ax is found in col 3 of file, Ay in col 4, etc.
                    Ax.append(float(split_line[3])) 
                    Ay.append(float(split_line[4]))
                    Bx.append(float(split_line[5]))
                    By.append(float(split_line[6]))
                line=f.readline()
        self.beam_centers_Ax=np.array(Ax)
        self.beam_centers_Ay=np.array(Ay)
        self.beam_centers_Bx=np.array(Bx)
        self.beam_centers_By=np.array(By)


    def TransDisplay(self, data, A_or_B,major_axis=20,
                     minor_axis=6, angle=None, cbar_label='', 
                     colorbar_lim=None, max_color_range=True, 
                     combine_colorbar=False):
        """This function creates a color plot of data, for probe A_or_B. The
        feed horns are represented using ellipses of size major_axis &
        minor_axis, rotated by angle.  If angle is None, uses self.angle_file;
        if that's also None, throws error. data must be a correctly organized
        array. The plot is drawn on succeeding figures. The graph is labeled
        title, and the colour bar is labeled cbar_label. colorbar_lim and
        max_color_range explained in draw_ellipses docs.  combine_colorbar is
        only relevant if multiple sets of ellipses are being plotted on the
        same figure. In that case, only 1 colorbar is shown if
        combine_colorbar=True, and one colorbar is shown for each set of data
        if it is False. Returns the EllipseCollection."""
        if A_or_B=='A':
            x=self.beam_centers_Ax
            y=self.beam_centers_Ay
        elif A_or_B=='B':
            x=self.beam_centers_Bx
            y=self.beam_centers_By
        else:
            print "I'm sorry that you do not understand that "+A_or_B
            +" is not A and is not B!"
            return
        major_axes=np.ones(len(x))*major_axis
        minor_axes=np.ones(len(x))*minor_axis
        if angle != None:
            angles=np.ones(len(x))*angle
          #  print angles
        else:
            angles=self.get_angles(A_or_B)
            if len(angles) != len(x):
                raise Exception("Angles file is invalid!")
        XY=np.hstack((x[:,np.newaxis],y[:,np.newaxis]))
        if combine_colorbar and self.curr_ellipses!=None: 
            plt.gcf().clear()
            ax=plt.subplot(1,1,1)
            #Make a new collection, containing all previous data plus new data
            old_majors=self.curr_ellipses._widths*2
            old_minors=self.curr_ellipses._heights*2
            #old_angles in radians, convert to degrees
            old_angles=self.curr_ellipses._angles*180/np.pi
            old_offsets=self.curr_ellipses._offsets
            old_data=self.curr_ellipses.get_array()
            combined_majors=np.hstack([old_majors,major_axes])
            combined_minors=np.hstack([old_minors,minor_axes])
            combined_angles=np.hstack([old_angles,angles])
            combined_data=np.hstack([old_data,data])
            combined_offsets=np.vstack([old_offsets,XY])
            new_ec=EllipseCollection(combined_majors,combined_minors,
                                     combined_angles,offsets=combined_offsets,
                                     transOffset=ax.transData)
            new_ec.set_array(combined_data)
            ec=new_ec
        else:
            ax=plt.subplot(1,1,1)
            ec=EllipseCollection(major_axes,minor_axes,angles, 
                             offsets=XY,
                             transOffset=ax.transData)        
            ec.set_array(data)

        self.curr_ellipses=ec
        ax.add_collection(ec)
        ax.autoscale_view()
        cbar=plt.colorbar(ec)
        if colorbar_lim !=None:
            cbar.set_clim(colorbar_lim)
            if max_color_range==True:
                norm=mpl.colors.Normalize(vmin=colorbar_lim[0],
                                          vmax=colorbar_lim[1])
                cbar=mpl.colorbar.ColorbarBase(cbar.ax,norm=norm)
        ec.color_bar=cbar
        cbar.set_label(cbar_label)
        return ec


    def set_legend(self,legend, collection, legend_name=None):
        """Sets the legend based on the colorbar. legend should be a dictionary
        mapping names to data values. collection is the ellipse collection
        containing the relevant colorbar.  legend_name is the title of the
        legend."""
        sorted_legend=sorted(legend.iteritems(),key=itemgetter(1),reverse=True)
        all_patches=[]
        all_keys=[]
        for i in range(0,len(sorted_legend)):
            all_keys.append(sorted_legend[i][0])
            val=sorted_legend[i][1]
            patch_color=collection.color_bar.to_rgba(val)
            if val< collection.color_bar.get_clim()[0]\
                    or val> collection.color_bar.get_clim()[1]:
                patch_color=(0,0,0,0)
            temp=matplotlib.patches.Patch(None,color=patch_color)
            all_patches.append(temp)
        leg=plt.figlegend(all_patches,all_keys,'upper right', title=legend_name)


    def set_title(self,raw_data_file, search_string, A_or_B, title=None, 
                  new_figure = True):
        """Draws a Title on the graph.  The title is set to title. If title is
        None and newfigure=True, sets title to search_string+ ' of ' + A_or_B +
        ' in ' + raw_data_file.  If title=None and newfigure=False, sets title
        to previous title plus newly generated title.  Returns None."""    
        if title==None:
            addtitle = search_string +' of ' + A_or_B +' in ' + raw_data_file
            if new_figure==True:
                plt.gcf().graph_title=addtitle
            elif new_figure==False:
                plt.gcf().graph_title=plt.gcf().graph_title+ " and " + addtitle
        else:
            plt.gcf().graph_title=title
        plt.title(plt.gcf().graph_title)


    def draw_ellipses(self,raw_data_file, search_string, A_or_B, 
                      major_axis=20, minor_axis=6, angle=None, 
                      min_val=0,max_val=1,convert='nochange', function = 0, 
                      title = None, fontsize=12,fontweight='normal',
                      cbar_label = None, new_figure=True, 
                      legend = None, legend_name = None, colorbar_lim=None, 
                      max_color_range=True,combine_colorbar=False, fig_num=1):
        """Draws ellipses for probe A_or_B.  Uses data from raw_data_file,
        searched for using search_string. Ellipses parameters given by
        major_axis, minor_axis, and angle (counterclockwise from horizontal).
        If angle is None, uses self.angle_file; if that's also None, throws
        error.  Data restricted according to convert, min_val, and max_val.
        The title of the graph is title (with properties fontsize and
        fontweight), while the label of the color bar is cbar_label. new_figure
        indicates whether a new figure should be created for plotting. A legend
        is made according to dictionary legend, with keys being names and
        values representing colors.  colorbar_lim sets range of numbers
        represented by colors.  If max_color_range is True, color bar
        represents entire possible range of colors; else, it represents range
        of colors in the data.  combine_colorbar is only relevant if multiple
        sets of data are being plotted on the same figure. In that case, 1
        colorbar is drawn if it is True, and a colorbar is drawn for each set
        of data if it is False. Returns None."""
        if angle==None and self.angle_file==None:
            raise ValueError("No angle or angle file specified!")
        if new_figure==False and len(plt.get_fignums())==0:
            print "You are stupid.  Here is a new figure anyways."
            print "new_figure is set to True."
            new_figure=True
        if cbar_label==None and combine_colorbar==False: 
            cbar_label=search_string
        elif cbar_label==None and combine_colorbar==True:
            #we can't make a reasonable colorbar label, so don't try
            cbar_label=""
        data_array=filehandler.IV_data_to_arr(raw_data_file,search_string)
        if len(data_array)==0:
            print "Yo homeboy! Your search_string returned no valid data!"
            print "You are so dumb. You are really dumb. For real."
            sys.exit(1)
        if A_or_B=='A':
            try:
                formatted_data=filehandler.data_to_pod_feed_fmt(
                    data_array,col_location=2,row_location=3,
                    map_file=self.map_file)
            except IndexError:
                print "Your search_string did not return enough valid data!"
                sys.exit(1)
        elif A_or_B=='B':
            try:
                formatted_data=filehandler.data_to_pod_feed_fmt(
                    data_array,col_location=2,row_location=4,
                    map_file=self.map_file)
            except IndexError:
                print "Your search_string did not return enough valid data!"
                sys.exit(1)
        else:
            raise ValueError("Probe should be either A or B!")
        modified_data=self.modify_data(formatted_data,min_val,max_val,
                                       convert,function)
#        plt.figure(fig_num)
        if new_figure:
            plt.figure()
            plt.gcf().graph_title=''
        ec=self.TransDisplay(modified_data,A_or_B,major_axis, 
                     minor_axis, angle, cbar_label, colorbar_lim, 
                             max_color_range, combine_colorbar)
        if legend!=None:
            self.set_legend(legend, ec, legend_name)
        self.set_title(raw_data_file, search_string, A_or_B, title, new_figure)
        drawer.set_size_weight(fontsize,fontweight)

    def draw_ellipses_data(self,two_d_data,data_name, A_or_B, 
                           major_axis=20, minor_axis=6, angle=0, 
                           min_val=0,max_val=1,convert='nochange',function = 0, 
                           title = None, cbar_label = None, new_figure=True, 
                           legend = None,legend_name = None,colorbar_lim=None, 
                           max_color_range=True,combine_colorbar=False, 
                           fig_num=1):
        """Draws ellipses for probe A_or_B.  Uses data from raw_data_file,
        searched for using search_string. Ellipses parameters given by
        major_axis, minor_axis, and angle (counterclockwise from horizontal).
        Data restricted according to convert, min_val, and max_val.  The title
        of the graph is title, while the label of the color bar is
        cbar_label. new_figure indicates whether a new figure should be created
        for plotting. A legend is made according to dictionary legend, with
        keys being names and values representing colors.  colorbar_lim sets
        range of numbers represented by colors.  If max_color_range is True,
        color bar represents entire possible range of colors; else, it
        represents range of colors in the data.  combine_colorbar is only
        relevant if multiple sets of data are being plotted on the same
        figure. In that case, 1 colorbar is drawn if it is True, and a colorbar
        is drawn for each set of data if it is False. Returns None."""
        if new_figure==False and len(plt.get_fignums())==0:
            print "You are stupid.  Here is a new figure anyways."
            print "new_figure is set to True."
            new_figure=True
        if cbar_label==None: 
            cbar_label=data_name+" for "+A_or_B
        if A_or_B=='A':
            formatted_data=filehandler.data_to_pod_feed_fmt(
                two_d_data,col_location=2,row_location=3,
                map_file=self.map_file)
        elif A_or_B=='B':
            formatted_data=filehandler.data_to_pod_feed_fmt(
                two_d_data,col_location=2,row_location=4,
                map_file=self.map_file)
        else:
            raise ValueError("Probe should be either A or B!")
        modified_data=self.modify_data(formatted_data,min_val,max_val,convert,
                                       function)
        if new_figure:
            plt.figure()
            plt.gcf().graph_title=''
            ec=self.TransDisplay(modified_data,A_or_B,major_axis, 
                             minor_axis, angle, cbar_label, colorbar_lim, 
                             max_color_range, combine_colorbar)
        if legend!=None:
            self.set_legend(legend, ec, legend_name)
        self.set_title('custom data', data_name, A_or_B, title, new_figure)

    
    def draw_hist(self,raw_data_file, search_string, A_or_B,
                  mapfile='mce_pod_map.txt',
                  min_val=0,max_val=1,convert='nochange', function=0,
                  bins=10,range=None,
                  title=None, xlabel=None, ylabel=None):
        '''Draws a histogram of the data from probe A_or_B.  The type of data
        is specified with search_string, and the data comes from the
        raw_data_file. The data is mapped to pod-feed format using mapfile.
        The data is restricted according to convert, min_val, and max_val. The
        data is placed into bins number of bins, and the graph shows a range of
        range.  The title of the histogram is title, while the x-axis and
        y-axis are labeled according to xlabel and ylabel. Returns None'''
        if title==None:
            title=search_string +' of ' + A_or_B +' in ' + raw_data_file
        if xlabel==None:
            xlabel=search_string
        if ylabel==None:
            ylabel="Number of probes"
        data_array=self.MCE_data_to_arr(raw_data_file,search_string)
        formatted_data=self.data_to_pod_feed_fmt(data_array,A_or_B,mapfile)
        modified_data=self.modify_data(formatted_data,min_val,max_val,convert,
                                       function)
        plt.figure()
        plt.hist(modified_data,bins,range)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

#end class


class fig:
    figure=None
    title=None
    collections=[]
    

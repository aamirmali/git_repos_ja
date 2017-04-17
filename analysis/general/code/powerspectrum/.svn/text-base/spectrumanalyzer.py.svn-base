import os
import math
import numpy as np
import matplotlib
from matplotlib import ticker
import matplotlib.pyplot as plt
from code.common import filehandler
import power_filter
from code.common import drawer

class SpectrumAnalyzer:
    """This class finds the power spectrum in real-world units and analyzes it.
    """
    data=None
    '''3D data from MCE'''
    nrows=None
    '''number of rows of data'''
    ncols=None
    '''number of cols of data'''
    valid_coors=None
    '''2D mask of coordinates that correspond to a detector in the map file'''
    filtgain=None
    '''filter gain'''
    dac_bits=None
    '''bit depth'''
    M_ratio=None
    Rfb=None
    sampling_freq=None
    responsivities=None
    '''2D array of responsivities of MCE detectors'''
    formatset=['b','g','r','c','m','y','k','b--','g--','r--',
               'c--','m--','y--','k--','b-+','g-+','r-+','c-+','m-+',
               'y-+','k-+','b-^','g-^','r-^']
    '''cycle of plot formats used by class'''
    pos_in_formatset=None
    '''position in formatset'''
    all_psds=None
    '''3D array containing PSD for every MCE coordinate'''
    dark_squids=None
    '''list of all dark squids.'''
    dark_detectors=None
    '''list of all dark detectors'''
    ramping_detectors=None
    '''list of all ramping detectors'''
    dark_squid_ref_freq=105
    '''deep magic. do not change.'''
    dark_squid_thres=6e-20
    '''deep magic.  do not change.'''
    dark_detector_peak_strength_thres=2
    '''threshold ratio of avg. PSD value at even multiples of noise_freq to
    avg. PSD value at odd multiples'''
    ramping_med_thres=1e-16
    '''ramping threshold'''
    noise_freq=4.8857
    '''fundamental frequency of the noise that is_dark_detector looks for'''
    is_col_invalid=None
    NFFT=None
    use_responsivities=False
    pow_response=None
    filter_params=None
    '''1D boolean array indicating which columns should be ignored'''
    def __init__ (self, data, filtgain=1218, dac_bits=14, M_ratio=8.5, 
                  Rfb=7084, sampling_freq=399., NFFT=256,
                  ivfile=None,
                  mapfile='mce_pod_map.txt', use_mapfile=True,
                  col_pos_in_file=2, row_pos_in_file=3, bad_cols=None,
                  subtract_mean=False,filter_params=None):
        """Initializes the object. datafile is the file containing the data,
        and will be read with mce_data. filtgain, dac_bits, M_ratio, and
        sampling_freq are parameters used to scale the power spectrum to units
        of A^2/Hz. If use_mapfile is True, the class will use mapfile to figure
        out which MCE coordinates have detectors, and ignore those that do
        not. col_pos_in_file and row_pos_in_file indicate the columns in
        mapfile in which MCE column and the first set of row data can be
        found. A second set of row data is assumed to exist in the column
        immediately to the right. Counting starts at 0, not 1. subtract_mean
        indicates whether the mean should be subtracted from the data. Note
        that this doesn't affect any PSD plot, and only affects timestream
        plots.  filter_params are the parameters of the integrated Butterworth
        filter, to be used to correct the power spectrum. It must be either
        None, in which case no correction is done, or a dictionary containing
        all of the following parameters: type, n_points, real_samp_freq, b11,
        b12, b21, b22, k1, k2. Refer to power_filter module for explanations of
        these parameters."""
        self.data=data
        self.nrows=self.data.shape[0]
        self.ncols=self.data.shape[1]
        if NFFT%2 != 0:
            raise ValueError("NFFT must be divisible by 2!")
        self.NFFT=NFFT
        self.filter_params=filter_params
        self.all_psds=[]
        self.dark_squids=[]
        self.dark_detectors=[]
        self.ramping_detectors=[]
        self.pos_in_formatset=0
        if self.filter_params!=None:
            args=self.filter_params #args to be passed to power_filter
            if 'type' not in args or 'real_samp_freq' not in args or \
                    'b11' not in args or 'b12' not in args or 'b21' \
                    not in args or 'b22' not in args or 'k1' \
                    not in args or 'k2' not in args:
                raise KeyError("filter parameters missing!")
            
            args['n_points']=NFFT/2 + 1
            args['eff_samp_freq']=sampling_freq
            self.pow_response=power_filter.get_pow_response(**args)
            
        if subtract_mean==True:
            for i in range(0,self.nrows):
                for j in range(0,self.ncols):
                    self.data[i][j] -= np.mean(self.data[i][j])
        self.filtgain=filtgain
        self.dac_bits=dac_bits
        self.M_ratio=M_ratio
        self.Rfb=Rfb
        self.sampling_freq=sampling_freq
        if use_mapfile:
            #initialize all to False
            self.valid_coors=np.zeros((self.nrows,self.ncols))>1
            self.build_valid_coordinates_array(mapfile,col_pos_in_file,
                                               row_pos_in_file)
        else:
            #initialize all to True
            self.valid_coors=np.ones((self.nrows,self.ncols))>0
        self.is_col_invalid=np.zeros(self.ncols)>1 #initialize all to False
        if bad_cols!=None:
            for col in bad_cols:
                self.is_col_invalid[col]=True
        if ivfile!=None:
            self.use_responsivities=True
            responsivities=filehandler.IV_data_to_arr(ivfile,"Responsivity")
            self.dark_squid_thres=math.sqrt(self.dark_squid_thres)
            self.dark_squid_thres *= 2**dac_bits*Rfb*M_ratio*1e-16
            self.ramping_med_thres=math.sqrt(self.ramping_med_thres)
            self.ramping_med_thres *=2**dac_bits*Rfb*M_ratio*1e-16
        else:
            self.use_responsivities=False
        for i in range(0,self.nrows): #initialize all PSDs
            row_psds=[]
            for j in range(0,self.ncols):
                psd=self.get_psd(self.data[i][j])
                if ivfile!=None:
                    watts_conver=2**dac_bits*Rfb*M_ratio*responsivities[i][j]
                    psd=np.sqrt(psd)*watts_conver
                row_psds.append(psd)
            self.all_psds.append(row_psds)
        self.all_psds=np.array(self.all_psds)

        self.dark_squids=self.get_dark_squids()
        self.dark_detectors=self.get_dark_detectors()
        self.ramping_detectors=self.get_ramping_detectors()

    def build_valid_coordinates_array(self,mapfile='mce_pod_map.txt',
                                      col_pos_in_file=2,row_pos_in_file=3):
        """Builds the array of valid detector positions. A detector exists at
        (row,col) iff self.valid_coors[row][col]==True. If mapfile cannot be
        found, all array elements are set to True. col_pos_in_file indicates
        the column of data in the file where the MCE col can be
        found. row_pos_in_file and row_pos_in_file+1 should indicate two file
        columns where MCE row data can be found. Returns None."""
        
        probe_A_map=filehandler.get_correspondance(row_pos_in_file,
                                                   col_pos_in_file,mapfile)
        probe_B_map=filehandler.get_correspondance(row_pos_in_file,
                                                   col_pos_in_file,mapfile)

        for i in range(0,len(probe_A_map)):
            rowA=probe_A_map[i][0]
            colA=probe_A_map[i][1]
            rowB=probe_B_map[i][0]
            colB=probe_B_map[i][1]
            self.valid_coors[rowA][colA]=True
            self.valid_coors[rowB][colB]=True

    def get_psd(self,relevant_data):
        """Returns the power spectrum of relevant_data in units of A^2/Hz."""
        conversion=1./self.filtgain/2**self.dac_bits*(1./50)/(1./self.Rfb+1./50)/(self.M_ratio*self.Rfb)
        relevant_data=relevant_data*conversion
        relevant_data -= np.mean(relevant_data)
        psd=matplotlib.mlab.psd(relevant_data,Fs=self.sampling_freq,
                                scale_by_freq=True,NFFT=self.NFFT)[0]
        if self.pow_response!=None:
            psd=psd/self.pow_response
        return psd
    
    def get_psd_for_detector(self,row=None,col=None,verbose=True):
        """Gets the PSD for detector(s). If only a row or a column is
        specified, print out all the valid PSD for detectors in the
        whole row or column. If both a row and a column is specified,
        print out the PSD for the detector in that row and that
        column. Returns an array of the PSDs and an array of their
        corresponding locations."""
        sel_psds=[]
        sel_loc=[]

        if row!=None and col!=None:
            if (self.valid_coors[row][col]==True and
                self.is_col_invalid[col]==False):
                if np.std(self.data[row][col])==0 and verbose:
                    print "no data for row",row,"col",col
                psd=self.all_psds[row][col]
                sel_psds.append(psd)
                sel_loc.append([row, col])
            elif verbose:
                print "There's no detector at row " + row + "and col " 
                + col + "."
        elif row!=None and col==None:
            for col in range(0,self.ncols):
                if self.valid_coors[row][col]==True \
                        and self.is_col_invalid[col]==False:
                    if np.std(self.data[row][col])==0 and verbose:
                        print "no data for row",row,"col",col
                    psd=self.all_psds[row][col]
                    sel_psds.append(psd)
                    sel_loc.append([row, col])
        elif col!=None and row==None:
            for row in range(0,self.nrows):
                if self.valid_coors[row][col]==True \
                        and self.is_col_invalid[col]==False:
                    if np.std(self.data[row][col])==0 and verbose:
                        print "no data for row",row,"col",col
                    psd=self.all_psds[row][col]
                    sel_psds.append(psd)
                    sel_loc.append([row, col])
        elif verbose:
            print 'Currently returning data for no row and no columns.' 
            print 'Very, very smart.'
        return np.array(sel_psds), np.array(sel_loc)
    

    def plot_timestream(self,sel_psds,sel_loc,new_figure=True,title=None,
                        n_legend_cols=1,fontsize=12,fontweight='normal',
                        hide_legend=False):
        """Plots the data directly. See docs for get_psd_for_detector for
        explanation of variable names. If newfigure is true, creates a new
        figure before plotting; otherwise, uses current figure.  fontsize and
        fontweight affect all text.  hide_legend is whether to make the legend
        invisible"""
        num_plots=0
        if new_figure: 
            self.new_fig()
        for i in range(0,sel_psds.shape[0]):
            if np.std(sel_psds[i])!=0:
                num_plots+=1
                row=sel_loc[i][0]
                col=sel_loc[i][1]
                label='r'+str(row)+'c'+str(col)
                format=self.formatset[self.pos_in_formatset]
                self.pos_in_formatset+=1
                self.pos_in_formatset %= len(self.formatset)
                plt.plot(self.data[row][col],format,label=label)                
        if num_plots!=0: 
            legend=plt.legend(ncol=n_legend_cols)
            legend.get_frame().set_visible(False)
        if title!=None:
            plt.title(title)
        else:
            plt.title("Time streams of "+str(num_plots)+" data set(s)")
        drawer.set_size_weight(fontsize,fontweight)
        if hide_legend:
            legend.set_visible(False)


    def plot_result(self,row=None,col=None,plot_format='loglog',
                    plot_psds=True,plot_timestream=False,new_figure=True,
                    title=None,timestream_title=None,legend_label_suffix='',
                    psd_min=None,psd_max=None,verbose=True,n_legend_cols=1,
                    fontsize=12,fontweight='normal',plot_grid=False,
                    hide_legend=False):
        """Plots all PSDs requested by user. See docs for get_psd_for_detector
        for more info. If row=None and col=None, makes a waterfall plot of PSDs
        of all detectors, then returns.  plot_format can be loglog, semilogx,
        semilogy, or linear, and indicates the type of plot to
        make. plot_timestream indicates whether a corresponding timestream
        should be plotted. new_figure indicates whether a new figure should be
        made before plotting. title is the title (likewise for
        timestream_title), and legend_label_suffix is the suffix appended to
        all legend labels. psd_min and psd_max are the y axis limits for the
        power spectrum plot. If a waterfall plot is plotted instead, values
        that fall outside these limits are not plotted. n_legend_cols is the
        number of columns the legend should have. fontsize and fontweight
        affect titles, tick labels, and axes labels. plot_grid is whether to
        plot a meshgrid. hide_legend is whether to hide the legend."""
        plt.grid(plot_grid)
        if row==None and col==None:
            #plot waterfall, but verify parameters first
            if plot_timestream or plot_psds==False:
                print "plot_result can only plot waterfall when row=None and"\
                    " col=None!"
            self.plot_waterfall(format=plot_format,psd_min=psd_min,
                                psd_max=psd_max,domination='row')
            return
        psds_and_locs=self.get_psd_for_detector(row,col,verbose)
        psds=psds_and_locs[0]
        if len(psds)==0:
            if verbose:
                print "You have no data for row",row,"col",col
            return
        locs=psds_and_locs[1]
        num_data_sets=0
        if plot_timestream==True and plot_psds==True:
            self.plot_timestream(psds,locs,True,title=timestream_title,
                                 n_legend_cols=n_legend_cols,fontsize=fontsize,
                                 fontweight=fontweight,hide_legend=hide_legend)
            self.new_fig()
        if plot_timestream==True and plot_psds==False:
            self.plot_timestream(psds,locs,new_figure,title=timestream_title,
                                 n_legend_cols=n_legend_cols,fontsize=fontsize,
                                 fontweight=fontweight,hide_legend=hide_legend)
            return
        if plot_timestream==False and plot_psds==True:
            if new_figure==True:
                self.new_fig()
        if plot_timestream==False and plot_psds==False:
            return
        x=np.linspace(0,self.sampling_freq/2,len(psds[0]))
        for i in range(0,len(psds)):
            if np.std(psds[i])==0: 
                continue
            num_data_sets+=1   
            label='r'+str(locs[i][0])+'c'+str(locs[i][1])+legend_label_suffix
            format=self.formatset[self.pos_in_formatset]
            self.pos_in_formatset+=1
            self.pos_in_formatset %= len(self.formatset)
            if plot_format=='loglog':
                plt.loglog(x,psds[i],format,label=label)
            elif plot_format=='semilogx':
                plt.semilogx(x,psds[i],format,label=label)
            elif plot_format=='semilogy':
                plt.semilogy(x,psds[i],format,label=label)
            else:
                plt.plot(x,psds[i],format,label=label)
        if num_data_sets!=0: 
            legend=plt.legend(ncol=n_legend_cols)
            legend.get_frame().set_visible(False)
        plt.xlabel("Frequency (Hz)")
        if self.use_responsivities==True:
            plt.ylabel("Power (W/rtHz)")
        else:
            plt.ylabel("Power (A^2/Hz)")
        if title==None:
            plt.title("Power spectrum of "+str(num_data_sets)+" data set(s)")
        else:
            plt.title(title)
        (xmin,xmax,ymin,ymax)=plt.axis()
        if psd_min!=None:
            ymin=psd_min
        if psd_max!=None:
            ymax=psd_max
        plt.axis([xmin,xmax,ymin,ymax])
        drawer.set_size_weight(fontsize,fontweight)
        if hide_legend:
            legend.set_visible(False)
        
    def plot_waterfall(self,freq_divisions=20,domination='col',
                       axis_divisions=1,plot_format='semilogy',limit=None,
                       colorbar=True,custom_label=None,psd_min=None,
                       psd_max=None,fontsize=12,fontweight='normal',
                       plot_grid=False, hide_legend=False):
        """Makes a waterfall plot of all PSDs. freq_divisions is the number of
        ticks that the frequency axis should be labelled with. domination
        should be either 'col' or 'row', and indicates whether the plot should
        be based on rows or columns. axis_divisions indicates one label every
        axis_divisions*self.nrows or axis_divisions*self.ncols detectors,
        depending on domination.  likewise, with the other axis. plot_format
        should be 'linear' or 'semilogy', and indicates whether the log of the
        PSD values should be taken before plotting. limit is an array-like
        object of length 2 that contains the lower and upper color
        limits. colorbar is whether a colorbar should be shown, and
        custom_label is a custom colorbar label to be used. Be default, it's
        set to W/rtHz, A^2/Hz, log W/rtHz, or log A^2/Hz, depending on
        self.use_responsivities and plot_format.  fontsize and fontweight
        affect titles, tick labels, and axes labels. plot_grid is whether to
        plot a meshgrid.  Note that a meshgrid is usually not very visible
        against the bright colors of the waterfall plot."""
        plt.grid(plot_grid)
        if plot_format!='semilogy' and plot_format!='linear':
            assert(False)
        if domination!='row' and domination!='col':
            assert(False)
            
        to_be_plotted=[]
        #copy valid cols of self.all_psds to to_be_plotted
        transposed_psds = self.all_psds.transpose((1,0,2))
        col_map = [] #col_map[graph_col] = actual col
        for col in range(self.ncols):
            if self.is_col_invalid[col]==False:
                to_be_plotted.append(transposed_psds[col])
                col_map.append(col)
        to_be_plotted=np.array(to_be_plotted)
        n_valid_cols=len(to_be_plotted)
        if domination=='row':
            to_be_plotted.transpose((1,0,2))
        new_shape=(self.nrows*n_valid_cols,self.all_psds.shape[2])
        to_be_plotted=to_be_plotted.reshape(new_shape)
        #Set invalid values to nan. If format is semilogy, take log.
        for i in range(len(to_be_plotted.flat)):
            val=to_be_plotted.flat[i]
            if val>0 and plot_format=='semilogy':
                to_be_plotted.flat[i]=np.log10(val)
            if val<=0:
                to_be_plotted.flat[i]=np.nan
            if psd_min!=None and val<psd_min:
                to_be_plotted.flat[i]=np.nan
            if psd_max!=None and val>psd_max:
                to_be_plotted.flat[i]=np.nan
        ax=plt.subplot(111)
        convert=self.sampling_freq/2./(to_be_plotted.shape[1]-1)
        def det_format_func(x,i):
            if domination=='col':
                graph_col=int(x/self.nrows)
                return col_map[graph_col]
            if domination=='row':
                return int(x/n_valid_cols)
        def freq_format_func(pos,i):
            return int(pos*convert)
        detformatter=ticker.FuncFormatter(det_format_func)
        freqformatter=ticker.FuncFormatter(freq_format_func)
        ax.xaxis.set_major_formatter(freqformatter)
        ax.yaxis.set_major_formatter(detformatter)
        freq_interval=math.ceil(float(self.sampling_freq)/freq_divisions)
        ax.xaxis.set_major_locator(ticker.
                                   MultipleLocator(freq_interval/convert))
        if domination=='col':
            det_interval=self.nrows*axis_divisions
            plt.ylabel('Column',fontweight=fontweight,fontsize=fontsize)
        else:
            det_interval=n_valid_cols*axis_divisions
            plt.ylabel('Row',fontsize=fontsize,fontweight=fontweight)
        ax.yaxis.set_major_locator(ticker.MultipleLocator(det_interval))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(1))
        plt.xlabel('Frequency (Hz)',fontsize=fontsize,fontweight=fontweight)
        plt.title("PSDs of all valid detectors",fontsize=fontsize,
                  fontweight=fontweight)
        image=plt.imshow(to_be_plotted,interpolation='nearest')
        if limit!=None:
            image.set_clim(limit[0],limit[1])
        if colorbar==True:
            cbar=plt.colorbar()
            label=''
            if custom_label==None:
                if plot_format=='linear':
                    prefix=''
                elif plot_format=='semilogy':
                    prefix='log '
                if self.use_responsivities:
                    suffix='W/rtHz'
                else:
                    suffix='A^2/Hz'
                label=prefix+suffix
            else:
                label=custom_label
            cbar.set_label(label)
        drawer.set_size_weight(fontsize,fontweight)

    def print_psd_level(self,row=None,col=None,ref_freq=10):
        """If both row and col are specified, prints out the average of 3
        datapoints around ref_freq. If row is specified but col is None, finds
        the average around ref_freq (in Hz) for each element in the row, prints
        it out, and prints out the median at the end. Analogous behavior if col
        is specified but row is None."""
        if row!=None and col!=None:
            noise_level=self.get_strength_near_freq(self.all_psds[row][col],
                                                    ref_freq)
            print "r"+str(row)+"c"+str(col)+" "+str(noise_level)
        if row==None and col!=None:
            all_noise_levels=[]
            for row in range(0,self.nrows):
                noise_level=self.get_strength_near_freq(self.all_psds[row][col],
                                                        ref_freq)
                print "r"+str(row)+"c"+str(col)+" "+str(noise_level)
                all_noise_levels.append(noise_level)
            med_noise=np.median(all_noise_levels)
            print "Median noise level for col",col,":",med_noise
        if row!=None and col==None:
            all_noise_levels=[]
            for col in range(0,self.ncols):
                noise_level=self.get_strength_near_freq(self.all_psds[row][col],
                                                        ref_freq)
                print "r"+str(row)+"c"+str(col)+" "+str(noise_level)
                all_noise_levels.append(noise_level)
            med_noise=np.median(all_noise_levels)
            print "Median noise level for row",row,":",med_noise

    def plot_custom_psds(psds, plot_format=''):
        """Plots a custom psds.  plot_format can be loglog, semilogx, semilogy,
        or linear. and indicates how the axes are plotted. Please, for the sake
        of God, do not ever use this method."""
        num_data_sets=0
        #Plot psds[i] for each valid i on the same figure
        x=np.linspace(0,self.sampling_freq/2,len(psds[0]))
        for psd in psds:
            num_data_sets+=1
            if plot_format=='loglog':
                plt.loglog(x,psd)
            elif plot_format=='semilogx':
                plt.semilogx(x,psd)
            elif plot_format=='semilogy':
                plt.semilogy(x,psd)
            else:
                plt.plot(x,psds)
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Power (A^2/Hz)")
        plt.title("Power spectrum of "+str(num_data_sets)+" data set(s)")

    def get_strength_near_freq(self,psd,freq,window_halfsize=1):
        """Returns the average value of psd around frequency freq (in Hz),
        using window_halfsize*2+1 datapoints."""
        points_per_hz=(len(psd)-1)/(self.sampling_freq/2.)
        index=points_per_hz*freq
        return np.mean(psd[index-window_halfsize:index+window_halfsize+1])

    def get_avg_strength(self,psd,freq,halfsize=2):
        """Same thing as get_strength_near_freq, but halfsize is in Hz, not
        in number of points. Throws ValueError if the halfsize is not big
        enough to incorporate at least 1 data point, or if halfsize is big
        enough to require inclusion of a datapoint that's out of bounds."""
        points_per_hz=(len(psd)-1)/(self.sampling_freq/2.)
        half_npoints=halfsize*points_per_hz
        index_at_freq=freq*points_per_hz
        index_low_freq=index_at_freq - half_npoints
        index_high_freq=index_at_freq + half_npoints
        #check whether boundary is big enough to include at least 1 point
        if int(index_low_freq)==int(index_at_freq)==int(index_high_freq):
            raise ValueError("Boundaries don't include any points!")
        #convert lower and upper bounds to integers
        lower=int(round(index_low_freq))
        upper=int(round(index_high_freq))
        if lower < 0 or upper >= len(psd):
            raise IndexError("Window halfsize too high!")
        return np.mean(psd[lower:upper+1])

    def get_all_avg_strength(self,freq,halfsize=2):
        """Calls get_avg_strength on every detector and returns the result as an
        array."""
        results=np.empty((self.nrows,self.ncols))
        for row in range(self.nrows):
            for col in range(self.ncols):
                results[row][col]=self.get_avg_strength(
                self.all_psds[row][col],freq,halfsize)
        return results

    def get_specs(self,condition,row=None,col=None):
        """Returns list of all special detectors in the appropriate row and/or
        col. condition is a function that returns True if a PSD is special and
        False otherwise."""
        all_specs=[]
        if row!=None and col!=None:
            if self.is_col_invalid[col]==False \
                    and condition(self.all_psds[row][col]):
                all_specs.append((row,col))
        if row==None and col!=None:
            for row in range(0,self.nrows):
                if self.is_col_invalid[col]==False \
                        and condition(self.all_psds[row][col]):
                    all_specs.append((row,col))
        if col==None and row!=None:
            for col in range(0,self.ncols):
                if self.is_col_invalid[col]==False \
                        and condition(self.all_psds[row][col]):
                    all_specs.append((row,col))
        if col==None and row==None:
            for row in range(0,self.nrows):
                for col in range(0,self.ncols):
                    if self.is_col_invalid[col]==False \
                            and condition(self.all_psds[row][col]):
                        all_specs.append((row,col))
        return all_specs        

    def print_specs(self,to_print,label=''):
        """Prints out label, followed by the content of to_print by column.
        to_print must be a list of tuples of length 2, in the form (row,col).
        Most often used to print out dark and ramping detectors, and dark
        squids."""
        print label
        dets_by_col=[]
        for i in range(self.ncols):
            dets_by_col.append([])
        for det in to_print:
            row=det[0]
            col=det[1]
            dets_by_col[col].append(row)
        for i in range(self.ncols):
            print "col",i,dets_by_col[i]
        
#Deep magic begins here...
    def is_dark_detector(self,psd):
        #conversion from frequency to array index
        nyquist=self.sampling_freq/2.
        conversion=float(len(psd)-1)/nyquist
        ref_vals=[]
        peak_vals=[]
        half_freq=self.noise_freq/2.
        max_multiple=math.ceil(nyquist/half_freq)
        max_multiple=int(max_multiple)
        for i in range(1,max_multiple):
            pos=round(half_freq*i*conversion)
            pos=int(pos)
            if pos>=len(psd):
                break
            if i%2==0:
                peak_vals.append(psd[pos])
            else:
                ref_vals.append(psd[pos])
        ratios=[]
        for i in range(len(peak_vals)):
            if i>=len(ref_vals):
                break
            ratios.append(peak_vals[i]/ref_vals[i])
        if np.mean(ratios)<self.dark_detector_peak_strength_thres and\
                self.is_dark_squid(psd)==False:
            return True
        return False

    def is_dark_squid(self,psd):
        """Returns True if psd represents a dark squid, and False
        otherwise. Uses self.dark_squid_ref_freq and self.dark_squid_thres to
        make this determination."""
        #if the data is 0, it's not a dark squid
        if np.std(psd)==0: 
            return False
        strength=self.get_strength_near_freq(psd,self.dark_squid_ref_freq)
        if strength<self.dark_squid_thres: 
            return True
        else: 
            return False
    
    def is_ramping_detector(self,psd):
        """Returns True if psd represents a ramping detector, and False
        otherwise. Uses self.ramping_med_thres to determine this."""
        if np.median(psd)>self.ramping_med_thres:
            return True
        else:
            return False
    
    def get_dark_squids(self,row=None,col=None):
        """Returns all dark squids, as specified by row, col, and tested by
        self.is_dark_squid()"""
        return self.get_specs(self.is_dark_squid,row=row,col=col)

    def get_dark_detectors(self,row=None,col=None):
        """Returns all dark detectors, as specified by row, col, and tested by
        self.is_dark_detector()"""
        return self.get_specs(self.is_dark_detector,row=row,col=col)

    def get_ramping_detectors(self,row=None, col=None):
        """Returns all ramping detectors, as specified by row, col, and tested
        by self.is_ramping_detector()"""
        return self.get_specs(self.is_ramping_detector, row=row, col=col)

    def plot_spec_hist(self,what_to_plot=None,criterion='median',bins=20):
        """Plots a histogram of special PSDs. what_to_plot should be either
        'squids' or 'dark detectors'. criterion can be 'median', to plot a
        histogram of the median value of the special PSDs, or '10hz', to use
        10Hz as a reference frequency, or '100hz'."""
        self.new_fig()
        all_noise_levels=[]
        if what_to_plot=='squids':
            to_be_plotted=self.dark_squids
        elif what_to_plot=='dark detectors': 
            to_be_plotted = self.dark_detectors
        print "Printing all " + what_to_plot
        for element in to_be_plotted:
            row=element[0]
            col=element[1]
            psd=self.all_psds[row][col]
            noise_level=None
            if criterion=='median':
                noise_level=np.median(psd)
            elif criterion=='10hz':
                ref_freq=10
                noise_level=self.get_strength_near_freq(psd,ref_freq,
                                                        window_halfsize=2)
            elif criterion=='100hz':
                ref_freq=100
                noise_level=self.get_strength_near_freq(psd,ref_freq,
                                                        window_halfsize=2)
            else:
                print "Invalid parameter 'criterion' for plot_spec_hist"
                return
            print "r"+str(row)+"c"+str(col)+": "+str(noise_level)
            all_noise_levels.append(noise_level)
        plt.hist(all_noise_levels,bins=bins)
        plt.xlabel(what_to_plot+" noise level")
        plt.title("Distribution of "+what_to_plot+" noise level")

    def plot_spec_psd(self,what_to_plot=None,plot_format='loglog'):
        """Plots special PSDs. what_to_plot is either 'squids' or 
        'dark detectors'. plot_format is either 'loglog', 'semilogx', 
        'semilogy', or 'linear'."""
        if what_to_plot=='squids':
            to_be_plotted=self.dark_squids
        elif what_to_plot=='dark detectors':
            to_be_plotted=self.dark_detectors
        else:
            print "Invalid parameter what_to_plot for plot_spec_psd"
            return
        num_points=len(to_be_plotted)
        for element in to_be_plotted:
            row=element[0]
            col=element[1]
            self.plot_result(row=row,col=col,
                             title='PSDs of '+str(num_points)+' '+what_to_plot,
                             plot_format=plot_format)
        
    def new_fig(self):
        """Draws a new figure. User should always call this, not plt.figure(),
        to create a new figure."""
        plt.figure()
        self.pos_in_formatset=0

    def show(self,save_dir=None):
        """Shows the plot. This is used to handle the error caused by user
        calling pyplot.show() without plotting anything first. Returns None."""
        if len(plt.get_fignums())==0:
            print "You haven't plotted anything yet! Not showing."
            return
        if save_dir==None:
            plt.show()
        else:
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            fig_nums=plt.get_fignums()
            for num in fig_nums:
                plt.figure(num)
                save_file=os.path.join(save_dir,'graph'+str(num)+'.png')
                plt.savefig(save_file)

#End class


import os
import matplotlib.pyplot as plt
import matplotlib.mlab
import numpy as np
class CommonPlotter:
    data=None #data converted to real-world units
    ncols=None
    nrows=None
    col_commons=None #common mode plots for every col
    n_invalid=None #number of invalid rows for every col
    common_all=None #common mode for all data
    n_invalid_all=None #number of invalid detectors for all data
    include_col=None #for every col, indicates whether col is to be considered
    normalize=None #whether to normalize before calculating common mode
    formatset=['b','g','r','c','m','y','k','b--','g--','r--',
               'c--','m--','y--','k--','b-+','g-+','r-+','c-+','m-+',
               'y-+','k-+','b-^','g-^','r-^']
    pos_in_formatset=None
    
    def __init__(self,data,include_col,normalize):
        """data must be a 3D array already converted to Amperes. include_col
        should be an array-like object with length equal to the number of
        columns in data, where each element is True if the column is to be
        included and False otherwise. normalize indicates whether the data
        should be normalized before adding to get the common mode."""
        self.data=data
        self.nrows=data.shape[0]
        self.ncols=data.shape[1]
        self.include_col=include_col
        self.normalize=normalize
        self.pos_in_formatset=0
        self.col_commons=[]
        self.n_invalid=[]
        for col in range(self.ncols):
            #initialize self.col_commons and self.n_invalids. Initialize to
            #None if the include_col[col]==False
            if include_col[col]:
                (common,n_invalid)=self.find_common(data[:,col])
                self.col_commons.append(common)
                self.n_invalid.append(n_invalid)
            else:
                self.col_commons.append(None)
                self.n_invalid.append(None)
        #find common for all data
        all_data=[]
        for row in range(self.nrows):
            for col in range(self.ncols):
                if include_col[col]:
                    all_data.append(data[row][col])
        if len(all_data)==0:
            raise ValueError("no data specified!")
        (self.common_all,self.n_invalid_all)=self.find_common(all_data)

    def find_common(self,set_of_data):
        #Returns (common,n_invalid), where common is the common mode of
        #set_of_data, and n_invalid is the number of zero elements. If all
        #elements are zero, returns (None,None) instead. The common mode is
        #defined as the sum of all non-zero elements in set_of_data, either 
        #normalized or not depending on self.normalize, divided by the number
        #of summed elements.
        common=np.zeros(len(set_of_data[0]))
        n_invalid=0
        for element in set_of_data:
            element -= np.mean(element)
            norm=np.sqrt(np.dot(element,element))
            if norm==0:
                n_invalid += 1
            else:
                if self.normalize:
                    element /= norm
                common += element
        if n_invalid==len(set_of_data):
            return (None,None)
        #if not normalized, divide by length of data to get right units; if
        #normalized, units are meaningless anyways, so we might as well divide
        #by the length of data
        common /= (len(set_of_data) - n_invalid)
        return (common,n_invalid)
    
    
    def plot_data(self,to_be_plotted,x_axis='default',plot_format='linear',
                  save_dir=None,xlabel='',ylabel='',
                  overplot=True,title_prefix='',filename_prefix=''):
        #plots to_be_plotted for each column for which a common mode was
        #found. Saves to save_dir if it isn't None, and plots each column on
        #separate figures if overplot is False. to_be_plotted must be a 2D
        #array with its first dimension's length equal to self.ncols. x_axis
        #is the x-axis to be used in plotting; this must be an array with the
        #same length as the data, or 'default' for the default axis.
        #The title is set to title_prefix+' col'+str(col)+', '
        #+str(self.n_invalid[col])+" rows off") if overplot is False, or
        #title_prefix+' for all specified cols' if it is True. The save files
        #are filename_prefix+"_col"+str(col)+".png" if overplot is False,
        #or filename_prefix+"_overplotted_cols.png" if it is True.
        
        #if we're not overplotting, we need to create a new figure if and only
        #if this is not the first column we're plotting. first_entry keeps
        #track of this
        first_entry=True 
        for col in range(self.ncols):
            if self.col_commons[col] != None:
                if x_axis=='default':
                    x_axis=range(len(to_be_plotted[col]))
                if overplot==False and first_entry==False:
                    self.new_fig()
                first_entry=False
                format=self.formatset[self.pos_in_formatset]
                self.pos_in_formatset += 1
                if self.pos_in_formatset==len(self.formatset):
                    self.pos_in_formatset=0
                label='c'+str(col)
                if plot_format=='linear':
                    plt.plot(x_axis,to_be_plotted[col],format,label=label)
                elif plot_format=='semilogx':
                    plt.semilogx(x_axis,to_be_plotted[col],format,label=label)
                elif plot_format=='semilogy':
                    plt.semilogy(x_axis,to_be_plotted[col],format,label=label)
                elif plot_format=='loglog':
                    plt.loglog(x_axis,to_be_plotted[col],format,label=label)
                else:
                    raise ValueError("Invalid plot format!")
                if overplot==False:
                    plt.title(title_prefix+' col'+str(col)+', '
                              +str(self.n_invalid[col])+" rows off")
                    plt.xlabel(xlabel)
                    plt.ylabel(ylabel)
                if overplot==False and save_dir!=None:
                    filename=filename_prefix+'_col'+str(col)+'.png'
                    save_file=os.path.join(save_dir,filename)
                    plt.savefig(save_file)
            elif self.col_commons[col]==None and self.include_col[col]:
                print "No non-zero rows for col",col
        if overplot==True:
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.title(title_prefix+' for all specified cols')
            plt.legend()
            if save_dir!=None:
                filename=filename_prefix+'_overplotted_cols.png'
                save_file=os.path.join(save_dir,filename)
                plt.savefig(save_file)


    def plot_psds(self,NFFT=1024,sampling_freq=399.,plot_format='semilogy',
                  save_dir=None,overplot=True):
        """Plots the PSDs of common modes of all valid columns using the
        specified parameters.  Saves to save_dir/psd_col0.png,
        save_dir/psd_col1.png, etc if save_dir isn't None; otherwise, doesn't
        save. Plots all columns on one figure if overplot is True, and plots on
        different figures if it's False. Units are arbitrary (and labelled as
        such) if self.normalize is True, and A^2/Hz if it's False. plot_format
        can be linear, semilogx, semilogy, or loglog."""
        all_psds=[]
        x_axis=None
        for col in range(self.ncols):
            if self.col_commons[col] != None:
                (psd,freqs)=matplotlib.mlab.psd(
                    self.col_commons[col],Fs=sampling_freq,scale_by_freq=True,
                    NFFT=NFFT)
                x_axis=freqs
                all_psds.append(psd)
            else:
                all_psds.append(None)
        if self.normalize:
            ylabel='Arbitrary units'
        else:
            ylabel='A^2/Hz'
        self.plot_data(all_psds,x_axis=x_axis,plot_format=plot_format,
                       title_prefix='Common mode PSD for',save_dir=save_dir,
                       overplot=overplot,xlabel='Frequency (Hz)',
                       ylabel=ylabel,filename_prefix='psd')

    def plot_timestreams(self,save_dir=None,overplot=False):
        """Plots the timestreams of common modes of all valid columns using
        the specified parameters. Saves to save_dir/time_col0.png,
        save_dir/time_col1.png, etc. if save_dir isn't None; otherwise, doesn't
        save. Plots all columns on one figure if overplot is True, and plots on
        different figures if it's False."""
        if self.normalize:
            ylabel='Arbitrary units'
        else:
            ylabel='Amperes'
        self.plot_data(self.col_commons,save_dir=save_dir,overplot=overplot,
                       title_prefix='Common mode timestream for',
                       filename_prefix='time',ylabel=ylabel)

    def plot_timestream_all(self,save_dir=None):
        """Plots the timestream of the common mode of all non-zero data.
        Saves to save_dir/time_common_all.png if save_dir is not None."""
        if self.normalize:
            ylabel='Arbitrary units'
        else:
            ylabel='Amperes'
        plt.plot(self.common_all)
        plt.title("Common mode timestream of all data, "
                  +str(self.n_invalid_all)+" detectors off")
        plt.ylabel(ylabel)
        if save_dir!=None:
            save_file=os.path.join(save_dir,'time_common_all.png')
            plt.savefig(save_file)
            

    def plot_psd_all(self,save_dir=None,sampling_freq=399.,NFFT=1024,
                     plot_format='linear'):
        """Plots the PSD of the common mode of all non-zero data. Saves to
        save_dir/psd_common_all.png if save_dir is not None. plot_format can
        be linear, semilogx, semilogy, or loglog."""
        (psd,freqs)=matplotlib.mlab.psd(
                    self.common_all,Fs=sampling_freq,scale_by_freq=True,
                    NFFT=NFFT)
        if plot_format=='linear':
            plt.plot(freqs,psd)
        elif plot_format=='semilogx':
            plt.semilogx(freqs,psd)
        elif plot_format=='semilogy':
            plt.semilogy(freqs,psd)
        elif plot_format=='loglog':
            plt.loglog(freqs,psd)
        else:
            raise ValueError("Invalid plot format!")
        plt.title("Common mode PSD of all data")
        if self.normalize:
            ylabel='Arbitrary units'
        else:
            ylabel='A^2/Hz'
        plt.ylabel(ylabel)
        if save_dir!=None:
            save_file=os.path.join(save_dir,'psd_common_all.png')
            plt.savefig(save_file)
        
        
    def new_fig(self):
        """Code should call this function instead of pyplot's figure(). This
        function resets the position in the object's format set to 0, meaning
        the format cycle starts from the beginning for each figure."""
        self.pos_in_formatset=0
        plt.figure()
    
    def show(self):
        """Convenience function, so that external code doesn't need to import
        matplotlib."""
        plt.show()

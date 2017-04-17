import sys
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import code.common.functionanalyzer as fa
import code.common.arrayfunctions as arf

class DipAnalyzer:
    '''Analyzes dips in data. Especially useful for finding dip width.
    @warning:prints offensive things if used inappropriately.
    
    @ivar data: the data to be analyzed. 
    @type data: numpy array/list, shape:(*)
    @ivar bound_ref: indicates whether dip boundaries should be detected based
    on nearest relative maximum, or the average between dips. Valid choices:
    'max', 'average'
    @type bound_ref: str
    @ivar bound_thres_ratio: Once the function rise toward bound_ref by this
    ratio, the boundaries of the dips are considered to be found.
    @type bound_thres_ratio: float
    @ivar dip_rise_thres: a threshold indicating how much the function must
    rise before the class looks for the closest local maximum of a dip.
    @type dip_rise_thres: float
    @ivar ignore_end_dips: indicates whether the dip at the ends of the data are
    ignored. The end dips are automatically excluded if bound_ref is set to
    average. 
    @type ignore_end_dips: boolean
    @ivar min_indices: an array of indices where local minima can be
    found. Each minima must be at least min_thres lower than the nearest local
    maxima on the left, or the start of the data, whichever is closer.
    @type min_indices: numpy array, shape:(*)
    @ivar dip_ends_indices: an array of dips. Each dip is represented by a one
    dimensional array of size 2. The first element is the left boundary. The
    second element is the right boundary.
    @type dip_ends_indices: numpy array, shape:(*,2)
    @ivar dip_widths: an array of dip widths
    @type dip_widths: numpy array(*)
    @ivar auto_update: deep magic. Indicates whether or not set_var
    automatically updates second-order class variables. Should always be true
    unless the user practices masochism.
    @type auto_update: boolean '''
    
    data=[]
    bound_ref = 'max'
    bound_thres_ratio = 1
    min_thres=0
    dip_rise_thres=0
    ignore_end_dips = True
    min_indices=np.array([])
    dip_ends_indices = np.array([])
    dip_widths=np.array([])
    auto_update=True

    def __init__ (self, data, 
                  bound_ref='max', bound_thres_ratio=1, 
                  min_thres=0, dip_rise_thres=0, ignore_end_dips=True):
        '''Initialize the class. Initializes self.min_indices,
        self.dip_ends_indices, and self.dip_widths.
        @return:None
        @type data: numpy array/list, shape:(*)
        @type bound_ref: str
        @type bound_thres_ratio: float
        @type min_thres: float
        @type dip_rise_thres: float
        @type ignore_end_dips: boolean        
        @see class variables ''' 
        self.data=data
        self.bound_ref=bound_ref
        self.bound_thres_ratio=bound_thres_ratio
        self.min_thres=min_thres
        self.dip_rise_thres=dip_rise_thres
        self.ignore_end_dips=ignore_end_dips
        all_falls=fa.get_all_falls(self.data, self.min_thres)# This has to go after all the input parameters.
        if all_falls.size!=0:
            self.min_indices=np.transpose(all_falls)[1]
        else:
            self.min_indices=np.array([])
        self.dip_ends_indices=self.get_dip_ends() # This has to go after min_indices.
        self.dip_widths=self.get_dip_widths()#This has to go after dip_ends_indices.
        

    def update(self):
        '''Updates the object according to current attributes.'''
        self.__init__(data=self.data, bound_ref=self.bound_ref, 
                  bound_thres_ratio=self.bound_thres_ratio, 
                  min_thres=self.min_thres, dip_rise_thres=self.dip_rise_thres,
                  ignore_end_dips=self.ignore_end_dips)


    def set_var(self, data='No change', bound_ref='No change', 
                bound_thres_ratio='No change', 
                min_thres='No change',dip_rise_thres= 'No change',
                ignore_end_dips='No change'):
        '''Sets the object attributes.
        @return: None
        @type data: numpy array/list, shape:(*)
        @type bound_ref: str
        @type bound_thres_ratio: float        
        @type min_thres: float
        @type dip_rise_thres: float
        @type ignore_end_dips: boolean '''
        if data!='No change':
            self.data=data
        if bound_ref!='No change':
            self.bound_ref=bound_ref
        if bound_thres_ratio!='No change':
            self.bound_thres_ratio=bound_thres_ratio
        if min_thres!='No change':
            self.min_thres=min_thres
        if dip_rise_thres!='No change':
            self.dip_rise_thres=dip_rise_thres
        if ignore_end_dips!='No change':
            self.ignore_end_dips=ignore_end_dips
        if self.auto_update==True:
            self.update()


    def get_dip_ends(self):
        """
        @return: an array of dips in the order they appear in self.data. Each
        dip is represented by a one dimensional array of size 2. The first
        element is the left boundary, and the second element is the right
        boundary.
        @rtype: numpy array, shape:(*,2)"""
        data=self.data
        percentage=self.bound_thres_ratio
        dip_ends=[]
        all_mins=self.min_indices
        if self.bound_ref=='max':
            if self.ignore_end_dips==True:
                all_mins=all_mins[1:np.size(all_mins)-1]
            for i in range(0,len(all_mins)):
                left_max_pos=fa.get_rise(self.data,thres=self.dip_rise_thres, start_index=all_mins[i], reverse=True)[1]
                right_max_pos=fa.get_rise(self.data,thres=self.dip_rise_thres, start_index=all_mins[i], reverse=False)[1]
                if left_max_pos==None or right_max_pos==None:
                    continue
                left_max=data[left_max_pos]
                right_max=data[right_max_pos]
                left_thres_value=percentage*(left_max-data[all_mins[i]])+data[all_mins[i]]
                right_thres_value=percentage*(right_max-data[all_mins[i]])+data[all_mins[i]]
                left_thres_index=fa.get_thres_index(self.data, left_thres_value,start_index=all_mins[i], reverse=True)
                right_thres_index=fa.get_thres_index(self.data, right_thres_value,start_index=all_mins[i], reverse=False)  
                dip_ends.append([left_thres_index, right_thres_index])
        elif self.bound_ref=='average':
            right_max_pos=fa.get_rise(self.data,thres=self.dip_rise_thres, start_index=all_mins[0], reverse=False)[1]
            left_max_pos=fa.get_rise(self.data,thres=self.dip_rise_thres, start_index=all_mins[1], reverse=True)[1]
            average=np.mean(data[right_max_pos:left_max_pos+1])
            for i in range(1, len(all_mins)-1):
                left_thres_value=percentage*(average-data[all_mins[i]])+data[all_mins[i]]
                right_max_pos=fa.get_rise(self.data, thres=self.dip_rise_thres, start_index=all_mins[i], reverse=False)[1]
                left_max_pos=fa.get_rise(self.data, thres=self.dip_rise_thres, start_index=all_mins[i+1], reverse=True)[1]
                average=np.mean(data[right_max_pos:left_max_pos+1])
                right_thres_value=percentage*(average-data[all_mins[i]])+data[all_mins[i]]
                left_thres_index=fa.get_thres_index(self.data,left_thres_value,start_index=all_mins[i], reverse=True)
                right_thres_index=fa.get_thres_index(self.data,right_thres_value,start_index=all_mins[i], reverse=False)
                dip_ends.append([left_thres_index, right_thres_index])
        dip_ends=np.array(dip_ends)
        return dip_ends
    
    
    def get_dip_widths(self):
        """@return: an array of dip widths. 
        @rtype: numpy array, shape:(*) """
        dip_widths=[]
        for i in self.dip_ends_indices:
            dip_widths.append(i[1]-i[0])
        dip_widths=np.array(dip_widths)
        return dip_widths


    def get_corr_min_indices(self):
        '''@return: an array of min indices such that the ith value corresponds
        to the ith dip. 
        @rtype: numpy array, shape:(*)'''
        corr_min_indices=[]
        for i in self.dip_ends_indices:
            corr_min_index=fa.get_fall(self.data, self.min_thres, i[0])[1]
            corr_min_indices.append(corr_min_index)
        corr_min_indices=np.array(corr_min_indices)
        return corr_min_indices


    def plot_spec(self, operant, condition,
                 closeup=False, closeup_name=None, closeup_analysis=True):
        '''The function takes operant, which must be an array with the length
        equal to the length of self.dip_ends_indices, and condition, which
        should be a boolean function, as parameters. If condition, given
        operant[i], returns True, plots the ith dip. If closeup=True, shows
        closeup of special dips with title modified by closeup_name. If
        closeup_analysis=True, shows analysis of special dips on closeup
        graphs.
        
        @return: None
        @type operant: numpy array
        @type condition: boolean function(element, index)
        @type closeup: boolean
        @type closeup_name: str
        @type closeup_analysis: boolean '''
        if np.shape(operant)[0]!=np.shape(self.dip_ends_indices)[0]:
            print 'The operant array does not have a 1 to 1 correspondence with the dips.'
            sys.exit(1)
        spec_dip_nums=np.array(arf.get_specs(operant, condition))
        spec_dip_nums=np.array(spec_dip_nums.flat)
        for i in spec_dip_nums:
            fa.plot_range(self.data, self.dip_ends_indices[i][0],
                          self.dip_ends_indices[i][1]+1,
                          'k-',linewidth=4)
        if closeup==True:
            for i in spec_dip_nums:
                dip_ends=self.dip_ends_indices[i]
                dip_width=dip_ends[1]-dip_ends[0]
                left_lim=dip_ends[0]-2*dip_width
                right_lim=dip_ends[1]+2*dip_width
                if left_lim<0:
                    left_lim=0
                if right_lim>=np.shape(self.data)[0]:
                    right_lim=np.shape(self.data)[0]-1
                fig=plt.figure()
                fig.set_size_inches(15 , 6)
                if closeup_name!=None:
                    plt.title('Dip ' + str(i) + ' of ' + closeup_name)
                fa.plot_range(self.data,left_lim,right_lim+1,'b-')
                fa.plot_range(self.data,dip_ends[0],dip_ends[1]+1,'k-',linewidth=4)
                if closeup_analysis==True:
                    analysis_text = "Dip Number: " + str(i) + '\n' + 'Dip Width: ' + str(dip_width)
                    plt.figtext(0.9,0.8,analysis_text)

                
    def get_spec_range(self, operant, min_val, max_val, inclusive=True, 
                       outside=False, graph=False,
                       closeup=False, closeup_name=None,closeup_analysis=True):
        '''Returns an array of certain dips. For a dip to be returned, operant
        must be within min_val and max_val, inclusively if inclusive is
        true. If outside is True, operant must be outside. If graph=True,
        graphs special dips. If closeup=True, shows closeup of special dips
        with title modified by closeup_name. If closeup_analysis=True, shows
        analysis of special dips on closeup graphs.
        
        @rtype: numpy array, shape:(*)
        @type operant: numpy array, shape:(*)
        @type min_val: float
        @type max_val: float
        @type inclusive: boolean
        @type outside: boolean
        @type graph: boolean
        @type closeup:boolean
        @type closeup_name: str
        @type closeup_analysis: boolean'''
        if outside==False:
            if inclusive==True:
                def condition(x,i):
                    if x>=min_val and x<=max_val:
                        return True
            if inclusive==False:
                def condition(x,i):
                    if x>min_val and x<max_val:
                        return True
        if outside==True:
            if inclusive==True:
                def condition(x,i):
                    if x<=min_val or x>= max_val:
                        return True
            if inclusive==False:
                def condition(x,i):
                    if x<min_val or x>max_val:
                        return True
        if graph==True:
            self.plot_spec(operant, condition, closeup=closeup,
                          closeup_name=closeup_name, 
                          closeup_analysis=closeup_analysis)
        spec_dip_nums=np.array(arf.get_specs(operant, condition))
        spec_dip_nums=np.array(spec_dip_nums.flat)
        return spec_dip_nums

        
    def get_quartile_outliers(self, operant, multiplier=1.5, graph=False,
                              closeup=False, closeup_name=None, 
                              closeup_analysis=True):
        '''Plots all dips in which the corresponding component of operant is an
        outlier according to the interquartile method. Multiplier determines
        the amount by which the interquartile range is mutltiplied. Returns an
        array of quartile outliers. If graph=True, graphs special dips. If
        closeup=True, shows closeup of special dips with title modified by
        closeup_name. If closeup_analysis=True, shows analysis of special dips
        on closeup graphs        
        
        @rtype: numpy array, shape:(*)
        @type operant: numpy array, shape:(*)
        @type multiplier: float
        @type graph: boolean
        @type closeup:boolean
        @type closeup_name: str
        @type closeup_analysis: boolean'''
        Q1=stats.scoreatpercentile(operant, 25)
        Q3=stats.scoreatpercentile(operant, 75)
        interquartile_range=Q3-Q1
        min_val=Q1-multiplier*interquartile_range
        max_val=Q3+multiplier*interquartile_range
        print "Now printing quartile outlier data."
        print "Outliers have dip widths less than",min_val,"and more than",max_val
        return self.get_spec_range(operant, min_val, max_val,inclusive=True, 
                                   outside=True, graph=graph,
                                   closeup=closeup, closeup_name=closeup_name,
                                   closeup_analysis=closeup_analysis)


    def plot_data(self,plot_name=None, xlabel='',ylabel='',plot_dips=True,
                  plot_dip_ends=True, plot_mins=True, plot_average=False,
                  plot_spec=None, plot_spec_args=None ):
        """Plots the data.  If plot_dips=True, indicates the entirety of the
        dips. If plot_dip_ends=True, indicates dip boundaries. If
        plot_mins=True, plots minimums. If plot_average=True, plots average
        value from the first relative maximum after a minimum to the last
        relative maximum before the next minimum. If plot_spec='outlier', calls
        self.plot_quartile_outliers with arguments plot_spec_args. If
        plot_spec='range', calls self.plot_spec_range with arguments
        plot_spec_args. For both 'outlier' and 'range', sets 'graph' to True
        and 'operant' to self.dip_widths by default. plot_name, xlabel, and
        ylabel indicate the plot's title, x-axis label, and y-axis
        label

        @return:None 
        @type plot_name: str
        @type xlabel: str
        @type ylabel: str
        @type plot_dips: boolean
        @type plot_dip_ends: boolean
        @type plot_mins: boolean
        @type plot_average: boolean
        @type plot_spec:str
        @type plot_spec_args: dict """
        if self.data.size==0:
            raise ValueError ('Data size is zero.')
        data=self.data
        fig=plt.figure()
        fig.set_size_inches(150,10)
        if plot_name!=None:
            plt.title(plot_name)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.plot(self.data,'b-')
        if plot_mins==True and self.min_indices.size!=0:
            plt.plot(self.min_indices, data[self.min_indices], 'bd')
        if plot_dip_ends==True and self.dip_ends_indices.size!=0:
            flat_dip_ends=np.array(self.dip_ends_indices.flat)
            plt.plot(flat_dip_ends, data[flat_dip_ends], 'ro')
        if plot_dips==True:
            for i in self.dip_ends_indices:
               fa.plot_range(self.data, i[0], i[1]+1, 'r-')
        if plot_average==True:
            for i in range(0, len(self.min_indices)-1):
                x_vals=[]
                y_vals=[]
                right_max_pos=fa.get_rise(self.data, thres=self.dip_rise_thres, 
                                           start_index=self.min_indices[i], 
                                           reverse=False)[1]
                left_max_pos=fa.get_rise(self.data, thres=self.dip_rise_thres, 
                                          start_index=self.min_indices[i+1], 
                                          reverse=True)[1]
                average=np.mean(data[right_max_pos:left_max_pos+1])
                for i in range (right_max_pos, left_max_pos+1):
                    x_vals.append(i)
                    y_vals.append(average)
                x_vals,y_vals = np.array(x_vals), np.array(y_vals)
                plt.plot(x_vals, y_vals, 'g-')
        if plot_spec!=None and plot_spec_args==None: plot_spec_args=dict()
        if plot_spec=='outliers':
            if ('operant' in plot_spec_args)==False:
                plot_spec_args['operant']=self.dip_widths
            if ('graph' in plot_spec_args)==False:
                plot_spec_args['graph']=True
            self.get_quartile_outliers(**plot_spec_args)
        if plot_spec=='range':
            if ('operant' in plot_spec_args)==False:
                plot_spec_args['operant']=self.dip_widths
            if ('min_val' in plot_spec_args)==False:
                print "MUST HAVE MINIMUMMM!!! NOO!!!!!"
                return
            if ('max_val' in plot_spec_args)==False:
                print "MUST HAVE MAXIMUMMM!!! NOO!!!!!"
                return
            if ('graph' in plot_spec_args)==False:
                plot_spec_args['graph']=True
            self.get_spec_range(**plot_spec_args)


    def plot_hist(self, hist_data, bins=10, data_name=None):
        """Plots the histogram of hist_data, using bins number of bins. If
        data_name !=None, title the graph and the x axis according to
        data_name. Returns None.  
        @return: None
        @type hist_data: numpy array/list, shape:(*)
        @type bins: int
        @type data_name: str """
        plt.figure()
        plt.hist(hist_data,bins=bins)
        if data_name!=None:
            plt.title("Distribution of " + data_name)
            plt.xlabel(data_name)

            
    def show(self):
        """Shows the graph.  Returns None."""
        if len(plt.get_fignums())==0:
            print "You haven't plotted anything yet. Go back to your cave."
            return None
        plt.show()


    def print_analysis(self, operant='dip_widths', operant_name=None):
        """Prints out data analysis of operant, with operant_name as its 
        name.
        @return: None
        @type operant: numpy array, shape:(*)
        @type operant_name: str"""
        if operant=='dip_widths':
            if operant_name==None:
                print "Dip Width Statistics :)"
            else:
                print operant_name + ' Statistics'
            operant=self.dip_widths
        else: 
            if operant_name!=None:
                print operant_name + ' Statistics'
            else:
                print 'Statistics'
        print "Mean: ",np.mean(operant)
        print "Standard Deviation: ",np.std(operant)
        print "Median: ",np.median(operant)
        print "Minimum: ",np.min(operant)
        print "Maximum: ",np.max(operant)
        print "Q1: ", stats.scoreatpercentile(operant, 25)
        print "Q3: ", stats.scoreatpercentile(operant, 75)


    def print_spec_analysis(self,special_dip_nums):
        """Prints out summary of special_dip_nums, an array of the dip numbers
        of special dips.
        @return: None
        @type special_dip_nums: numpy array, shape:(*)"""
        print "Printing special dip info"
        print "Special Dips: ",special_dip_nums
        corr_min_indices=self.get_corr_min_indices()
        prev_dip_pos=None
        prev_dip_num=None
        for element in special_dip_nums:
            print ""
            print "Dip num:",element
            curr_dip_pos=corr_min_indices[element]
            print "Dip min position:",curr_dip_pos
            print "width: ", self.dip_ends_indices[element][1]- self.dip_ends_indices[element][0]
            if prev_dip_pos!=None:
                abs_diff=curr_dip_pos-prev_dip_pos
                print "Absolute distance from previous:",abs_diff
                num_diff=element-prev_dip_num
                print str(num_diff)+" dips from previous"
            else: print "First dip"
            prev_dip_pos=curr_dip_pos
            prev_dip_num=element
    

#End class.

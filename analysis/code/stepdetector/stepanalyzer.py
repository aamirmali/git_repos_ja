"""Master module of this package"""
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import scipy.signal as sig
import crosscorr_detect
import code.common.functionanalyzer as fa


class Transition:
    """A transition; should be private."""
    type=None
    """either 'rise' or 'fall'"""
    start_pos=None
    """starting index of the transition"""
    end_pos=None
    """ending index of the transition"""
    amplitude=None
    """amplitude of the transition (high value - low value)"""
    def __init__(self,type,start_pos,end_pos):
        self.type=type
        self.start_pos=start_pos
        self.end_pos=end_pos
        self.amplitude=None


class StepAnalyzer:
    """This class is meant to find the amplitude of heater blocks. It uses
    three methods to do so: directly finding the transitions, using
    cross-correlation to find the transitions, and using twice the standard
    deviation as the amplitude.  The class also detects if the data is ramping,
    noise, or 0 throughout."""
    data=None
    rises=None
    falls=None
    transitions=[]
    amplitudes=None
    thres=None
    noise_thres=5
    is_noise=None
    is_ramping=None
    is_off=None
    period=None
    error_detected=None
    crosscorr_error_thres=0.1
    crosscorr_error=None
    ramping_std_thres=1e7
    method_used=None
    verbose=None
    def __init__(self,data,verbose=False,plot=False):
        """Initializes class. Sets attributes method_used, is_noise, 
        is_ramping, and is_off, which the user should access by calling 
        self.get_data_quality.
        @param data: data to be analyzed
        @param verbose: whether or not error messages should be printed
        @param plot: whether class should plot its results
        @type data: 1D array
        @type verbose: boolean
        @type plot: boolean
        """
        self.data=sig.detrend(data)
        self.thres=np.std(data)
        self.error_detected=False
        self.is_noise=False
        self.is_ramping=False
        self.is_off=False
        self.method_used='none'
        self.transitions=[]
        self.verbose=verbose
        if np.std(data)==0:
            self.is_off=True
            return
        elif np.std(data)>self.ramping_std_thres:
            self.is_ramping=True
            return
        elif self.is_data_noise()==True:
            self.is_noise=True
            return
        else:
            self.period=self.find_period()
            self.rises=fa.get_all_rises(self.data,self.thres)
            self.falls=fa.get_all_falls(self.data,self.thres)
            self.combine_transitions()
            #ensure combine_transitions detected no errors
#            self.error_detected=True
            if self.error_detected==False:
                self.set_amplitudes()
            #checks whether set_amplitudes detected any errors
            if self.error_detected==False:
                self.amplitudes=self.amplitudes_to_list()
            if self.error_detected==False and len(self.amplitudes)!=0:
                self.method_used='best'
                if plot: self.plot_transitions_and_avgs()
            else:
                stats=crosscorr_detect.get_amplitudes(self.data,self.period,
                                                      plot)
#                print "stats",stats
                if stats!=None and stats[1]<self.crosscorr_error_thres:
                    self.amplitudes=stats[0]
                    self.method_used='cross-corr'
                    self.crosscorr_error=stats[1]
                else:
                    self.method_used='std'
                    self.amplitudes=None
                    if plot:
                        #Hack. Unfortunately, there's no way to make
                        #crosscorr_detect plot iff detection actually succeeds.
                        plt.gcf().clear()
                        plt.plot(self.data)
                        plt.title("Standard deviation method")
                        upperbound=self.get_med_amplitude()/2
                        fa.plot_const(0,len(self.data),upperbound)
                        fa.plot_const(0,len(self.data),-upperbound)

    def get_method_used(self):
        """@return: method used to find amplitude, if amplitude was
        found. Could be 'best', 'cross-corr', or 'std'. If amplitude was not
        found, returns 'ramping', 'noise', or 'off' to indicate why it was not
        found."""
        if self.is_ramping: return "ramping"
        elif self.is_noise: return "noise"
        elif self.is_off: return "off"
        else: return self.method_used

    def get_med_amplitude(self):
        """@return: the median amplitude. Returns None if no such amplitude was
        found."""
        if self.is_noise or self.is_ramping or self.is_off:
            return None
        if self.amplitudes!=None:
            return np.median(self.amplitudes)
        else:
            return 2*np.std(self.data)

    def get_quartile_amplitude(self):
        """@return: the interquartile range of the amplitudes found, or None
        if no amplitudes were found in the first place. Note that the error in
        the amplitude estimate should be this value divided by the square root
        of the number of amplitudes found."""
        if self.is_noise or self.is_ramping or self.is_off:
            return None
        if self.amplitudes!=None and len(self.amplitudes)>0:
            Q1=stats.scoreatpercentile(self.amplitudes,25)
            Q3=stats.scoreatpercentile(self.amplitudes,75)
            return Q3-Q1
        else:
            return None


    def find_period(self):
        #Finds the period of the heater steps. Returns the period in number of
        #data points, or None if the period could not be found.
        fourier=np.fft.rfft(self.data)
        psd=(fourier*fourier.conjugate()).real
        max_i=0
        max_val=0
        for i in range(0,len(psd)):
            if psd[i]>max_val:
                max_val=psd[i]
                max_i=i
            i+=1
        if max_i==0:
            return None
        else:
            period=1.*len(self.data)/max_i
            return int(np.rint(period))

    def is_data_noise(self):
        #Indicates whether or not data is noise.
        autocorr=np.correlate(self.data,self.data,mode='same')
        autocorr=autocorr-np.mean(autocorr)
        autocorr_abs=np.abs(autocorr)
        ratio=autocorr[len(autocorr_abs)/2]/np.median(autocorr_abs)
        if ratio>self.noise_thres:
            return True
        else:
            return False


    def combine_transitions(self):
        #Combines all rises and falls found by the class into a list of
        #Transition objects, ordered from low index to high index.
        rise_i=0
        fall_i=0
        while rise_i<len(self.rises) and fall_i<len(self.falls):
            #add rises until pos of rise exceeds pos of next fall
            while rise_i<len(self.rises):
                if fall_i<len(self.falls) and \
                        self.rises[rise_i][0]>=self.falls[fall_i][0]:
                    break
                t=Transition('rise',self.rises[rise_i][0],
                             self.rises[rise_i][1])
                self.transitions.append(t)
                rise_i+=1
            #add falls until pos of fall exceeds pos of next rise
            while fall_i<len(self.falls):
                if rise_i<len(self.rises) and \
                        self.falls[fall_i][0]>=self.rises[rise_i][0]:
                    break
                t=Transition('fall',self.falls[fall_i][0],
                             self.falls[fall_i][1])
                self.transitions.append(t)
                fall_i+=1
        if len(self.transitions)<=2:
            if self.verbose:
                print "Only",len(self.transitions),"transitions detected!"
            self.error_detected=True

        
    def set_amplitudes(self):
        #Uses list of Transition objects found by self.combine_transitions to
        #find a list of amplitudes, setting the 'amplitude' attribute of every
        #Transition accordingly. Also sets self.error_detected to indicate
        #whether any errors in the list of Transitions was found.
        amplitude_count=0
        for i in range(1,len(self.transitions)-1):
            if self.transitions[i].type==self.transitions[i-1].type\
                    or self.transitions[i].type==self.transitions[i+1].type:
                if self.verbose:
                    print "False positive or negative detected around",\
                        self.transitions[i].start_pos
                self.error_detected=True
                return

            else:
                #First, check whether the separation between the prev and next
                #transitions is seriously wrong (<0.5*period or >1.5*period)
                left_pos=(self.transitions[i-1].start_pos+self.transitions[i-1].end_pos)/2
                right_pos=(self.transitions[i+1].start_pos+self.transitions[i+1].end_pos)/2
                separation=right_pos-left_pos
                if np.abs(separation-self.period)>0.5*self.period:
                    self.error_detected=True
                    if self.verbose:
                        print "Incorrect separation near",left_pos
                    return

                amplitude_count+=1
                #find avg to the left of the transition
                lowerlim=self.transitions[i-1].end_pos
                upperlim=self.transitions[i].start_pos
                left_avg=np.mean(self.data[lowerlim:upperlim+1])
#                self.draw_const(lowerlim,upperlim,left_avg)
                #find avg to right of transition
                lowerlim=self.transitions[i].end_pos
                upperlim=self.transitions[i+1].start_pos
                right_avg=np.mean(self.data[lowerlim:upperlim+1])
#                self.draw_const(lowerlim,upperlim,right_avg)
                self.transitions[i].amplitude=np.abs(right_avg-left_avg)
        if amplitude_count==0:
            self.error_detected=True
                
    def plot_transitions_and_avgs(self):
        #Plots the transitions and averages in between. Can only be called if
        #method_used='best', because otherwise, the program has no idea how
        #wide the transitions are.
        if self.method_used!='best':
            print "Yo, your data sucks. Get better data."
            return
        plt.plot(self.data)
        plt.title("Best method")
        for i in range(0,len(self.transitions)):
            transition=self.transitions[i]
            #First, plot the transition.
            if transition.type=='rise':
                fa.plot_range(self.data,transition.start_pos,
                              transition.end_pos+1,format='r-^')
            elif transition.type=='fall':
                fa.plot_range(self.data,transition.start_pos,
                              transition.end_pos+1,format='g-v')
            else:
                print "Dumb programmer/user detected. Will now self destruct."
            #Now, plot the avg. value of the parts in between the transitions
            if transition.amplitude!=None:
                #plot left
                lowerlim=self.transitions[i-1].end_pos
                upperlim=transition.start_pos
                leftavg=np.mean(self.data[lowerlim:upperlim+1])
                fa.plot_const(lowerlim,upperlim,leftavg)
                #plot right
                lowerlim=transition.end_pos
                upperlim=self.transitions[i+1].start_pos
                rightavg=np.mean(self.data[lowerlim:upperlim+1])
                fa.plot_const(lowerlim,upperlim,rightavg)


    def amplitudes_to_list(self):
        #Takes all amplitudes in self.transitions and puts them in a list.
        #Returns the list.
        amplitudes=[]
        for i in range(0,len(self.transitions)):
            if self.transitions[i].amplitude != None:
                amplitudes.append(self.transitions[i].amplitude)
        return amplitudes

    def remove_transitions(self):
        """Removes transitions from the datastream. Should only be used if
        self.method_used=='best'.
        @return: the resulting datastream. Returns None if self.method_used is
        not 'best'.
        """
        if self.method_used!='best':
            print "can't remove transitions; no idea where they are"
            return None
        datastream=[]
        zero_data_found=False
        for i in range(0,len(self.transitions)-1):
            curr_trans=self.transitions[i]
            next_trans=self.transitions[i+1]
            if curr_trans.end_pos < next_trans.start_pos:
                avg=np.mean(self.data[curr_trans.end_pos:next_trans.start_pos])
                for i in range(curr_trans.end_pos,next_trans.start_pos+1):
                    datastream.append(self.data[i]-avg)
            else:
                zero_data_found=True
        if zero_data_found==True:
            print "Data of 0 size detected!"
        return datastream

    def plot_hist(self):
        """Plots a histogram of the amplitudes"""
        if self.method_used != 'best' and self.method_used != 'cross-corr':
            print "Not possible to plot histogram; data is horrible."
            return
        plt.figure()
#        amplitudes=self.amplitudes_to_list()
        if len(self.amplitudes)==0:
            print "No amplitudes to plot!"
            return
        plt.hist(self.amplitudes)
        plt.title("Histogram of amplitudes")

    def print_analysis(self):
        """Prints analysis of the data."""
        print "Method used was",self.method_used
        if self.method_used=='best':
            amplitudes=self.amplitudes_to_list()
            print len(amplitudes),"amplitudes analyzed"
            print "Amplitude median",self.get_med_amplitude()
            print "Amplitude quartile range",self.get_quartile_amplitude()

            rise_widths=[]
            for i in range(0,len(self.rises)):
                width=self.rises[i][1]-self.rises[i][0]
                rise_widths.append(width)
            print "Rise width mean",np.mean(rise_widths)
            print "Rise width STD",np.std(rise_widths)

            fall_widths=[]
            for i in range(0,len(self.falls)):
                width=self.falls[i][1]-self.falls[i][0]
                fall_widths.append(width)
            print "Fall width mean",np.mean(fall_widths)
            print "Fall width STD",np.std(fall_widths)
        
        elif self.method_used=='cross-corr':
            print len(self.amplitudes),"amplitudes analyzed"
            print "Amplitude median",self.get_med_amplitude()
            print "Amplitude quartile range",self.get_quartile_amplitude()
            print "% detection failure:",self.crosscorr_error
        
        elif self.method_used=='std':
            print "Amplitude:",self.get_med_amplitude()
            if self.crosscorr_error==None:
                print "cross correlation step failed completely"
            else:
                print "% detection failure in cross correlation step:",\
                    self.crosscorr_error
            

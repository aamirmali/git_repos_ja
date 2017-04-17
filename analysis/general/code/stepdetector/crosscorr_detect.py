"""Internal module used to determine heater block amplitudes using the
cross correlation method. Only master_get_amplitudes should be called 
directly."""
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import scipy.signal as sig
import code.common.functionanalyzer as fa


def cross_corr_block(data,period):
    #Finds the cross correlation of data with a step-function kernel of
    #period period.  Returns the cross-correlation.
    length=period/2
    kernel=[]
    for i in range(0,length):
        if i<length/2: kernel.append(-1)
        if i==length/2: kernel.append(0)
        if i>length/2: kernel.append(1)
    corr=fa.correlate(data,kernel,mode='same')
    return corr


def compute_amplitudes_block(corr,data,period,plot=False):
    #Computes amplitudes, assuming the heater blocks look more like square
    #waves than sine waves. corr is the cross-correlation with the appropriate
    #kernel, indicating the positions of the transitions. data is the
    #timestream, period is the period of the blocks, and plot indicates
    #whether the function should plot its results. Returns tuple
    #(amplitudes,fractional_error), where amplitudes is a list and
    #fractional_error is between 0 and 1. Returns None if period is invalid, or
    #if 2 or fewer transitions were detected.
    abs_corr=np.abs(corr)
    abs_corr=sig.convolve(sig.hann(period/8),abs_corr,mode='same')
    rises=fa.get_all_rises(abs_corr,np.std(abs_corr))
    extrema=np.transpose(rises)[1]
    amplitudes=[]
    errors=0
    for i in range(1,len(extrema)-1):
        #calculate median value for flat part to the left
        lowerlim=extrema[i-1]
        upperlim=extrema[i]
        if np.abs(upperlim-lowerlim-period/2.)>0.05*period:
            errors+=1
        left_med=np.median(data[lowerlim:upperlim+1])
        if plot:
            fa.plot_const(lowerlim,upperlim,left_med)
        #calculate median value for flat part to right
        lowerlim=extrema[i]
        upperlim=extrema[i+1]
        right_med=np.median(data[lowerlim:upperlim+1])
        if plot:
            fa.plot_const(lowerlim,upperlim,right_med)
        amplitude=np.abs(right_med-left_med)
        amplitudes.append(amplitude)
    if len(extrema)>2 and period<len(data)/2:
        fractional_error=1.*errors/len(extrema)
        return (amplitudes,fractional_error)
    else:
        return None

def cross_corr_sine(data,period):
    #Finds the cross correlation of data with a constant-value kernel of
    #period period.  Returns the cross-correlation.
    length=period/2
    kernel=[]
    for i in range(0,length):
        #create triangle wave kernel
        val=1-2.*np.abs(i-length/2)/length
        val=1
        kernel.append(val)
    corr=fa.correlate(data,kernel,mode='same')
    return corr


def find_larger_neighbor(data,pos):
    #Returns position of maximum among 3 data points: pos, pos-1, and pos+1.
    #pos must not be outside array bounds
    ref_val=data[pos]
    best_pos=pos
    if pos-1 >=0 and data[pos-1]>ref_val:
        ref_val=data[pos-1]
        best_pos=pos-1
    if pos+1<len(data) and data[pos+1]>ref_val:
        best_pos=pos+1
    return best_pos


def find_smaller_neighbor(data,pos):
    #Returns position of minimum among 3 data points: pos, pos-1, and pos+1.
    #pos must not be outside array bounds
    ref_val=data[pos]
    best_pos=pos
    if pos-1 >=0 and data[pos-1] <ref_val:
        ref_val=data[pos-1]
        best_pos=pos-1
    if pos+1<len(data) and data[pos+1] < ref_val:
        best_pos=pos+1
    return best_pos


def compute_amplitudes_sine(corr,data,period,plot=False):
    #Computes amplitudes, assuming the heater blocks look more like sine
    #waves than square waves. corr is the cross-correlation with the appropriate
    #kernel, indicating the positions of the maxima. data is the
    #timestream, period is the period of the blocks, and plot indicates
    #whether the function should plot its results. Returns tuple
    #(amplitudes,fractional_error), where amplitudes is a list and
    #fractional_error is between 0 and 1. Returns None if period is invalid, or
    #if 2 or fewer maxima were detected in the data.
    corr=corr-np.mean(corr)
    rises=fa.get_all_rises(corr,np.std(corr))
    maxes=np.transpose(rises)[1]    
    falls=fa.get_all_falls(corr,np.std(corr))
    mins=np.transpose(falls)[1]
    max_phases=[]
    min_phases=[]
    errors=0
    fraction_error=0
    for i in range(len(maxes)):
        max_phases.append(maxes[i]%period)
        if i+1 < len(maxes):
            if abs(maxes[i+1]-maxes[i]-period) >1:
                errors+=1
    for i in range(len(mins)):
        min_phases.append(mins[i]%period)
        if i+1<len(mins):
            if abs(mins[i+1]-mins[i]-period) > 1:
                errors+=1
    fraction_error=float(errors)/(len(maxes)+len(mins))
    max_phase=np.median(max_phases)
    min_phase=np.median(min_phases)
    extrema=[]
    if min_phase<max_phase:
        for n in range(len(data)/period+1):
            curr_min=n*period+min_phase
            curr_max=n*period+max_phase
            if curr_min<len(data):
                curr_min=find_smaller_neighbor(data,curr_min)
                extrema.append(curr_min)
            if curr_max<len(data):
                curr_max=find_larger_neighbor(data,curr_max)
                extrema.append(curr_max)
    elif max_phase < min_phase:
        for n in range(len(data)/period+1):
            curr_min=n*period+min_phase
            curr_max=n*period+max_phase
            if curr_max<len(data):
                curr_max=find_larger_neighbor(data,curr_max)
                extrema.append(curr_max)
            if curr_min<len(data):
                curr_min=find_smaller_neighbor(data,curr_min)
                extrema.append(curr_min)
    else:
        return None
    if len(extrema)<2:
        return None
    amplitudes=[]
    for i in range(0,len(extrema)-1):
        curr_extrem=extrema[i]
        next_extrem=extrema[i+1]
        if plot:
            plt.plot(curr_extrem,data[curr_extrem],'go')
            plt.plot(next_extrem,data[next_extrem],'go')
        amplitude=abs(data[curr_extrem]-data[next_extrem])
        amplitudes.append(amplitude)
    if len(amplitudes)==0:
        return None
    else:
        return (amplitudes,fraction_error)

    
def get_amplitudes(data,period,plot=False):
    """Master function of this internal module. Uses the cross-correlation
    method to determine amplitudes. plot determines whether the module plots
    its results.
    @return: (amplitudes,fractional_error) if successful where amplitudes is
    a list. fractional_error is a number between 0 and 1, indicating the
    percentage of heater blocks that weren't detected. Returns None if
    period couldn't be detected, or if the number of heater blocks detected
    is less than 3"""
    if plot:
        plt.plot(data)
        plt.title("Cross correlation method")
    if period==None:
        return None
    if period>20:
        corr=cross_corr_block(data,period)
        ret=compute_amplitudes_block(corr,data,period,plot)
    else:
        corr=cross_corr_sine(data,period)
        ret=compute_amplitudes_sine(corr,data,period,plot)
    return ret



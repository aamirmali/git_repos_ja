import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as sig

def get_fall(data, thres=0, start_index=0, reverse=False):
    """Finds the indices of the beginning and the end of the first fall in data
    starting from start_index. A fall is defined to be a segment of a function
    that is monotonically decreasing (non-increasing) for which the last value
    is at least thres smaller than the first value. The beginning of the fall
    is defined to be the point at where the function stops rising. If the
    start_index is in the middle of the fall, the start_index will be taken to
    be the beginning. The end of the of the fall is defined to be the point
    where the function begins to rise again. If no such end can be found, no
    fall is considered to be found. If reverse is True, this method searches
    the data backwards(from higher indices to lower indices); a fall in this
    case is a segment that decreases as one moves from right to left (higher
    indices to lower indices).

    @return: [beginning index, end index]; None, if no fall is found or data
    size is zero
    @rtype: numpy array, shape: (2)
    @type data: numpy array, shape: (*)
    @type thres: float 
    @type start_index: int 
    @type reverse: boolean """
    i=start_index
    if len(data)==0:
        print "Data size is 0."
        return None
    try: 
        ref_val=data[i]
        ref_index=i
    except IndexError:
        print "Invalid start_index. Virus uploaded to computer."
        sys.exit(1)
    if reverse==False:
        while i<len(data)-1:
            #search for max and set it as reference value
            while i<len(data)-1 and data[i+1]>data[i]:
                i+=1
            ref_val=data[i]
            ref_index=i
            #search for min
            while i<len(data)-1 and data[i+1]<=data[i]:
                i+=1
            if (ref_val-data[i]) > thres and i!=len(data)-1:
                return np.array((ref_index,i))
               #min found, so return
    if reverse==True:
        while i>0:
            while i>0 and data[i-1]>data[i]:
                i-=1
            ref_val=data[i]
            ref_index=i
            while i>0 and data[i-1]<=data[i]:
                i-=1
            if (ref_val-data[i])>thres and i!=0:
                return np.array((ref_index,i))
    return None


def get_rise(data, thres=0, start_index=0, reverse=False):
    """Finds the indices of the beginning and the end of the first rise in data
    starting from start_index. A rise is defined to be a segment of a function
    that is monotonically increasing (non-decreasing) for which the last value
    is at least thres bigger than the first value. The beginning of the rise is
    defined to be the point at where the function stops falling. If the
    start_index is in the middle of the rise, the start_index will be taken to
    be the beginning. The end of the of the rise is defined to be the point
    where the function begins to fall again. If no such end can be found, no
    rise is considered to be found. If reverse is True, this method searches
    the data backwards(from higher indices to lower indices); a rise in this
    case is a segment that increases as one moves from right to left (higher
    indices to lower indices).

    @return: [beginning index, end index]; None, if no fall is
    found or data size is zero 
    @rtype: numpy array, shape: (2)
    @type data: numpy array, shape: (*)
    @type thres: float 
    @type start_index: int 
    @type reverse: boolean """
    i=start_index
    if len(data)==0:
        print "Data size is 0."
        return None
    try:
        ref_val=data[i]
        ref_index=i
    except IndexError:
        print "Invalid start_index. Virus uploaded."
        sys.exit(1)
    if reverse==False:
        while i<len(data)-1:
            while i<len(data)-1 and data[i+1]<data[i]:
                i+=1
            ref_val=data[i]
            ref_index=i
            while i<len(data)-1 and data[i+1]>=data[i]:
                i+=1
            if (data[i]-ref_val)>thres and i!=len(data)-1:
                return np.array((ref_index,i))
    if reverse==True:
        while i>0:
            while i>0 and data[i-1]<data[i]:
                i-=1
            ref_val=data[i]
            ref_index=i
            while i>0 and data[i-1]>=data[i]:
                i-=1
            if (data[i]-ref_val)>thres and i!=0:
                return np.array((ref_index,i))
    return None


def get_all_falls(data, thres):   
    """Finds the indices of the beginnings and the ends of all the falls in
    data. A fall is defined to be a segment of a function that is monotonically
    decreasing (non-increasing) for which the last value is at least thres
    smaller than the first value. The beginning of the fall is defined to be
    the point at where the function stops rising. The end of the of the fall is
    defined to be the point where the function begins to rise again. If no such
    end can be found, no fall is considered to be found.

    @return: a numpy array, where the ith element corresponds to the ith fall,
    represented by the numpy array [beginning index, end index]
    @rtype: numpy array, shape: (*,2)
    @type data: numpy array, shape: (*)
    @type thres: float """
    falls=[]
    next_fall=get_fall(data, thres=thres)
    while next_fall!=None:
        falls.append(next_fall)
        next_fall=get_fall(data, thres=thres, start_index=next_fall[1]+1)
    falls=np.array(falls)
    return falls


def get_all_rises(data, thres):
    """Finds the indices of the beginnings and the ends of all the rises in
    data. A rise is defined to be a segment of a function that is monotonically
    increasing (non-decreasing) for which the last value is at least thres
    bigger than the first value. The beginning of the rise is defined to be the
    point at where the function stops falling. The end of the of the rise is
    defined to be the point where the function begins to fall again. If no such
    end can be found, no rise is considered to be found.

    @return: a numpy array, where the ith element corresponds to the ith rise,
    represented by the numpy array [beginning index, end index]
    @rtype: numpy array, shape: (*,2)
    @type data: numpy array, shape: (*)
    @type thres: float """
    rises=[]
    next_rise=get_rise(data, thres=thres)
    while next_rise!=None:
        rises.append(next_rise)
        next_rise=get_rise(data, thres=thres, start_index=next_rise[1]+1)
    rises=np.array(rises)
    return rises


def get_thres_index(data, thres_value, start_index=0, reverse=False):
    """Finds the first value in data that crosses or touches the threshold
    thres_value, starting from start_index. If reverse is True, this method
    searches backwards.
    
    @return: the index where the value of the data crosses or touches the
    threshold thres_value.
    @rtype: int
    @type data: numpy array, shape: (*)
    @type thres_value: float
    @type start_index: int
    @type reverse: boolean """
    i = start_index
    try:
        if reverse == False:
            if thres_value>=data[start_index]:
                while thres_value>data[i]:
                    i+=1
            else:
                while thres_value<data[i]:
                    i+=1
        if reverse == True:
            if thres_value>=data[start_index]:
                while thres_value>data[i]:
                    i-=1
            else:
                while thres_value<data[i]:
                    i-=1
        return i
    except IndexError:
        print "Threshold not reached. Returning None."
        return None


def correlate(data, kernel, mode):
    """Finds the cross-correlation of the kernel on data. This method
    has big-O of n*logn, and is superior to numpy.correlate for data
    with length more than about 3000.
    @return: the cross-correlation of the kernel on data.
    @rtype: numpy array, shape:(*)
    @param data: the data to be cross-correlated.
    @type data: numpy array, shape:(*)
    @param kernel: the template for the cross-correlation
    @type kernel: numpy array, shape:(*)
    @param mode: controls the length of the output. This parameter is
    passed directly into scipy.signal.fftconvolve(). 
    @type mode: str """
    data=np.array(data)
    kernel=np.array(kernel)
    kernel=kernel[::-1]
    return sig.fftconvolve(data,kernel,mode)


def plot_range(data, start_index, end_index, format='b-', **args):
    """Plots the data between start_index and end_index-1 inclusively. The
    parameters of plot is specified with format, and **args.    
    @return: None
    @type data: numpy array, shape: (*)
    @type start_index: int
    @type end_index: int
    @param format: a format string that is directly passed into
    matplotlib.pyplot.plot() @type format: string
    @param args: arguments that control the format of the plot; these are
    passed directly into matplotlib.pyplot.plot() """
    x_val=range(start_index,end_index)
    y_val=data[x_val]
    plt.plot(x_val,y_val, format, **args)


def plot_const(lowerlim,upperlim,value):
    """Plots a constant value of value, from lowerlim to upperlim"""
    x_vals=[]
    y_vals=[]
    for i in range(lowerlim,upperlim+1):
        x_vals.append(i)
        y_vals.append(value)
    x_vals,y_vals=np.array(x_vals),np.array(y_vals)
    plt.plot(x_vals,y_vals,'go')


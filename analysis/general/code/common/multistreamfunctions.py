import os
import sys
import matplotlib.pyplot as plt
import numpy as np
parent_dir=os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
sys.path.append(parent_dir)
from common import arrayfunctions as arf


def sum_filter(data, axis=None, equal_weight=False):
    '''Filters out the sum of data.
    @return: the filtered data. Each data element of data is treated as a
    vector, as is each sum. Each data element will have its projection along
    its corresponding sum subtracted out.
    @rtype: numpy array
    @param data: an array of data elements. If data is an dim dimensional
    array, it is considered to be a (dim-1) dimensional array of data
    elements. The last axis is the data element.
    @type data: numpy array
    @param axis: determines which axis is summed over. If it is j and the data
    is a (a1,a2...a(j-1),aj,a(j+1)...a(dim-1) shaped array of data elements,
    then the sum array be be a (a1...a(j-1),(aj+1)...a(dim-1)) shaped array of
    sum elements. The data in the index [b1]...[b(j-1)][bj][b(j+1)]...[b(dim)]
    will have its projection along the sum element in the index
    [b1]...[b(j-1)][b(j+1)]...[b(dim)] subtracted out. If this parameter is
    None, every axis except the last is summed over, leaving one sum vector.
    @type axis: int
    @param equal_weight: determines whether or not each data element is given
    equal weight in the sum. If it is set to True, each data element will be
    normalized before summed over.
    @type equal_weight: boolean. '''
    if equal_weight==True:
        weighted_data=arf.modify_array(data, arf.wrap(arf.standardize), 
                                       len(data.shape)-1)
    else:
        weighted_data=data
    if axis!=None:
        sum_array = np.sum(weighted_data, axis)
        sum_array = arf.modify_array(sum_array, arf.wrap(arf.standardize), 
                                     len(sum_array.shape)-1)
        index=[]
        index.append(axis)
        index.extend(range(0,axis))
        index.extend(range(axis+1, len(data.shape)))
        data=np.transpose(data, index)
        for index in range(0, data.shape[0]):
            def sum_filter(x, i):
                sum_array_copy=sum_array
                for depth in range(0, len(i)):
                    sum_array_copy=sum_array_copy[i[depth]]
                return arf.projection_filter(x, sum_array_copy, 
                                             normalized_projection=True)
            data[index]=arf.modify_array(data[index], sum_filter, 
                                         len(sum_array.shape)-1)
        index=[]
        index.extend(range(1, axis+1))
        index.append(0)
        index.extend(range(axis+1, len(data.shape)))
        return np.transpose(data, index)
    else:
        sum_vector=arf.sum_space_array_function(weighted_data, arf.wrap(np.sum), 
                                                op_dim=1, 
                                                op_ar_dim=len(np.shape(data))-1)
        sum_vector=arf.standardize(sum_vector)
        def sum_filter(x, i):
            return arf.projection_filter(x, sum_vector, 
                                         normalized_projection=True)
        return arf.modify_array(data, sum_filter, len(data.shape)-1)

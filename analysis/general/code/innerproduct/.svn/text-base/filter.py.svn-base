import numpy as np
import code.common.arrayfunctions as arf
import code.common.multistreamfunctions as msf


def general_filter(data, non_rows=[], non_cols=[], non_elements=[], mean_filter=False, sum_filter=None):
    '''Filters data.
    @return: filtered data. This will be a 2 dimensional array of data, each of
    which is a 1 dimensional array.
    @rtype: numpy array, 3 dimensional
    @param data: the data to be filtered.This parameter is to be a 2
    dimensional array of data elements. The index in the first dimension is the
    row number, and the index in the second dimension is the column
    number. Each data element is to be a 1 dimensional array.
    @type data: numpy array, 3 dimensional
    @param non_rows: the rows (first dimension) to be ignored. The data in
    these rows will be set a stream of 0.
    @type non_rows: numpy array/list/tuple, shape:(*)
    @param non_cols: the columns (second dimension) to be ignored. The data in
    these columns will be set a stream of 0.
    @type non_cols: numpy array/list/tuple, shape:(*)
    @param non_elements: the elements to be ignored. This parameter is to be an
    array of elements. Each element is represented by (row, col).
    @type non_elements: numpy array/list, shape:(*,2)
    @param mean_filter: indicates whether or not the mean is subtracted from
    data.
    @type mean_filter: boolean
    @param sum_filter: indicates how data should be filtered. The data is
    treated as a vector. This parameter can take values of None, 'array_sum',
    'col_sum', or 'row_sum'. None: data is not filtered. 'array_sum': the
    projection of the data along the sum of all data is filtered
    out. 'row_sum': the projection of data along its respective sum within a
    row is filtered out. 'col_sum': the projection of data along its respective
    sum within a column is filtered out.
    @type sum_filter: str '''
    for i in non_rows:
        data[i]=np.zeros(np.shape(data[0]))
    for j in non_cols:
        for row in data:
            row[j]=np.zeros(np.shape(row[0]))
    for index in non_elements:
        data[index[0]][index[1]]=np.zeros(np.shape(data[0][0]))
    if mean_filter==True:
        def subtract_mean(x, i):
            mean=np.mean(x)
            return x-mean
        data=arf.modify_array(data, subtract_mean, len(np.shape(data))-1)
    if sum_filter!=None:
        if sum_filter == 'array_sum':
            data=msf.sum_filter(data, equal_weight=True)
        elif sum_filter == 'row_sum':
            data=msf.sum_filter(data, 1, equal_weight=True)
        elif sum_filter == 'col_sum':
            data=msf.sum_filter(data, 0, equal_weight=True)
        else:
            raise ValueError ("The parameter sum_filter can only be None, 'array_sum', 'col_sum', or 'row_sum'.")
    return data

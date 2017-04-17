import matplotlib.pyplot as plt
import numpy as np
import filter
import code.common.arrayfunctions as arf
import code.common.functionanalyzer as fa
import code.common.multistreamfunctions as msf


class PointwiseProduct:
    '''Mainly used to calculate the Pointwise Product.
    @ivar data: data array that will be used in all functions. It is taken to
    be a 2 dimensional array (with row number the first dimension, and column
    number the second dimension) of data elements, where each data element is an
    array. Initialization filters it according to data_filter, and sets
    non_rows and non_cols to zeros. Initialization also normalizes each data
    element such that its euclidean norm is 1.
    @type data: numpy array, 3 dimensional
    @ivar non_rows: indicates which rows (first dimension of data) are to be
    ignored. All the data in these rows will be set to a stream of 0.
    @type non_rows: numpy array/list/tuple, shape:(*)
    @ivar non_cols: indicates which columns (second dimension of data) are to be
    ignored. All the data in these columns will be set to a stream of 0.
    @type non_cols: numpy array/list/tuple, shape:(*) 
    @ivar non_elements: indicates which detectors are to be ignored. All the
    data for these detectors will be set to a stream of 0. This parameter is an
    array of detectors, with each detector represented by (row, col).
    @type non_elements: numpy array/list, shape:(*,2)'''


    data=None
    non_rows=[]
    non_cols=[]
    non_elements=[]


    def __init__(self, data, non_rows=[], non_cols=[], non_elements=[],
                 sum_filter=None, normalize=True):
        '''Initializes the class. Sets self.data, self.non_rows, and
        self.non_cols.
        @param data: the input data. It is to be a 2 dimensional array (The
        first dimension is considered the row number, while the second dimenion
        is considered the column number.) of data elements, where each data
        element is an array.
        @type data: numpy array, 3 dimensions
        @param non_rows: indicates which rows (first dimension in data) should
        be ignored. Data elements in these rows will be set to a stream of 0.
        @type non_rows: numpy array/list/tuple, shape:(*)
        @param non_cols: indicates which columns (second dimension in data)
        should be ignored. Data elements in these columns will be set to a
        stream of 0.
        @type non_cols: numpy array/list/tuple, shape:(*)
        @param non_elements: indicates which detectors are to be ignored. All
        the data for these detectors will be set to a stream of 0. This
        parameter is to be an array of detectors, with each detector
        represented by (row, col).
        @type non_elements: numpy array/list, shape:(*,2)
        @param sum_filter: indicates how data should be filtered. This
        parameter can take values of None, 'array_sum', 'col_sum', or
        'row_sum'. None: data is not filtered. 'array_sum': the projection of
        the data along the sum of all data is filtered out. 'row_sum': the
        projection of data along its respective sum within a row is filtered
        out. 'col_sum': the projection of data along its respective sum within
        a column is filtered out.
        @type sum_filter: str 
        @param normalize: determines whether or not data is normalized. If set
        to True, the data will be normalized by dividing by its euclidean norm
        (root-sum-square)
        @type normalize: boolean '''
        data=filter.general_filter(data, non_rows=non_rows, non_cols=non_cols, 
                                   non_elements=non_elements,
                                   mean_filter=True, sum_filter=sum_filter)
        if normalize ==True:
            data=arf.modify_array(data, arf.wrap(arf.normalize), len(np.shape(data))-1)
        self.data=data
        self.non_rows=non_rows
        self.non_cols=non_cols
        self.non_elements=non_elements


    def standard_sum(self, axis=None):
        '''Finds the normalized pointwise sum of self.data.
        @return: an array of normalized pointwise sum. The resulting sum has a
        norm of 1.
        @rtype: numpy array
        @param axis: the axis to sum over. It is set to None by default, and
        when it is set to None, it will sum over all axis except the last.
        @type axis: int '''
        if axis!=None:
            sum_data=np.sum(self.data, axis)
            standardized_sum=arf.modify_array(sum_data, 
                                              arf.wrap(arf.standardize), 
                                              len(np.shape(sum_data))-1)
        else:
            sum_data=arf.sum_space_array_function(self.data, arf.wrap(np.sum), 
                                                  op_dim=1, 
                                                  op_ar_dim=len(np.shape(self.data))-1)
            standardized_sum=arf.standardize(sum_data)
        return standardized_sum


    def data_data_pointwise_product(self):
        '''Takes self.data and calculate every pointwise product.
        @return: an array of all the pointwise products of dimension
        (dim(self.data)-1)*(dim(self.data)-1). The first (dim(self.data)-1)
        dimensions specify the index first data element, and the second
        (dim(self.data)-1) dimensions specify the index of the second data
        element. The pointwise product (an inner product) of those two data
        element is calculated and placed in the corresponding index.
        @rtype: numpy array'''
        def normalize_pointwise_product(x, i):
            if i[0]>=i[2]:
                return np.sum(x[0]*x[1])
            else:
                return np.nan
        all_pointwise_product=arf.product_space_array_function((self.data,self.data), 
                                                               normalize_pointwise_product, 
                                                               (2,2))
        def reflect(x, i):
            if i[0]<i[2]:
                return all_pointwise_product[i[2]][i[3]][i[0]][i[1]]
            else:
                return x
        all_pointwise_product=arf.modify_array(all_pointwise_product, reflect, 4)
        return all_pointwise_product

    
    def sum_data_pointwise_product(self, axis=None):
        '''Calculates all the pointwise product of the sum of an axis against
        all the data.
        @return: an array of the pointwise products.
        @rtype: numpy array, 2 or 3 dimensional
        @param axis: indicate the axis to sum over. If axis is None, this
        function will sum over all but the last axis.
        @type axis: int '''
        standardized_sum=np.array(self.standard_sum(axis))
        def pointwise_product(x, i):
            return np.sum(x[0]*x[1])
        product_array=arf.product_space_array_function((standardized_sum, self.data),
                                                       pointwise_product, 
                                                       (len(standardized_sum.shape)-1,2))
        return np.array(product_array)


    def sum_sum_pointwise_product(self, axis1=None, axis2=None):
        '''Calculates all the pointwise product of the sum of data along axis1
        against the sum of data along axis2.
        @type axis1: int
        @type axis2: int '''
        standardized_sum_1=np.array(self.standard_sum(axis1))
        standardized_sum_2=np.array(self.standard_sum(axis2))
        def pointwise_product(x, i):
            return np.sum(x[0]*x[1])
        product_array=arf.product_space_array_function((standardized_sum_1, standardized_sum_2),
                                                       pointwise_product, 
                                                       (len(standardized_sum_1.shape)-1, len(standardized_sum_2.shape)-1))
        return np.array(product_array)


    def to_file(self, filename):
        '''Saves multiple arrays of pointwise product to a npz file. The arrays
        are placed into a NpzFile object, which is a dictionary of arrays. The
        arrays saved are named 'data_data', 'row_sum_data', 'col_sum_data',
        'array_sum_data', 'row_sum_row_sum, and 'col_sum_col_sum'.
        @param filename: the name of file where the arrays are to be saved.
        @type filename: str, end with '.npz' '''
        data_data_pointwise_product=np.transpose(self.data_data_pointwise_product(), (1,3,0,2))
        row_sum_data_pointwise_product=np.transpose(self.sum_data_pointwise_product(1),(0,2,1))
        col_sum_data_pointwise_product=np.transpose(self.sum_data_pointwise_product(0),(0,2,1))
        array_sum_data_pointwise_product=np.transpose(self.sum_data_pointwise_product(), (1,0))
        row_sum_row_sum_pointwise_product=self.sum_sum_pointwise_product(1,1)
        col_sum_col_sum_pointwise_product=self.sum_sum_pointwise_product(0,0)
        np.savez(filename, 
                 data_data=data_data_pointwise_product, 
                 row_sum_data=row_sum_data_pointwise_product, 
                 col_sum_data=col_sum_data_pointwise_product, 
                 array_sum_data=array_sum_data_pointwise_product, 
                 row_sum_row_sum=row_sum_row_sum_pointwise_product, 
                 col_sum_col_sum=col_sum_col_sum_pointwise_product)

    
    def analyze(self, index1, index2):
        '''Shows a graphical analysis of 2 time streams in self.data. The
        timestream to be shown is specified with index1 and index2. This
        function shows a graph of the timestreams and shows their
        normalized pointwise product.
        @type index1: numpy array/list/tuple, shape:(2)
        @type index2: numpy array/list/tuple, shape:(2)'''
        plt.figure()
        plt.title('Timestream of Col ' +str(index1[1]) + ' Row ' + str(index1[0]) 
                  + ' and Col ' + str(index2[1]) + ' Row ' + str(index2[0]))
        plt.xlabel('Time (Data Point Taken at 399 Hz)')
        plt.ylabel('Normalized Power')
        data1_mean=np.mean(self.data[index1[0]][index1[1]])
        data2_mean=np.mean(self.data[index2[0]][index2[1]])
        data1=self.data[index1[0]][index1[1]]-data1_mean
        data2=self.data[index2[0]][index2[1]]-data2_mean
        square_integral1_sqrt=np.sqrt(np.sum(data1*data1))
        square_integral2_sqrt=np.sqrt(np.sum(data2*data2))
        data1=data1/square_integral1_sqrt
        data2=data2/square_integral2_sqrt
        plt.plot(data1)
        plt.plot(data2)
        #plt.plot(find_base(data2))
        pointwise_product=np.sum(data1*data2)
        plt.figtext(0.39, 0.85, 'Normalized Pointwise Product: ' 
                    + str(pointwise_product))
        print pointwise_product


#end of class

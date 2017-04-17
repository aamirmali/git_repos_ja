import sys
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
import code.common.drawer as drawer
import code.common.arrayfunctions as arf
from code.common import exceptions

class SimilarityDrawer:
    '''Draws rectangles showing pointwise products.
    @ivar data_data_col_dom: The column dominated array of pointwise product
    between data and data; data_data_col_dom[i][j][k][l] is the pointwise
    product between the detector at column i and row k and the detector at
    column j and row l.
    @type data_data_col_dom: numpy array, 4 dimensional
    @ivar data_data_row_dom: The row dominated array of pointwise product
    between data and data; data_data_row_dom[i][j][k][l] is the pointwise
    product between the detector at column k and row i and the detector at
    column l and row j.
    @type data_data_row_dom: numpy array, 4 dimensional
    @ivar row_sum_data: An array of the pointwise product between the sum
    within rows and data; row_sum_data[i][j][k] is the pointwise product
    between the sum of all columns in row i with the detector at column j and
    row k.
    @type row_sum_data: numpy array, 3 dimensional
    @ivar col_sum_data: An array of the pointwise product between the sum
    within columns and data; col_sum_data[i][j][k] is the pointwise product
    between the sum of all rows in column i with the detector at column j and
    row k.
    @type col_sum_data: numpy array, 3 dimensional
    @ivar array_sum_data: An array of the pointwise product between the sum of
    all detectors and data; The value at index [i][j] is the pointwise product
    of the sum with the detector at column i and row j.
    @type array_sum_data: numpy array, 2 dimensional
    @ivar row_sum_row_sum: An array of the pointwise product between sum within
    rows and sum within rows.
    @type row_sum_row_sum: numpy array, 2 dimensional
    @ivar col_sum_col_sum: An array of the pointwise product between sum within
    columns and sum within columns.
    @type col_sum_col_sum: numpy array, 2 dimensional
    @ivar number_of_cols: the number of columns in the original data,
    including non columns
    @type number_of_cols: int
    @ivar number_of_rows: the number of rows in the original data,
    including non rows
    @type number_of_rows: int
    @ivar number_of_plotted_cols: the number of columns actually shown in
    plots. If cut_nons is true, the non_columns are not included; else, they
    are included.
    @type number_of_plotted_cols: int
    @ivar number_of_plotted_rows: the number of rows actually shown in
    plots. If cut_nons is true, the non_rows are not included; else, they are
    included.
    @type number_of_plotted_rows: int
    @ivar col_indices: maps the original column indices to the column indices
    after non_cols and cut_nons are taken into account. Inputted column indices
    will be converted with this array before they are passed into a
    function. If the ith value of this array is j, an inputted column index
    with a value of i will be converted to j.  A column that is in non_cols
    will be converted to -1.
    @type col_indices: numpy array, shape:(*)
    @ivar row_indices: maps the original row indices to the row indices after
    non_rows and cut_nons are taken into account. Inputted row indices will be
    converted with this array before they are passed into a function. If the
    ith value of this array is j, an inputed row index with a value of i will
    be converted to j.  A row that is in non_rows will be converted to -1.
    @type row_indices: numpy array, shape:(*)
    @ivar inverse_col_indices: the map from the plotted column indices to the
    column indices in the original data. If the ith value of this array is j,
    then the ith plotted column is the jth column in the original data.
    @type inverse_col_indices: numpy array, shape:(*)
    @ivar inverse_row_indices: the map from the plotted row indices to the row
    indices in the original data. If the ith value of this array is j, then the
    ith plotted row is the jth row in the original data.
    @type inverse_row_indices: numpy array, shape:(*)
    @ivar non_cols: indicates the columns to be ignored. The data in these
    columns will not be shown, and will not be included in any calculations.
    @type non_cols: sorted list, shape:(*)
    @ivar non_rows: indicates the rows to be ignored. The data in these rows
    will not be shown, and will not be included in any calculations.
    @type non_rows: sorted list, shape:(*)
    @ivar non_detectors: indicates the detectors to be ignored. The data in
    these detectors will not be shown, and will not be included in any
    calculations. This parameter is an array of detectors, with each detector
    represented by (col, row).
    @type non_detectors: sorted list, shape:(*,2)
    @ivar data_data_limit: the default colour limit for data_data. In any
    functions that plots data_data, any pointwise product outside of this range
    will be shown at the respective limits if the parameter limit is set to
    'class'.
    @type data_data_limit: tuple, shape:(2)
    @ivar row_sum_data_limit: the default colour limit for row_sum_data. In any
    functions that plots row_sum_data, any pointwise product outside of this
    range will be shown at the respective limits if the parameter limit is set
    to 'class'.
    @type row_sum_data_limit: tuple, shape:(2)
    @ivar col_sum_data_limit: the default colour limit for col_sum_data. In any
    functions that plots col_sum_data, any pointwise product outside of this
    range will be shown at the respective limits if the parameter limit is set
    to 'class'.
    @type col_sum_data_limit: tuple, shape:(2)
    @ivar array_sum_data_limit: the default colour limit for array_sum_data. In
    any functions that plots array_sum_data, any pointwise product outside of
    this range will be shown at the respective limits if the parameter limit is
    set to 'class'.
    @type array_sum_data_limit: tuple, shape:(2)
    @ivar row_sum_row_sum_limit: the default colour limit for
    row_sum_row_sum. In any functions that plots row_sum_row_sum, any pointwise
    product outside of this range will be shown at the respective limits if the
    parameter limit is set to 'class'.
    @type row_sum_row_sum_limit: tuple, shape:(2)
    @ivar col_sum_col_sum_limit: the default colour limit for
    col_sum_col_sum. In any functions that plots col_sum_col_sum, any pointwise
    product outside of this range will be shown at the respective limits if the
    parameter limit is set to 'class'.
    @type col_sum_col_sum_limit: tuple, shape:(2) '''


    data_data_col_dom=None
    data_data_row_dom=None
    row_sum_data=None
    col_sum_data=None
    array_sum_data=None
    row_sum_row_sum=None
    col_sum_col_sum=None
    number_of_cols=None
    number_of_rows=None
    number_of_plotted_cols=None
    number_of_plotted_rows=None
    col_indices=np.array([])
    row_indices=np.array([])
    inverse_col_indices=np.array([])
    inverse_row_indices=np.array([])
    non_cols=[]
    non_rows=[]
    non_detectors=[]
    data_data_limit=[]
    row_sum_data_limit=[]
    col_sum_data_limit=[]
    array_sum_data_limit=[]
    row_sum_row_sum_limit=[]
    col_sum_col_sum_limit=[]


    def __init__(self, npzdict, 
                 non_cols=[], non_rows=[], non_detectors=[], cut_nons=False, 
                 class_limit=None, data_data_limit=[], row_sum_data_limit=[], 
                 col_sum_data_limit=[], array_sum_data_limit=[], 
                 row_sum_row_sum_limit=[], col_sum_col_sum_limit=[]):
        '''Initializes the class. 
        @param npzdict: the NpzFile object that contains the required data. The
        object is to be a dictionary containing arrays with keyword
        'data_data', 'row_sum_data', 'col_sum_data', 'array_sum_data',
        'row_sum_row_sum', and 'col_sum_col_sum'.
        @type npzdict: Npzfile/Dictionary
        @param non_cols: indicates the cols to be ignored. The data in these
        columns will not be shown and will not be considered in calculations.
        @type non_cols: numpy array/list/tuple, shape:(*)       
        @param non_rows: indicates the rows to be ignored. The data in these
        rows will not be shown and will not be considered in calculations.
        @type non_rows: numpy array/list/tuple, shape:(*)
        @param non_detectors: indicates the detectors to be ignored. The data in
        these detectors will not be shown and will not be included in any
        calculations.  This parameter is to be an array of detectors, with each
        detector represented by (col, row).
        @type non_detectors: numpy array/list, shape:(*,2)
        @param cut_nons: if this parameter is set to True, the data in non_rows
        and non_cols will be removed from the data. If it is set to False, the
        data will be set to NaN, and will be shown as white spaces in plots.
        @type cut_nons: boolean
        @param class_limit: The overarching limit for the class. All other
        class limit parameters, if not specified, will be set to this
        limit. This parameter can be None, 'full', 'non_auto', 'inliers' or (x,
        y). None: limit is not set. 'full': limit is set to (min of data_data,
        max of data_data). 'non_auto': the limit is set to (min of data_data,
        max of data_data) with the pointwise product between the same detector
        removed. 'inliers' the limit is set to (min of data_data, max of
        data_data) with outliers removed. (x, y): the limit is set to (x, y).
        @type class_limit: str; numpy array/list/tuple, shape:(2)
        @param data_data_limit: sets the value of self.data_data_limit
        @type data_data_limit: numpy array/list/tuple, shape:(2) 
        @param row_sum_data_limit: sets the value of self.row_sum_data_limit
        @type row_sum_data_limit: numpy array/list/tuple, shape:(2)
        @param col_sum_data_limit: sets the value of self.col_sum_data_limit
        @type col_sum_data_limit: numpy array/list/tuple, shape:(2)
        @param array_sum_data_limit: sets the value of
        self.array_sum_data_limit
        @type array_sum_data_limit: numpy array/list/tuple, shape:(2)
        @param row_sum_row_sum_limit: sets the value of
        self.row_sum_row_sum_limit
        @type row_sum_row_sum_limit: numpy array/list/tuple, shape:(2)
        @param col_sum_col_sum_limit: sets the value of
        self.col_sum_col_sum_limit
        @type col_sum_col_sum_limit: numpy array/list/tuple, shape:(2) '''
        try:
            self.data_data_col_dom=npzdict['data_data']
            self.row_sum_data=npzdict['row_sum_data']
            self.col_sum_data=npzdict['col_sum_data']
            self.array_sum_data=npzdict['array_sum_data']
            self.row_sum_row_sum=npzdict['row_sum_row_sum']
            self.col_sum_col_sum=npzdict['col_sum_col_sum']
        except KeyError as message:
            raise KeyError('The data dictionary does not have all the required arrays.\n' + str(message)) 
        non_cols=sorted(set(non_cols))
        non_rows=sorted(set(non_rows))
        non_detectors=sorted(set(non_detectors))
        self.cut_nons=cut_nons
        self.non_cols=non_cols
        self.non_rows=non_rows
        self.non_detectors=non_detectors
        number_of_cols=npzdict['data_data'].shape[0]
        number_of_rows=npzdict['data_data'].shape[2]
        self.set_indices_and_length(number_of_cols, number_of_rows, non_cols, non_rows, cut_nons)
        self.erase(non_cols, non_rows, non_detectors, cut_nons)
        self.set_class_limits(class_limit, data_data_limit, 
                              row_sum_data_limit,col_sum_data_limit, 
                              array_sum_data_limit, 
                              row_sum_row_sum_limit, col_sum_col_sum_limit)
        self.data_data_row_dom=np.transpose(self.data_data_col_dom,(2,3,0,1))


    def set_indices_and_length(self, number_of_cols, number_of_rows, non_cols=[], non_rows=[], cut_nons=False):
        '''Class internal method. Sets self.number_of_cols,
        self.number_of_rows, self.number_of_plotted_cols,
        self.number_of_plotted_rows, self.col_indices, self.row_indices,
        self.inverse_col_indices, and self.inverse_row_indices.
        @see: class variables'''
        if cut_nons==False:
            number_of_plotted_cols=number_of_cols
            number_of_plotted_rows=number_of_rows
            col_indices=np.arange(0, number_of_cols)
            for col in non_cols:
                col_indices[col]=-1
            row_indices=np.arange(0, number_of_rows)
            for row in non_rows:
                row_indices[row]=-1
            inverse_col_indices=np.arange(0, number_of_cols)
            inverse_row_indices=np.arange(0, number_of_rows)
        else:
            number_of_plotted_cols=number_of_cols-len(non_cols)
            number_of_plotted_rows=number_of_rows-len(non_rows)
            col_indices=np.empty((number_of_cols), dtype=np.int32)
            col_index=0
            non_col_index=0
            for i in range(0, col_indices.shape[0]):
                if non_col_index<len(non_cols) and i==non_cols[non_col_index]:
                    col_indices[i]=-1
                    non_col_index+=1
                else:
                    col_indices[i]=col_index
                    col_index+=1
            row_indices=np.empty((number_of_rows), dtype=np.int32)
            row_index=0
            non_row_index=0
            for i in range(0, row_indices.shape[0]):
                if non_row_index<len(non_rows) and i==non_rows[non_row_index]:
                    row_indices[i]=-1
                    non_row_index+=1
                else:
                    row_indices[i]=row_index
                    row_index+=1
            inverse_col_indices=np.empty((number_of_plotted_cols), dtype=np.int32)
            for i in range(0, col_indices.shape[0]):
                if col_indices[i]!=-1:
                    inverse_col_indices[col_indices[i]]=i
            inverse_row_indices=np.empty((number_of_plotted_rows), dtype=np.int32)
            for i in range(0, row_indices.shape[0]):
                if row_indices[i]!=-1:
                    inverse_row_indices[row_indices[i]]=i
        self.number_of_cols=number_of_cols
        self.number_of_rows=number_of_rows
        self.number_of_plotted_cols=number_of_plotted_cols
        self.number_of_plotted_rows=number_of_plotted_rows
        self.col_indices=col_indices
        self.row_indices=row_indices
        self.inverse_col_indices=inverse_col_indices
        self.inverse_row_indices=inverse_row_indices


    def erase(self, non_cols=[], non_rows=[], non_detectors=[], cut_nons=False):
        '''Class internal method. Removes non_cols, non_rows, and non_detectors.
        @see: __init__ and class variables '''
        if non_detectors!=[]:
            data_data=np.transpose(self.data_data_col_dom, (0,2,1,3))
            for index in non_detectors:
                data_data[index[0]][index[1]]=arf.create((data_data[0][0].shape), 
                                                         np.nan)
            data_data=np.transpose(data_data, (2,3,0,1))
            for index in non_detectors:
                data_data[index[0]][index[1]]=arf.create((data_data[0][0].shape), 
                                                         np.nan)
            self.data_data_col_dom=np.transpose(data_data, (0,2,1,3))
            for index in non_detectors:
                for data in self.row_sum_data:
                    data[index[0]][index[1]]=np.nan
                for data in self.col_sum_data:
                    data[index[0]][index[1]]=np.nan
                self.array_sum_data[index[0]][index[1]]=np.nan
        if cut_nons==False:
            if non_cols!=[]:
                def data_data_col_delete(x, i):
                    if i[0] in non_cols or i[1] in non_cols:
                        return arf.create(np.shape(x), np.nan)
                    else:
                        return x
                self.data_data_col_dom=arf.modify_array(self.data_data_col_dom, 
                                                        data_data_col_delete, 2)
                def row_sum_data_col_delete(x, i):
                    if i[1] in non_cols:
                        return arf.create(np.shape(x), np.nan)
                    else:
                        return x
                self.row_sum_data=arf.modify_array(self.row_sum_data, 
                                                   row_sum_data_col_delete, 2)
                def col_sum_data_col_delete(x, i):
                    if i[0] in non_cols or i[1] in non_cols:
                        return arf.create(np.shape(x), np.nan)
                    else:
                        return x
                self.col_sum_data=arf.modify_array(self.col_sum_data, 
                                                   col_sum_data_col_delete, 2)       
                def array_sum_data_col_delete(x, i):
                    if i[0] in non_cols:
                        return arf.create(np.shape(x), np.nan)
                    else:
                        return x
                self.array_sum_data=arf.modify_array(self.array_sum_data, 
                                                     array_sum_data_col_delete, 1) 
                def col_sum_col_sum_col_delete(x, i):
                    if i[0] in non_cols or i[1] in non_cols:
                        return np.nan
                    else:
                        return x
                self.col_sum_col_sum=arf.modify_array(self.col_sum_col_sum, 
                                                      col_sum_col_sum_col_delete, 2)
            if non_rows!=[]:
                def data_data_row_delete(x, i):
                    if i[2] in non_rows or i[3] in non_rows:
                        return np.nan
                    else:
                        return x 
                self.data_data_col_dom=arf.modify_array(self.data_data_col_dom, 
                                                        data_data_row_delete, 4)
                def row_sum_data_row_delete(x, i):
                    if i[0] in non_rows or i[2] in non_rows:
                        return np.nan
                    else:
                        return x
                self.row_sum_data=arf.modify_array(self.row_sum_data, 
                                                   row_sum_data_row_delete, 3)
                def col_sum_data_row_delete(x, i):
                    if i[2] in non_rows:
                        return np.nan
                    else:
                        return x
                self.col_sum_data=arf.modify_array(self.col_sum_data, 
                                                   col_sum_data_row_delete, 3)           
                def array_sum_data_row_delete(x, i):
                    if i[1] in non_rows:
                        return np.nan
                    else:
                        return x
                self.array_sum_data=arf.modify_array(self.array_sum_data, 
                                                     array_sum_data_row_delete, 2) 
                def row_sum_row_sum_row_delete(x, i):
                    if i[0] in non_rows or i[1] in non_rows:
                        return np.nan
                    else:
                        return x
                self.row_sum_row_sum=arf.modify_array(self.row_sum_row_sum, 
                                                      row_sum_row_sum_row_delete, 2)
        else:
            if non_cols!=[]:
                self.data_data_col_dom=np.delete(self.data_data_col_dom, non_cols, 0)
                self.data_data_col_dom=np.delete(self.data_data_col_dom, non_cols, 1)
                self.row_sum_data=np.delete(self.row_sum_data, non_cols, 1)
                self.col_sum_data=np.delete(self.col_sum_data, non_cols, 0)
                self.col_sum_data=np.delete(self.col_sum_data, non_cols, 1)
                self.array_sum_data=np.delete(self.array_sum_data, non_cols, 0)
                self.col_sum_col_sum=np.delete(self.col_sum_col_sum, non_cols, 0)
                self.col_sum_col_sum=np.delete(self.col_sum_col_sum, non_cols, 1)
            if non_rows!=[]:
                self.data_data_col_dom=np.delete(self.data_data_col_dom, non_rows, 2)
                self.data_data_col_dom=np.delete(self.data_data_col_dom, non_rows, 3)
                self.row_sum_data=np.delete(self.row_sum_data, non_rows, 0)
                self.row_sum_data=np.delete(self.row_sum_data, non_rows, 2)
                self.col_sum_data=np.delete(self.col_sum_data, non_rows, 2)
                self.array_sum_data=np.delete(self.array_sum_data, non_rows, 1)
                self.row_sum_row_sum=np.delete(self.row_sum_row_sum, non_rows, 0)
                self.row_sum_row_sum=np.delete(self.row_sum_row_sum, non_rows, 1)


    def set_class_limits(self, class_limit=None, data_data_limit=[], 
                         row_sum_data_limit=[], col_sum_data_limit=[], 
                         array_sum_data_limit=[], 
                         row_sum_row_sum_limit=[], col_sum_col_sum_limit=[]):
        '''Class internal Function. Sets the class limit parameters. 
        @see: __init__ and class variables'''
        if class_limit!=None:
            if class_limit=='full':
                class_limit=(np.nanmin(self.data_data_col_dom), 
                             np.nanmax(self.data_data_col_dom))
            elif class_limit=='non_auto':
                def erase_auto(x, i):
                    if i[0]==i[1] and i[2]==i[3]:
                        return np.nan
                    else:
                        return x
                non_auto_data=arf.modify_array(self.data_data_col_dom, 
                                               erase_auto, 4)
                class_limit=(np.nanmin(non_auto_data), np.nanmax(non_auto_data))
            elif class_limit=='inliers':
                Q1=scipy.stats.scoreatpercentile(self.data_data_col_dom.flat, 25,
                                                 limit=(-np.inf, np.inf))
                Q3=scipy.stats.scoreatpercentile(self.data_data_col_dom.flat, 75, 
                                                 limit=(-np.inf, np.inf))
                iqr=Q3-Q1
                def erase_outliers(x, i):
                    if x>1.5*iqr+Q3 or x<Q1-1.5*iqr:
                        return 0
                    else:
                        return x
                inliers=arf.modify_array(self.data_data_col_dom, erase_outliers, 4)
                class_limit=(np.nanmin(inliers), np.nanmax(inliers))
            elif type(class_limit)!=str:
                    class_limit=class_limit
            else:
                print 'Input string for parameter limit is invalid.'
                class_limit=[]
        if data_data_limit!=[]:
            self.data_data_limit=data_data_limit
        if row_sum_data_limit!=[]:
            self.row_sum_data_limit=row_sum_data_limit        
        if col_sum_data_limit!=[]:
            self.col_sum_data_limit=col_sum_data_limit        
        if array_sum_data_limit!=[]:
            self.array_sum_data_limit=array_sum_data_limit
        if row_sum_row_sum_limit!=[]:
            self.row_sum_row_sum_limit=row_sum_row_sum_limit
        if col_sum_col_sum_limit!=[]:
            self.col_sum_col_sum_limit=col_sum_col_sum_limit
        if data_data_limit==[]:
            self.data_data_limit=class_limit
        if row_sum_data_limit==[]:
            self.row_sum_data_limit=class_limit
        if col_sum_data_limit==[]:
            self.col_sum_data_limit=class_limit
        if array_sum_data_limit==[]:
            self.array_sum_data_limit=class_limit
        if row_sum_row_sum_limit==[]:
            self.row_sum_row_sum_limit=class_limit
        if col_sum_col_sum_limit==[]:
            self.col_sum_col_sum_limit=class_limit


    def plot_single_block(self, index1, index2, function=None, limit='class', colorbar=True, dominance='column'):
        '''Plots a single block of the pointwise product. The block is either a
        whole column crossed with another whole column or a whole row crossed
        with another whole row depending on dominance. The column or row to be
        crossed is specified with index1 and index2.
        @type index1: int
        @type index2: int
        @param function: a function to be applied to each pointwise product.
        @type function: function(element, index)
        @param limit: sets the colour limit. If an element is outside of the
        limit, it will be set to the respective limit.This parameter can be
        None, 'class', 'non_auto', or (x,y). None: no limit is set. 'class':
        the limit is set to self.data_data_limit. 'non_auto': the limit is set
        to (min in the block, max in the block) with the main diagonals
        removed. (x,y): limit is set to (x,y).
        @type limit: str; numpy array/list/tuple, shape:(*)
        @param colorbar: indicates whether or not a colorbar is shown.
        @type colorbar: boolean
        @param dominance: indicates whether a block is a whole column crossed 
        with another whole column or a whole row crossed with another whole
        row. This parameter can be 'column' or 'row'.
        @type dominance: str '''
        if dominance == 'column':
            if self.col_indices[index1]!=-1 and self.col_indices[index2]!=-1:
                title= ('Normalized Pointwise Products of Rows of Col ' 
                        + str(index1) + ' with Rows of Col ' + str (index2))
                ylabel= 'Rows of Col ' +str(index1)
                xlabel= 'Rows of Col ' +str(index2)
                data=self.data_data_col_dom[self.col_indices[index1]][self.col_indices[index2]]
                def format(x, i):
                    return self.inverse_row_indices[x]
            else:
                raise exceptions.ExistenceError('One of the columns is a non column.')
        elif dominance == 'row':
            if self.row_indices[index1]!=-1 and self.row_indices[index2]!=-1:
                title= ('Normalized Pointwise Products of Cols of Row ' 
                        + str(index1) + ' with Cols of Row ' + str (index2))
                ylabel= 'Cols of Row ' +str(index1)
                xlabel= 'Cols of Row ' +str(index2)
                data=self.data_data_row_dom[self.row_indices[index1]][self.row_indices[index2]]
                def format(x, i):
                    return self.inverse_col_indices[x]
            else:
                raise exceptions.ExistenceError('One of the rows is a non row.')
        else:
            raise ValueError("The parameter dominance can only be 'column' or 'row'")
        colorbar_label = 'Normalized Pointwise Product'
        if limit!=None:
            if limit=='class':
                limit=self.data_data_limit
            elif limit=='non_auto':
                def erase_auto(x, i):
                    if i[0]==i[1]:
                        return np.nan
                    else:
                        return x
                non_auto_data=arf.modify_array(data, erase_auto, 2)
                limit=[np.nanmin(non_auto_data), np.nanmax(non_auto_data)]
            elif type(limit)==str:
                raise ValueError ('Invalid input for parameter limit')
        drawer.draw_image(data, title=title, xlabel=xlabel, ylabel=ylabel, 
                          function=function, limit=limit, 
                          colorbar=colorbar, colorbar_label=colorbar_label)
        drawer.set_ticks(plt.gca(), format, format, 1, 1)
    

    def plot_data_data(self, function=None, limit='class', colorbar=True, 
                       dominance='column'):
        '''Plots all the data as a 2 dimensional array. if the data is an array
        of shape (m,n,o,p), it is plotted as a shape(m*o, n*p)
        array. Data[i][j][k][l] is plotted at point [i*(m-1)+j][k*(n-1)+l]. The
        data is drawn as a 2 dimensional array of 2 dimensional arrays.
        @param function: a function to be applied to each pointwise product.
        @type function: function(element, index)
        @param limit: sets the colour limit. If an element is outside of the
        limit, it will be set to the respective limit.This parameter can be
        None, 'class', 'non_auto', or (x,y). None: no limit is set. 'class':
        the limit is set to self.data_data_limit. 'non_auto': the limit is set
        to (min in the block, max in the block) with the main diagonals
        removed. (x,y): limit is set to (x,y).
        @type limit: str; numpy array/list/tuple, shape:(*)
        @param colorbar: indicates whether or not a colorbar is shown.
        @type colorbar: boolean
        @param dominance: indicates whether a large block is column crossed
        with column or row crossed with row. This parameter can be 'column' or
        'row'. 'column': data_data_col_dom is used for data. Big blocks
        represent columns crossed with columns 'row': data_data_row_dom is used
        for data. Big blocks represent rows crossed with rows.
        @type dominance: str '''
        if dominance == 'column':
            title= 'Column Dominated Pointwise Product of All Data'
            xlabel = 'Col'
            ylabel = 'Col'
            data=np.transpose(self.data_data_col_dom,(0,2,1,3))
            def format(x, i):
                plotted_col_index=int(int(x)/self.number_of_plotted_rows)
                return self.inverse_col_indices[plotted_col_index]
            tick_factor=self.number_of_plotted_rows
        elif dominance == 'row':
            title= 'Row Dominated Pointwise Product of All Data'
            xlabel = 'Row'
            ylabel = 'Row'
            data=np.transpose(self.data_data_row_dom,(0,2,1,3))
            def format(x, i):
                plotted_row_index=int(int(x)/self.number_of_plotted_cols)
                return self.inverse_row_indices[plotted_row_index]
            tick_factor=self.number_of_plotted_cols
        else:
            raise ValueError("The parameter dominance can only be 'column' or 'row'")
        colorbar_label= 'Normalized Pointwise Product'
        size=np.shape(data)[0]*np.shape(data)[1]
        data=data.reshape((size,size))
        if limit!=None:
            if limit=='class':
                limit=self.data_data_limit
            elif limit=='non_auto':
                def erase_auto(x, i):
                    if i[0]==i[1]:
                        return np.nan
                    else:
                        return x
                non_auto_data=arf.modify_array(data, erase_auto, 2)
                limit=[np.nanmin(non_auto_data), np.nanmax(non_auto_data)]
            elif type(limit)==str:
                raise ValueError ('Invalid input for parameter limit')
        drawer.draw_image(data, title=title, xlabel=xlabel, ylabel=ylabel, 
                          function=function, limit=limit, 
                          colorbar=colorbar, colorbar_label=colorbar_label)
        drawer.set_ticks(plt.gca(), format, format, tick_factor, tick_factor)

    
    def plot_data_data_average(self, function=None, limit='class', 
                               colorbar=True, dominance='column'):        
        '''For each i, and j, takes the average of the array data[i][j], and
        plots it.
        @param function: a function to be applied to each average.
        @type function: function(element, index)
        @param limit: sets the colour limit. If an element is outside of the
        limit, it will be set to the respective limit.This parameter can be
        None, 'class', or (x,y). None: no limit is set. 'class': the limit is
        set to self.data_data_limit. 'non_auto': the limit is set
        to (min in the average, max in the average) with the main diagonals
        removed. (x,y): limit is set to (x,y).
        @type limit: str; numpy array/list/tuple, shape:(*)
        @param colorbar: indicates whether or not a colorbar is shown.
        @type colorbar: boolean
        @param dominance: indicates whether a whole column crossed with another
        whole column is averaged or whether a whole row crossed with another
        whole row is averaged. This parameter can be 'column' or
        'row'. 'column': data_data_col_dom is used for data. Whole column
        crossed with another whole column is averaged.  'row':
        data_data_row_dom is used for data. Big blocks represent rows crossed
        with rows. Whole row crossed with another whole row is averaged.
        @type dominance: str '''
        def nanmean(x, i):
            return scipy.stats.nanmean(x.flat)
        if dominance == 'column':
            title= 'Average Pointwise Product of All Rows in Each Column'
            xlabel = 'Col'
            ylabel = 'Col'
            average_array=arf.modify_array(self.data_data_col_dom, nanmean, 2)
            def format(x, i):
                return self.inverse_col_indices[x]
        elif dominance == 'row':
            title= 'Average Pointwise Product of All Cols in Each Row'
            xlabel = 'Row'
            ylabel = 'Row'
            average_array=arf.modify_array(self.data_data_row_dom, nanmean, 2)
            def format(x, i):
                return self.inverse_row_indices[x]
        else:
            raise ValueError("the parameter dominance can only be 'column' or 'row'")
        colorbar_label= 'Average Normalized Pointwise Product'
        if limit!=None:
            if limit=='class':
                limit=self.data_data_limit
            elif limit=='non_auto':
                def erase_auto(x, i):
                    if i[0]==i[1]:
                        return np.nan
                    else:
                        return x
                non_auto_data=arf.modify_array(average_array, erase_auto, 2)
                limit=[np.nanmin(non_auto_data), np.nanmax(non_auto_data)]
            elif type(limit)==str:
                raise ValueError ('Invalid input for parameter limit')
        drawer.draw_image(average_array, title=title, xlabel=xlabel, ylabel=ylabel, 
                          function=function, limit=limit, 
                          colorbar=colorbar, colorbar_label=colorbar_label)
        drawer.set_ticks(plt.gca(), format, format, 1, 1)

        
    def plot_row_sum_row_data(self, row_sum_row_num, function=None, 
                              limit='class', colorbar=True):
        '''Plots the sum of a row crossed with all of data.
        @param row_sum_row_num: indicates which row's sum is crossed with all
        of data.
        @type row_sum_row_num: int
        @param function: a function to be applied to each average.
        @type function: function(element, index)
        @param limit: sets the colour limit. If an element is outside of the
        limit, it will be set to the respective limit.This parameter can be
        None, 'class', or (x,y). None: no limit is set. 'class': the limit is
        set to self.row_sum_data_limit. (x,y): limit is set to (x,y).
        @type limit: str; numpy array/list/tuple, shape:(*)
        @param colorbar: indicates whether or not a colorbar is shown.
        @type colorbar: boolean '''
        if self.row_indices[row_sum_row_num]!=-1:
            title= ('Pointwise Product of Sum of all Cols in Row ' 
                    + str(row_sum_row_num) + ' with Data')
            xlabel = 'Row'
            ylabel = 'Col'
            colorbar_label='Normalized Pointwise Product'
            data=self.row_sum_data[self.row_indices[row_sum_row_num]]
        else:
            raise exceptions.ExistenceError('The specified row is a non row.')
        def xformat(x, i):
            return self.inverse_row_indices[x]
        def yformat(x, i):
            return self.inverse_col_indices[x]
        if limit!=None:
            if limit=='class':
                limit=self.row_sum_data_limit
            elif type(limit)==str:
                raise ValueError ('Invalid input for parameter limit')
        drawer.draw_image(data, title=title, xlabel=xlabel, ylabel=ylabel, 
                          function=function, limit=limit, 
                          colorbar=colorbar, colorbar_label=colorbar_label)
        drawer.set_ticks(plt.gca(), xformat, yformat, 1, 1)

    
    def plot_row_sum_data(self, function=None, limit='class', colorbar=True):
        '''Plots the pointwise product of every row's sum against all of
        data. The data is displayed as large blocks ordered horizontally. The
        ith block is the pointwise product of the sum of the ith row with all
        of data.
        @param function: a function to be applied to each data element.
        @type function: function(element, index)
        @param limit: sets the colour limit. If an element is outside of the
        limit, it will be set to the respective limit.This parameter can be
        None, 'class', or (x,y). None: no limit is set. 'class': the limit is
        set to self.row_sum_data_limit. (x,y): limit is set to (x,y).
        @type limit: str; numpy array/list/tuple, shape:(*)
        @param colorbar: indicates whether or not a colorbar is shown.
        @type colorbar: boolean '''
        title='Pointwise Product of Sum of all Cols in Rows with Data'
        xlabel = 'Sum of all Columns in Row'
        ylabel = 'Col'
        colorbar_label='Normalized Pointwise Product'
        data=np.transpose(self.row_sum_data,(1,0,2))
        xlength=data.shape[1]*data.shape[2]
        ylength=data.shape[0]
        data=data.reshape(ylength, xlength)
        def xformat(x, i):
            plotted_row_sum_row_num=int(int(x)/self.number_of_plotted_rows)
            return self.inverse_row_indices[plotted_row_sum_row_num]
        xtick_factor = self.number_of_plotted_rows
        def yformat(x, i):
            return self.inverse_col_indices[x]
        if limit!=None:
            if limit=='class':
                limit=self.row_sum_data_limit
            elif type(limit)==str:
                raise ValueError ('Invalid input for parameter limit')
        drawer.draw_image(data, title=title, xlabel='', ylabel=ylabel, 
                          function=function, limit=limit, 
                          colorbar=colorbar, colorbar_label=colorbar_label)
        drawer.set_ticks(plt.gca(), xformat, yformat, xtick_factor, 1)


    def plot_col_sum_col_data(self, col_sum_col_num, function=None, 
                              limit='class', colorbar=True):
        '''Plots the sum of a column crossed with all of data.
        @param col_sum_col_num: indicates which column's sum is crossed with
        all of data.
        @type col_sum_col_num: int
        @param function: a function to be applied to each data element.
        @type function: function(element, index)
        @param limit: sets the colour limit. If an element is outside of the
        limit, it will be set to the respective limit.This parameter can be
        None, 'class', or (x,y). None: no limit is set. 'class': the limit is
        set to self.col_sum_data_limit. (x,y): limit is set to (x,y).
        @type limit: str; numpy array/list/tuple, shape:(*)
        @param colorbar: indicates whether or not a colorbar is shown.
        @type colorbar: boolean '''
        if self.col_indices[col_sum_col_num]!=-1:
            title= ('Pointwise Product of Sum of all Rows in Col ' 
                    + str(col_sum_col_num) + ' with Data')
            xlabel = 'Row'
            ylabel = 'Col'
            colorbar_label='Normalized Pointwise Product'
            data=self.col_sum_data[self.col_indices[col_sum_col_num]]
        else:
            raise exceptions.ExistenceError('The specified column does not exist')
        def xformat(x, i):
            return self.inverse_row_indices[x]
        def yformat(x, i):
            return self.inverse_col_indices[x]
        if limit!=None:
            if limit=='class':
                limit=self.col_sum_data_limit
            elif type(limit)==str:
                raise ValueError ('Invalid input for parameter limit')
        drawer.draw_image(data, title=title, xlabel=xlabel, ylabel=ylabel, 
                          function=function, limit=limit, 
                          colorbar=colorbar, colorbar_label=colorbar_label)
        drawer.set_ticks(plt.gca(), xformat, yformat, 1, 1)


    def plot_col_sum_data(self, function=None, limit='class', colorbar=True):
        '''Plots the pointwise product of every column's sum against all of
        data. The data is displayed as large blocks ordered vertically. The ith
        block is the pointwise product of the sum of the ith column with all of
        data.
        @param function: a function to be applied to each data element.
        @type function: function(element, index)
        @param limit: sets the colour limit. If an element is outside of the
        limit, it will be set to the respective limit.This parameter can be
        None, 'class', or (x,y). None: no limit is set. 'class': the limit is
        set to self.col_sum_data_limit. (x,y): limit is set to (x,y).
        @type limit: str; numpy array/list/tuple, shape:(*)
        @param colorbar: indicates whether or not a colorbar is shown.
        @type colorbar: boolean '''
        title='Pointwise Product of Sum of all Rows in Cols with Data'
        xlabel = 'Row'
        ylabel = 'Sum of all Rows in Col'
        colorbar_label='Normalized Pointwise Product'
        data=self.col_sum_data
        xlength=data.shape[2]
        ylength=data.shape[0]*data.shape[1]
        data=data.reshape(ylength, xlength)
        def xformat(x, i):
            return self.inverse_row_indices[x]
        def yformat(x, i):
            plotted_col_sum_col_num=int(int(x)/self.number_of_plotted_cols)
            return self.inverse_col_indices[plotted_col_sum_col_num]
        ytick_factor=self.number_of_plotted_cols
        if limit!=None:
            if limit=='class':
                limit=self.col_sum_data_limit
            elif type(limit)==str:
                raise ValueError ('Invalid input for parameter limit')
        drawer.draw_image(data, title=title, xlabel=xlabel, ylabel='', 
                          function=function, limit=limit, 
                          colorbar=colorbar, colorbar_label=colorbar_label)
        drawer.set_ticks(plt.gca(), xformat, yformat, 1, ytick_factor)

        
    def plot_array_sum_data(self, function=None, limit='class', colorbar=True):
        '''plots the pointwise product of the sum all the detectors against all
        the detectors. 
        @param function: a function to be applied to each data element.
        @type function: function(element, index)
        @param limit: sets the colour limit. If an element is outside of the
        limit, it will be set to the respective limit.This parameter can be
        None, 'class', or (x,y). None: no limit is set. 'class': the limit is
        set to self.array_sum_data_limit. (x,y): limit is set to (x,y).
        @type limit: str; numpy array/list/tuple, shape:(*)
        @param colorbar: indicates whether or not a colorbar is shown.
        @type colorbar: boolean '''
        title = 'Pointwise Product of Sum of All Data with Data'
        xlabel='Row'
        ylabel='Col'
        colorbar_label='Normalized Pointwise Product'
        def xformat(x, i):
            return self.inverse_row_indices[x]
        def yformat(x, i):
            return self.inverse_col_indices[x]
        if limit!=None:
            if limit=='class':
                limit=self.array_sum_data_limit
            elif type(limit)==str:
                raise ValueError ('Invalid input for parameter limit')
        drawer.draw_image(self.array_sum_data, title=title, 
                          xlabel=xlabel, ylabel=ylabel, 
                          function=function, limit=limit, 
                          colorbar=colorbar, colorbar_label=colorbar_label)
        drawer.set_ticks(plt.gca(), xformat, yformat, 1, 1)


    def plot_row_sum_row_sum(self, function=None, limit='class', colorbar=True):
        '''Plots the pointwise product of the every row's sum against every
        row's sum.
        @param function: a function to be applied to each pointwise product.
        @type function: function(element, index)
        @param limit: sets the colour limit. If an element is outside of the
        limit, it will be set to the respective limit.This parameter can be
        None, 'class', 'non_auto', or (x,y). None: no limit is set. 'class':
        the limit is set to self.row_sum_row_sum_limit. 'non_auto': the limit
        is set to (min in the data, max in the data) with the main diagonals
        removed. (x,y): limit is set to (x,y).
        @type limit: str; numpy array/list/tuple, shape:(*)
        @param colorbar: indicates whether or not a colorbar is shown.
        @type colorbar: boolean '''
        title = 'Pointwise Product of Sum of Cols in Rows with Sum of Cols in Rows'
        xlabel = 'Row'
        ylabel = 'Row'
        colorbar_label = 'Normalized Pointwise Product'
        def format(x, i):
            return self.inverse_row_indices[x]
        if limit!=None:
            if limit=='class':
                limit=self.row_sum_row_sum_limit
            elif limit=='non_auto':
                def erase_auto(x, i):
                    if i[0]==i[1]:
                        return np.nan
                    else:
                        return x
                non_auto_data=arf.modify_array(self.row_sum_row_sum, erase_auto, 2)
                limit=[np.nanmin(non_auto_data), np.nanmax(non_auto_data)]
            elif type(limit)==str:
                raise ValueError ('Invalid input for parameter limit')
        drawer.draw_image(self.row_sum_row_sum, title=title, 
                          xlabel=xlabel, ylabel=ylabel, 
                          function=function, limit=limit, 
                          colorbar=colorbar, colorbar_label=colorbar_label)  
        drawer.set_ticks(plt.gca(), format, format, 1 , 1)  
  
      
    def plot_col_sum_col_sum(self, function=None, limit='class', colorbar=True):
        '''Plots the pointwise product of the every column's sum against every
        column's sum.
        @param function: a function to be applied to each pointwise product.
        @type function: function(element, index)
        @param limit: sets the colour limit. If an element is outside of the
        limit, it will be set to the respective limit.This parameter can be
        None, 'class', 'non_auto', or (x,y). None: no limit is set. 'class':
        the limit is set to self.col_sum_col_sum_limit. 'non_auto': the limit
        is set to (min in the data, max in the data) with the main diagonals
        removed. (x,y): limit is set to (x,y).
        @type limit: str; numpy array/list/tuple, shape:(*)
        @param colorbar: indicates whether or not a colorbar is shown.
        @type colorbar: boolean '''
        title = 'Pointwise Product of Sum of Rows in Cols with Sum of ROws in Cols'
        xlabel = 'Col'
        ylabel = 'Col'
        colorbar_label = 'Normalized Pointwise Product'
        def format(x, i):
            return self.inverse_col_indices[x]
        if limit!=None:
            if limit=='class':
                limit=self.col_sum_col_sum_limit
            elif limit=='non_auto':
                def erase_auto(x, i):
                    if i[0]==i[1]:
                        return np.nan
                    else:
                        return x
                non_auto_data=arf.modify_array(self.col_sum_col_sum, erase_auto, 2)
                limit=[np.nanmin(non_auto_data), np.nanmax(non_auto_data)]
            elif type(limit)==str:
                raise ValueError ('Invalid input for parameter limit')
        drawer.draw_image(self.col_sum_col_sum, title=title, 
                          xlabel=xlabel, ylabel=ylabel, 
                          function=function, limit=limit, 
                          colorbar=colorbar, colorbar_label=colorbar_label)  
        drawer.set_ticks(plt.gca(), format, format, 1 , 1 )  


#end of class

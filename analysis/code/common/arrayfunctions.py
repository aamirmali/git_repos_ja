import copy
import numpy as np


def create(shape, element, to_array=True):
    """@return: an array filled with element, with shape specified by the
    parameter shape.
    @rtype: numpy array, shape:(shape, shape(element))
    @type shape: list, shape:(*)
    @param element: the object to be placed in each index of the array.
    @type element: float/numpy array
    @param to_array: indicate whether or not the returned value should be a
    numpy array.
    @type to_array: boolean """
    def create_list(shape, element):
        new_list=[]
        if len(shape)==1:
            for i in range(0, shape[0]):
                new_list.append(element)
        else:
            for i in range(0, shape[0]):
                new_list.append(create_list(shape[1:],element))
        return new_list
    new_array=create_list(shape, element)
    if to_array==True:
        new_array=np.array(new_array)
    return new_array

                                            
def fill(array, element, to_array=True):
    """@return: an array filled with element, with the shape of the input array.
    @rtype: numpy array, shape:(shape(array),shape(element))
    @type array: numpy array
    @param element: the object to be placed in each index of the array.
    @type element: float/numpy array 
    @param to_array: indicate whether or not the returned value should be a
    numpy array.
    @type to_array: boolean """
    def fill_list(array, element):
        new_list=[]
        if len(np.shape(array))==1:  
            for i in range(0,np.shape(array)[0]):
                new_list.append(element)
        else:    
            for i in range(0,np.shape(array)[0]):
                new_list.append(fill_list(array[i], element))
        return new_list
    new_array=fill_list(array,element)
    if to_array==True:
        new_array=np.array(new_array)
    return new_array


def normalize(array):
    '''@return: an array which has been normalized by dividing by its euclidean
    norm (the root-sum-square).
    @rtype: numpy array
    @param array: the array to be normalized.
    @type array: numpy array '''
    norm=np.sqrt(np.sum(array**2))
    if norm!=0:
        inverse_norm=1/norm
        array=array*inverse_norm
    return array


def standardize(array):
    '''@return: standardized array. The array is standardized by subtracting
    its mean, and then dividing by its euclidean norm (the root-sum-square).
    @rtype: numpy array
    @param array: the array to be standardized.
    @type array: numpy array ''' 
    mean=np.mean(array)
    array=array-mean
    norm=np.sqrt(np.sum(array**2))
    if norm!=0:
        inverse_norm=1/norm
        array=array*inverse_norm
    return array


def projection_filter(vector, projection, normalized_projection=False):
    '''Filters out the projection of vector along the parameter
    projection. Vector and projection are both treated as vectors. The inner
    product between two arrays is the sum of the products of corresponding
    values in the array.
    @return: the input vector with its projection along the input projection
    subtracted out. The returned vector is the largest component of parameter
    vector that is orthogonal to projection.
    @rtype: numpy array
    @param vector: the input vector from which its projection along the
    parameter projection will be subtracted.
    @type vector: numpy array
    @type projection: numpy array
    @param normalized_projection: indicates whether or not the parameter
    projectio has been normalized. If it has not been normalized, it will be
    normalized in this function.
    @type normalized_projection: boolean '''
    if normalized_projection==False:
        inner_product=np.sum(vector*projection)
        projection_coefficient=inner_product/(np.sum(projection**2))
    else:
        projection_coefficient=np.sum(vector*projection)
    return vector-projection_coefficient*projection


def meshgrid(array_list, dim_list=1):
    """ Mesh the grid of the arrays in array_list. If the ith value of dim_list
    is j, then the ith array in array_list is considered to be a j dimensional
    array of elements. The meshgrid of A1,... An, returns n arrays,
    mesh(A1),..., mesh(An). Each element in mesh(Ai) is the ith element of the
    tuple element of the product space of A1,...,An (See
    product_space_array_function.).
    @return: a list of the meshed grid.
    @rtype: list of numpy arrays
    @param array_list: a list of arrays to be meshed. Each array is an array of
    elements. Each element can be an array or a single value.
    @type array_list: list of numpy arrays
    @param dim_list: a list of the same length as array list. The ith array
    will be considered to be a (ith value) dimension array of elements. If the
    input is an integer, it will be converted to a list of with the same length
    as array_list, filled with that integer.
    @see: product_space_array_function
    @warning: need theory checking """
    if type(dim_list) == int:
        dim_array=create([(len(array_list))],dim_list)
        dim_list=[]
        dim_list.extend(dim_array)
    meshedgrid=[]
    for i in range(0, len(array_list)):
        index=[]
        shape=[]
        rotater=0
        sec=0
        transpose_index=[]
        for k in range(1, len(array_list)):
            index=(i+k)%len(array_list)
            for j in range (0,dim_list[index]):
                shape.append(np.shape(array_list[index])[j])
        print shape
        grid=create(shape, array_list[i])
        for j in range(i+1,len(array_list)):
            rotater+=dim_list[j]
        for j in range(0,i+1):
            sec+=dim_list[j]
        for k in range(0, sec):
            transpose_index.append(rotater+k)
        for k in range(0, rotater):
            transpose_index.append(k)
        element_dim=len(np.shape(array_list[i]))-dim_list[i]
        for k in range(0, element_dim):
            transpose_index.append(rotater+sec+k)
        grid_i=np.transpose(grid, transpose_index)
        meshedgrid.append(grid_i)
    return meshedgrid


def wrap(function):
    '''Wraps a function which takes in only one required parameter in a
    function that has two input parameters, the second of which is a dummy
    parameter. The output function can be used as input for the functions whcih
    requires a function with the parameters element and index as input.
    @return: a function with two parameters. The first of the parameter is the
    required parameter of the input function. The second is irrelevant.
    @rtype: function(element, index)
    @param function: a function that will be wrapped. It is to have only one
    required parameter.
    @type function: function(element, **args) '''
    def wrapped_function(element, index):
        return function(element)
    return wrapped_function


def get_specs(operant, condition, dim=1, to_array=True):
    """Checks a condition for all elements in the array operant. The function
    considers operant to be a dim dimension array of elements. If the dimension
    of operant is n, the function considers operant to be a dim*(n-dim) array,
    where an array of (n-dim) dimension is considered to be a single
    element. The function checks condition upon each element.
    
    @return: A list of indices of elements for which condition is true. Each
    index is represented by a dim length list, which indicates the location of
    the element in the array.
    @rtype: list, shape(*,dim) 
    @type operant: numpy array
    @param condition: a boolean function that takes in 2 parameters, an element
    and its index, a dim length list that indicates the index of the element. 
    @type condition: boolean function (element, index)
    @type dim: int 
    @param to_array: indicate whether or not the returned value should be a
    numpy array.
    @type to_array: boolean """
    specs=[]
    def check_spec(operant, condition, dim, index):
        if dim==0:
            if condition(operant, index)==True:
                curr_spec=copy.deepcopy(index)
                specs.append(curr_spec)
        if dim>0:
            for i in range(0, np.shape(operant)[0]):
                index.append(i)
                check_spec(operant[i], condition, dim-1,index)
                index.pop()
    check_spec(operant, condition, dim, index=[])
    if to_array==True:
        specs=np.array(specs)
    return specs


def modify_array(operant, function, dim=1, to_array=True):
    """Modifies each element of an array. This function considers operant to be
    a dim dimension array of elements. If the dimension of operant is n, the
    function considers operant to be a dim*(n-dim) array, where an array of
    (n-dim) dimension is considered to be a single element. This function
    modifies each element according to the parameter function.
    @return: A dim dimensional list of element, with the same shape as the
    first dim dimensions of the operant array. Each element is object returned
    by function acting upon the corresponding element in operant.
    @rtype: list, shape:(shape(first dim dimensions of operant), shape(element))
    @type operant: numpy array
    @param function: a function that takes in 2 parameters, an element
    and its index, a dim length list that indicates the index of the element. 
    @type function: function (element, index)
    @type dim: int 
    @param to_array: indicate whether or not the returned value should be a
    numpy array.
    @type to_array: boolean """
    def modify_element(operant, condition, dim, index):
        if dim==0:
            return function(operant, index)
        if dim>0:
            array=[]
            for i in range(0,np.shape(operant)[0]):
                index.append(i)
                array.append(modify_element(operant[i], condition, dim-1, index))
                index.pop()
            return array
    modified_array=modify_element(operant, function, dim, index=[])
    if to_array==True:
        modified_array=np.array(modified_array)
    return modified_array


def sum_space_array_function(operant_array, function, op_dim=1, op_ar_dim=0, to_array=True):
    """Finds the image of a function that takes an element array as input. The
    operant_array is an op_ar_dim dimensional array of operant, and each
    operant is an op_dim dimensional array of element. The element array is an
    op_ar_dim dimensional array of element, with each element's index
    corresponding to the operant's index in the operant_array.
    @return: an array of the image of function upon each element array. Each
    image's index corresponds to the index of the element in operant.
    @rtype: numpy array, dimension: op_dim
    @param operant_array: an array of operant. Each operant is an array of
    elements.
    @type operant_array: numpy array
    @param function: a function that takes in an element array, and the
    element's index in operant as input. Each element in the array corresponds
    to the operant in the operant_array.
    @type function(element array, index)
    @type op_dim: int
    @type op_ar_dim: int 
    @param to_array: indicate whether or not the returned value should be a
    numpy array.
    @type to_array: boolean """
    new_index=[]
    new_index.extend(range(op_ar_dim, op_ar_dim+op_dim))
    new_index.extend(range(0, op_ar_dim))
    new_index.extend(range(op_ar_dim+op_dim, len(np.shape(operant_array))))
    operant_array=np.transpose(operant_array, new_index)
    return modify_array(operant_array, function, op_dim, to_array)
    

def product_space_array_function(operant_list, function, op_dim_list=1, to_array=True):
    ''' Apply a function to each entry of the product space of all the operant
    lists. If A is an array of shape (a1,...,ai), and B is an array of shape
    (b1,...,bj), then the product space of A and B (abbreviated to AB), is
    defined to be an array of shape (a1,...,ai,b1,...bj). If the element in the
    index (x1,...,xi) of A is p1, and the element in the index (y1,...,yj) of B
    is p2, then the element in the index (x1,...,xi,y1,...,yi) of AB is the
    tuple element (p1, p2). The product of more than 2 arrays is defined
    recursively. The shape of ABC = the shape of (AB)C = shape of A(BC). If p3
    is an element of C, then the corresponding element of (AB)C is the tuple
    element of AB extended by p3, in other words, (p1,p2,p3). Similarly, if (p2
    , p3) is the tuple element of BC, and p1 is an element of A, then A(BC)
    would be p1 extended by (p2, p3), giving (p1, p2, p3). Thus ABC is defined
    to be (AB)C = A(BC). In this function, the ith array of operant_list is
    considered to be an op_dim_list[i] dimensional 9array of elements. The
    product space of all the array in operant_list is calculated, and then
    function is applied to each tuple element of the product space.
    @return: the modified product space
    @rtype: numpy array/list
    @param operant_list: a list of operant arrays. Each operant array is
    considered to be an array of elements. Each element can be an array or a
    single value.
    @type operant_list: list of numpy arrays 
    @param function: The function to be applied to each tuple element of the
    product space. The function needs two parameters: the first is the tuple
    element, and the second is the index of that element in the product space.
    @type function: function(tuple element,index)
    @param op_dim_list: a list of operant dimensions. If the ith value of this
    list is x, then the ith array of operant_list is considered to be a x
    dimensional array of elements. If an integer is given, the op_dim_list is
    considered to be a list with the same length as operant_list filled with
    that integer.
    @type op_dim_list: int; list, shape:(*)    
    @param to_array: indicate whether or not the returned value should be a
    numpy array.
    @type to_array: boolean
    @warning: VERY DEEP MAGIC! '''
    list_len=len(operant_list)
    if type(op_dim_list) == int:
        dim_array=create([list_len],op_dim_list)
        op_dim_list=[]
        op_dim_list.extend(dim_array)
    if list_len!=len(op_dim_list):
        raise IndexError('The length of the operant_list is ' 
                         + 'not the same as the length of op_dim_list.')
    def depth_seeking_recursion(element_list, operant_index, element_index):
        def recursion_wrapper(x, i):
            element_list.append(x)
            element_index.extend(i)
            array=depth_seeking_recursion(element_list, operant_index+1, 
                                          element_index)
            element_list.pop()
            for i in range (0, op_dim_list[operant_index]):
                element_index.pop()
            return array
        if operant_index==list_len:
            return function(element_list, element_index)
        else:
            return modify_array(operant_list[operant_index], recursion_wrapper,
                                op_dim_list[operant_index])
    image_array=depth_seeking_recursion(element_list=[], operant_index=0, 
                                        element_index=[])
    if to_array==True:
        image_array=np.array(image_array)
    return image_array


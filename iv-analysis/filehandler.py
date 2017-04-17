import numpy as np
import mce_data
import os
import mce_dirfile


def fix_dirfile_signed_field(data):
    '''dirfile data does not support signed ints, this fuction coverts
    data_mode 10 dirfile data to a signed field.
    @return: the mce data
    @rtype: numpy array, 3 dimensional
    '''
    index= data > 2**27
    data[index]=data[index]-2**28
    return data

def get_mce_data(datafile, **args):
    '''Gets mce data from a mce data file using mce_data.SmallMCEFile.Read
    @return: the mce data
    @rtype: numpy array, 3 dimensional
    @param datafile: the file to be passed into mce_data.SmallMCEFile
    @type datafile: str
    @param args: arguments to be passed into mce_data.SmallMCEFile.Read '''
    if os.path.isdir(datafile):
        data=mce_dirfile.getdata(datafile)
        data=fix_dirfile_signed_field(data)
    elif os.path.isfile(datafile):
        with open(datafile) as f:
            mce=mce_data.SmallMCEFile(datafile)
            data=mce.Read(**args).data
    return data


def IV_data_to_arr(datafile,search_string): 
    """Puts MCE data in datafile into a two-dimensional array, with 
    column number as first dimension.  Does this by searching datafile 
    for lines starting with search_string.  Returns the 2D array"""
    with open(datafile) as f:
        vals=[]
        line=f.readline()
        while line!="":
            if search_string in line:
                line_vals=line.split(None,1)[1].split()
                for i in range(0,len(line_vals)):
                    line_vals[i]=float(line_vals[i])
                vals.append(line_vals)
            line=f.readline()
    vals=np.array(vals)
    if np.size(vals)==0:
        return np.array([])
    return np.transpose(vals)


def printout(formatstring,array,f):
    '''Prints out data in array, in the format of the IV .out files, where
    formatstring is the string preceding the data for every column. Prints
    out to file pointer f.'''
    nrows=array.shape[0]
    ncols=array.shape[1]
    for col in range(0,ncols):
        string='<'+formatstring+'_C'+str(col)+'>'
        for row in range(0,nrows):
            string+=' '
            string+=str(array[row][col])
        f.write(string+'\n')


def data_to_pod_feed_fmt(two_d_data,row_location,col_location=2,
                         map_file='mce_pod_map.txt'):
    """Takes two_d_data, an array in MCE row-col format, and returns a 1D array
    where the 0th element is pod 1 feed 1, the 1st is pod 1 feed 2,
    etc. map_file should contain the correspondance between pod/feed and
    row/col.  The first line is ignored.  The second line should be for pod 1
    feed 1, the third for pod 1 feed 2, etc. row_location is the column in the
    file that contains the MCE row; similarly for col_location."""
    correspondance=get_correspondance(row_location,col_location,map_file)
    formatted_data=[]
    for i in range(0,len(correspondance)):
        MCE_row=correspondance[i][0]
        MCE_col=correspondance[i][1]
        formatted_data.append(two_d_data[MCE_row][MCE_col])
    return np.array(formatted_data)


def get_correspondance(row_location,col_location=2,map_file='mce_pod_map.txt'):
    """Takes MCE data in 2D array data, and puts it in pod-feed format
    according to mapfile.  Uses probe A_or_B.  Returns formatted data as a
    1D array that's ordered pod 1 feed 1, pod 1 feed 2, etc."""
    correspondance=np.zeros([240,2])
#    correspondance=[]
    with open(map_file) as f:
        line=f.readline() #first line discarded
        line=f.readline()
        while line!="":
            split_result=line.split()
            pod=int(split_result[0])
            feed=int(split_result[1])
            MCE_Col=int(split_result[col_location])
            MCE_Row=int(split_result[row_location])
            correspondance[(pod-1)*10+(feed-1)]=[MCE_Row,MCE_Col]
#            correspondance.append((MCE_Row,MCE_Col))
            line=f.readline()
    correspondance=np.array(correspondance)
    return correspondance

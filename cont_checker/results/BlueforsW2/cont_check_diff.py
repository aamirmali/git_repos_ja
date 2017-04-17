#!/usr/bin/env python
#Type the two files you want to compare as arguments after cont_check.py
import sys
import numpy as np


def main(fname1, fname2):
    file1 = np.loadtxt(fname1, dtype = 'string')
    file2 = np.loadtxt(fname2, dtype = 'string')

    #extract data
    data1_st = file1[:,4]
    data2_st = file2[:,4]

    #turn data into floats
    data1 = data1_st.astype(np.float)
    data2 = data2_st.astype(np.float)

    #Create error and difference between data
    err = np.divide(data1,5)
    diff = np.subtract(data1,data2)

    #See if differences exceed errors
    err_mask = np.greater(err,diff)
    ind = np.where(err_mask==False)

    #extract corresponding labels for data
    name1 = file1[:,0:4]
    #name2 = file2[:,0:4]

    print "A difference of greter than 20 percent was found at: "\
    #,file1[ind]
    #print "With corresponding values in the second file: ",file2[ind]
    for a, b in zip(file1[ind], file2[ind]):
        print a[:-1], ':', a[-1], b[-1]
    return file1[ind], file2[ind]

if __name__ == '__main__':
    files = sys.argv
    main(files[1], files[2])
    #print "file 1: ", files[2]

    #for x in xrange(len(sys.argv)):



#taken from SciPy cookbook, with slight modifications
import numpy as np
from scipy import optimize

def gaussian(height, center_x, center_y, width_x, width_y):
    """Returns a gaussian function with the given parameters"""
    width_x = float(width_x)
    width_y = float(width_y)
    return lambda x,y: height*np.exp(
                -(((center_x-x)/width_x)**2+((center_y-y)/width_y)**2)/2)

def moments(data):
    """Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution by calculating its
    moments """
    total = data.sum()
    X, Y = np.indices(data.shape)
    x = (X*data).sum()/total
    y = (Y*data).sum()/total
    col = data[:, int(y)]
    width_x = np.sqrt(abs((np.arange(col.size)-y)**2*col).sum()/col.sum())
    row = data[int(x), :]
    width_y = np.sqrt(abs((np.arange(row.size)-x)**2*row).sum()/row.sum())
    height = data.max()
    return height, x, y, width_x, width_y

def fitgaussian(data):
    """Tries to fit a 2D Gaussian to the 2D array data. On failure, returns
    None.  On success, returns (height, x, y, width_x, width_y, R^2)."""
    params = moments(data)
    errorfunction = lambda p: np.ravel(gaussian(*p)(*np.indices(data.shape)) -
                                 data)
    p,flag = optimize.leastsq(errorfunction, params)
    if flag < 1 or flag > 4: return None
    #calculate R^2
    err=errorfunction(p)
    R_squared=1-np.var(err)/np.var(np.ravel(data))
    return (p[0],p[1],p[2],p[3],p[4],R_squared)

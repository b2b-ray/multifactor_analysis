import numpy as np
from scipy.spatial.distance import pdist

def get_optimal_position(xdata, ydata, rect_xlen, rect_ylen):

    x = np.empty((len(xdata), 2))
    x[:,0] = xdata - 0.5*rect_xlen
    x[:,1] = xdata + 0.5*rect_xlen

    return True

def getOverlap(a, b):
    """
    Computes the overlap between the intervals a and b
    """
    return max(0, min(a[1], b[1]) - max(a[0], b[0]))


def compute_overlap(x):
    """
    Parameters:
    -----------
      x: numpy array of shape (number of intervals, 2)
         containing the lower and upper limits for each interval

    Note:
    -----
       For 2 intervals a, b the overlap can be computed as folowing

    """
    print x
    print pdist(x, getOverlap)




ndim=3 
xdata = np.arange(ndim)
ydata = np.ones(ndim)*3
rect_xlen = np.ones(ndim)*2
rect_ylen = np.ones(ndim)
compute_overlap(np.arange(100).reshape((-1,2)))


import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import ticker
import arrayfunctions as arf


def draw_image(data, title='', xlabel='', ylabel='', function=None, limit=None, 
               colorbar=True, colorbar_label=''):
    '''Draws the image according to data.
    @param data: the data to be plotted. The entries in the array specifies the
    colour of a pixel.
    @type data: numpy array, 2 dimensional
    @param title: specifies the title of the plot
    @type title: str
    @param xlabel: specifies the label on the x axis
    @type xlabel: str
    @param ylabel: specifies the label on the y axis
    @type ylabel: str
    @param function: a function to be applied to each data element before they
    are plotted.
    @type function: function(element, index)
    @param limit: indicates the lower and upper limits of colour. Any data
    element outside of this range will be shown at their respective limit.
    @type limit: numpy array/list/tuple, shape:(2)
    @param colorbar: indicates whether or not a colorbar is shown.
    @type colorbar: boolean
    @param colorbar_label: specifies the label on the colorbar.
    @type colorbar_label: str '''
    fig=plt.figure()
    if data.shape[1]>50:
        fig_xlength=0.16*(data.shape[1])
    else:
        fig_xlength=8
    if data.shape[0]>50:
        fig_ylength=0.12*(data.shape[0])
    else:
        fig_ylength=6
    fig.set_size_inches(fig_xlength, fig_ylength)
    matplotlib.rcParams['font.size']=1.2*min(fig_ylength, fig_xlength)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if function!=None:
        data=arf.modify_array(data, function, 2)
    image=plt.imshow(data,interpolation='nearest')
    if limit!=None:
        image.set_clim(limit[0], limit[1])
    if colorbar==True:
        cbar=plt.colorbar()
        cbar.set_label(colorbar_label)


def set_ticks(axes, xformat_function=None, yformat_function=None, 
              xtick_factor=None, ytick_factor=None):
    """Set tick marks of axes at the appropriate places, with xformat_function
    & yformat_function as the format functions. Ticks are placed at every
    multiple of xtick_factor and ytick_factor.  All fields except axes can be
    None, in which case the corresponding field is ignored."""
    if xtick_factor!=None:
        axes.xaxis.set_major_locator(ticker.MultipleLocator(xtick_factor))
    if xformat_function!=None:
        xformatter=ticker.FuncFormatter(xformat_function)
        axes.xaxis.set_major_formatter(xformatter)
    if ytick_factor!=None:
        axes.yaxis.set_major_locator(ticker.MultipleLocator(ytick_factor))
    if yformat_function!=None:
        yformatter=ticker.FuncFormatter(yformat_function)
        axes.yaxis.set_major_formatter(yformatter)

def set_size_weight(fontsize,fontweight,fig=None):
    """sets the size and weight of all text in fig. If fig is None, uses
    current figure"""
    if fig==None:
        fig=plt.gcf()
    for o in fig.findobj(matplotlib.text.Text):
        o.set_size(fontsize)
        o.set_weight(fontweight)

#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import itertools
import cStringIO
os.environ['MPLCONFIGDIR'] = "/home/rth/.matplotlib"
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np
import pandas
rc('text', usetex=False)


def pcolor2d(title='title',xlab='x',ylab='y',
             z=[[1,2,3,4],[2,3,4,5],[3,4,5,6],[4,5,6,7]]):
    fig=Figure()
    fig.set_facecolor('white')
    ax=fig.add_subplot(111)
    if title: ax.set_title(title)
    if xlab: ax.set_xlabel(xlab)
    if ylab: ax.set_ylabel(ylab)
    image=ax.imshow(z)
    image.set_interpolation('bilinear')
    canvas=FigureCanvas(fig)
    stream=cStringIO.StringIO()
    canvas.print_png(stream)
    return stream.getvalue()

def bar_plot(d, labels):
    colors = itertools.cycle(['b', 'g', 'r', 'c', 'm', 'y', 'k'])
    fig=Figure(figsize=(8, 6), dpi=200)
    fig.set_facecolor('white')
    fig.subplots_adjust(bottom=0.30)
    ax=fig.add_subplot(111)
    ax.set_title("")
    ax.set_ylabel('Factor values')
    #ax.grid(which='major')
    bottom = None
    for col in d.columns:
	if bottom is None:
	    bottom = 0*d[col]
	ax.bar(range(len(d[col])), d[col], align='center', bottom=bottom,
		label=labels[col], color=colors.next(), alpha=0.6)
	bottom += d[col]
    ax.set_xticks(range(len(d[col])))
    ax.set_xlim([-0.5, len(d[col])])
    ax.set_xticklabels([unicode(el) for el in d[col].index], size='x-small',
	    rotation='vertical')
    leg = ax.legend(loc='best', fancybox=True, prop={'size':9})
    leg.get_frame().set_alpha(0.5)

    canvas=FigureCanvas(fig)
    stream=cStringIO.StringIO()
    canvas.print_png(stream, bbox_inches='tight')
    return stream.getvalue()

def two_axis_plot(X=None, xval=None, yval=None, c=None, xlabel='', ylabel='', title=''):
    if X is None:
	X = pandas.DataFrame(index=xval.index, columns=['x', 'y', 'c'])
	X['x'] = xval
	X['y'] = yval
	X['c'] = c

    colors = itertools.cycle(['b', 'g', 'r', 'c', 'm', 'y', 'k'])
    markers = itertools.cycle(['o', 'd', 's', 'p', '^'])
    fig=Figure(figsize=(12, 8), dpi=200)
    fig.set_facecolor('white')
    #fig.subplots_adjust(bottom=0.30)
    ax=fig.add_subplot(111)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    if len(np.unique(X.c.values)) == 1:
	ax.scatter(X.x.values, X.y.values, marker='o')
    else:
	for c in range(len(np.unique(X.c.values):
	    _idx = X.c == c
	    ax.scatter(X.x[_idx].values, X.y[_idx].values,
		    c=colors.next(), marker=markers.next(), label=str(c+1),
		    linewidths=0.5
		    )
	leg = ax.legend(loc='best', fancybox=True, prop={'size':9})
	leg.get_frame().set_alpha(0.5)


    for label, x, y in zip(X.index, X.x.values, X.y.values):
	ax.annotate(
    	    label,
		xy= (x,y),
		xytext= (-5, np.random.randint(0,7)),
		textcoords = 'offset points', ha = 'center', va = 'bottom',
		fontsize='x-small',
		alpha=0.5)
    Dx = X.x.max() - X.x.min()
    Dy = X.y.max() - X.y.min()

    ax.set_xlim([X.x.min()-0.03*Dx, X.x.max()+0.03*Dx])
    ax.set_ylim([X.y.min()-0.01*Dy, X.y.max()+0.03*Dy])

    canvas=FigureCanvas(fig)
    stream=cStringIO.StringIO()
    canvas.print_png(stream, bbox_inches='tight')
    return stream.getvalue()

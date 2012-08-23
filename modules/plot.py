#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import cStringIO
os.environ['MPLCONFIGDIR'] = "/home/rth/.matplotlib"
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

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

def plot(title='title',xlab='x',ylab='y',mode='plot',
         data={'xxx':[(0,0),(1,1),(1,2),(3,3)],
               'yyy':[(0,0,.2,.2),(2,1,0.2,0.2),(2,2,0.2,0.2),(3,3,0.2,0.3)]}):
    fig=Figure()
    fig.set_facecolor('white')
    ax=fig.add_subplot(111)
    if title: ax.set_title(title)
    if xlab: ax.set_xlabel(xlab)
    if ylab: ax.set_ylabel(ylab)
    legend=[]
    keys=sorted(data)
    for key in keys:
        stream = data[key]
        (x,y)=([],[])
        for point in stream:
            x.append(point[0])
            y.append(point[1])
        if mode=='plot':
            ell=ax.plot(x, y)
            legend.append((ell,key))
        if mode=='hist':
            ell=ax.hist(y,20)            
    if legend:
        ax.legend([x for (x,y) in legend], [y for (x,y) in legend], 
                  'upper right', shadow=True)
    canvas=FigureCanvas(fig)
    stream=cStringIO.StringIO()
    canvas.print_png(stream)
    return stream.getvalue()


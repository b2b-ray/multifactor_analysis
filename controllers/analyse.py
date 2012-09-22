#!/usr/bin/python
# -*- coding: utf-8 -*-

import applications.market_segmentation.modules.plot as mplt
import pandas
import numpy as np
from  applications.market_segmentation.modules.analyse import mongo2pandas

def index():
    response.files.append(URL('static', 'js/jquery.zoomooz.min.js'))
    study = dbm.studies.find_one({'_id': ObjectId(request.vars['study'])})
    return dict(mplt=mplt, study=study)

def manage():
    redirect(URL(r=request, c='analyse', f='index',
		args=request.args, vars=request.vars))

def show_weights():
    study = ObjectId(request.vars.study)
    rows = dbm.factors.group(['category'], {'study': study},
	    {'list': []}, 'function(obj, prev) {prev.list.push(obj)}')
    categories = list(dbm.categories.find({'study': study}))
    for idx in range(len(rows)):
	cur_cats = filter(lambda x: x['_id'] == rows[idx]['category'], 
		categories)[0]
	rows[idx]['cat_title'] = cur_cats['title']
    return dict(rows=rows)

def set_weight():
    _id = {'_id': ObjectId(request.args[0])}
    value = float(request.args[1])/1000
    dbm.factors.update( _id, {"$set": { 'weight': value}})
    return ''


def bar_plot():
    study = ObjectId(request.vars.study)
    rows = dbm.factors.group(['category'], {'study': study},
	    {'list': []}, 'function(obj, prev) {prev.list.push(obj)}')
    categories = list(dbm.categories.find({'study': study}))
    for idx in range(len(rows)):
	cur_cats = filter(lambda x: x['_id'] == rows[idx]['category'], 
		categories)[0]
	rows[idx]['cat_title'] = cur_cats['title']
    return dict(rows=rows)

def bar_plot_compute():
    d, w, labels = mongo2pandas(dbm, request.vars.study)
    return mplt.bar_plot(d[list(request.args)], labels)

def two_axis_plot():
    study = ObjectId(request.vars.study)
    cats = list(dbm.categories.find({'study': study}))
    return dict(cats=cats)

def two_axis_plot_compute():
    study = ObjectId(request.vars.study)
    cats = [dbm.categories.find_one({'_id': ObjectId(request.args[0])}),
	    dbm.categories.find_one({'_id': ObjectId(request.args[1])})]
    d0, w0, l = mongo2pandas(dbm, study, {'category': cats[0]['_id']})
    d1, w1, l = mongo2pandas(dbm, study, {'category': cats[1]['_id']})

    return mplt.two_axis_plot((d0*w0).sum(axis=1), (d1*w1).sum(axis=1),
	    xlabel=cats[0]['title'], ylabel=cats[1]['title'])


def draw():
    return mplt.pcolor2d()




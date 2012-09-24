#!/usr/bin/python
# -*- coding: utf-8 -*-

import applications.market_segmentation.modules.plot as mplt
import pandas
import numpy as np
from  applications.market_segmentation.modules.analyse import mongo2pandas

from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import pandas

def index():
    _append_files = [
      'js/jquery.dataTables.min.js',
      'css/jquery.dataTables.css',
      'css/jquery.dataTables_themeroller.css',
      'css/demo_table.css',
      'css/demo_table_jui.css',
      'js/TableTools.min.js',
      'css/TableTools.css',
     'js/jquery.zoomooz.min.js'
      ]
    for f in _append_files:
	response.files.append(URL('static', f))
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
    d, w, labels, cats = mongo2pandas(dbm, request.vars.study)
    return mplt.bar_plot(d[list(request.args)], labels)

def two_axis_plot():
    study = ObjectId(request.vars.study)
    cats = list(dbm.categories.find({'study': study}))
    return dict(cats=cats)

def two_axis_plot_compute():
    d, w, l, cats = mongo2pandas(dbm, request.vars.study,
	    {'category':\
	    {'$in': [ObjectId(el) for el in request.args]}})

    if request.vars.pca:
	# compute principal component analysis
	pca = PCA(n_components=2)
	pca.fit((d*w).values)
	pdata = pandas.DataFrame(index=d.index, columns=['x', 'y', 'c'])
	pdata[['x','y']] = pca.transform((d*w).values)
	pdata['c'] = 0
    else:
	columns = list(cats.keys())
	columns.append('c')
	pdata = pandas.DataFrame(index=d.index, columns=columns)
	# computing rating for categories
	for _cid in cats:
	    mask = cats[_cid]
	    cw = w[mask]
	    cw = cw/cw.sum(axis=1)[0]
	    pdata[_cid] =  (d[mask]*cw).sum(axis=1)
	pdata['c'] = 0

    if request.vars.cluster:
	# K-means clustering
	k_means = KMeans(n_clusters=int(request.vars.n_clusters))
	if request.vars.use_categories and not request.vars.pca:
	    k_means.fit(pdata[[c for c in pdata.columns if c != 'c']].values)
	else:
	    k_means.fit((d*w).values)
	if request.vars.pca:
	    pdata['c'] = k_means.labels_
	else:
	    pdata['c'] = k_means.labels_

    if request.vars.type == 'html':
	request.vars['type'] = 'png'
	img = IMG(_src=URL(r=request, c='analyse', f='two_axis_plot_compute',
		    args=request.args, vars=request.vars))
	if request.vars.cluster:
	    # Create a table with different cluster for visualization
	    bins = np.bincount(k_means.labels_)
	    ii = np.nonzero(bins)[0]
	    ctable = pandas.DataFrame(columns=np.arange(len(np.unique(k_means.labels_))),
		    index=np.arange(bins.max()), dtype=object)
	    ctable.ix[:] = ''
	    for idx, val in enumerate(np.unique(k_means.labels_)):
		companies = d.index[ k_means.labels_ == val]
		ctable[idx][:len(companies)] = sorted(list(companies))

	    return dict(img=img, ctable=ctable)
	else:
	    return dict(img=img)

    elif request.vars.type == 'png':
	if request.vars.pca:
	    return mplt.two_axis_plot(pdata, xlabel=u'Проекция 1', ylabel=u'Проекция 2',
		    title=u'Визуализация методом главных компонентов')
	else:
	    cats_db = list(dbm.categories.find({'_id':\
		    {'$in': [ObjectId(el) for el in request.args]}}))
	    return mplt.two_axis_plot(xval=pdata[request.args[0]],
		    yval=pdata[request.args[1]], c=pdata['c'],
		    xlabel=filter(lambda x: x['_id'] == ObjectId(request.args[0]), cats_db)[0]['title'],
		    ylabel=filter(lambda x: x['_id'] == ObjectId(request.args[1]), cats_db)[0]['title'])
	    #	xlabel=cats[0]['title'], ylabel=cats[1]['title'])


def draw():
    return mplt.pcolor2d()




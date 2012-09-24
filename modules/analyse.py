#!/usr/bin/python
# -*- coding: utf-8 -*-
import pandas
import numpy as np
import sys
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import pandas

if sys.version[:3] == '2.7':
    from bson.objectid import ObjectId
else:
    from pymongo.objectid import ObjectId

def mongo2pandas(dbm, study, mfilter={}, normalize_weights=True):
    _sid = ObjectId(study)
    q_factors = {'study': _sid}
    q_dts = {'study': _sid}
    if mfilter:
        q_factors.update(mfilter)
    factors = list(dbm.factors.find(q_factors))
    cols_and_title = [(el['variable'], el['title']) for el in factors]
    columns = zip(*cols_and_title)[0]
    labels = dict(cols_and_title)
    d = pandas.DataFrame(
            columns=columns,
            index=[el['name'] for el in dbm.dataset.find({'study': _sid},
				    sort=[('_id',1)])],
            dtype=object)
    for dts in dbm.dataset.find(q_dts):
	for column in d.columns:
	    _fid = filter(lambda x: x['variable']==column, factors)[0]['_id']
	    cfactor = filter(lambda x: x['_id'] == _fid, dts['factors'])[0]
    	    d[column][dts['name']] = cfactor['rating']

    d = d.sort_index()
    # setting the category list
    cats = {}
    for f in factors:
	_cid = str(f['category'])
	if _cid in cats:
	    cats[_cid].append(f['variable'])
	else:
	    cats[_cid] = [f['variable']]

    # generate weights 
    w = pandas.DataFrame(d.copy(deep=True), dtype=float)
    for f in factors:
	w[f['variable']][:] = f['weight'] 
    # normalizing
    if normalize_weights:
	w = w/w.sum(axis=1)[0]

    return d, w, labels, cats


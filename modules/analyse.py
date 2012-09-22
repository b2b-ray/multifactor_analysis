#!/usr/bin/python
# -*- coding: utf-8 -*-
import pandas
import numpy as np
import sys
if sys.version[:3] == '2.7':
    from bson.objectid import ObjectId
else:
    from pymongo.objectid import ObjectId

def mongo2pandas(dbm, study, mfilter={}):
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
        idx = 0
        for factor in dts['factors']:
            if all([factor[key] == mfilter[key] for key in mfilter]):
		d[d.columns[idx]][dts['name']] = factor['rating']
                idx += 1
    d = d.sort_index()

    # generate weights 
    w = pandas.DataFrame(d.copy(deep=True), dtype=float)
    for f in factors:
	w[f['variable']][:] = f['weight'] 
    # normalizing
    w = w/w.sum(axis=1)[0]

    return d, w, labels


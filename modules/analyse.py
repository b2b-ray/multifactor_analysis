#!/usr/bin/python
# -*- coding: utf-8 -*-
import pandas
import numpy as np
from bson.objectid import ObjectId

def mongo2pandas(dbm, study, mfilter={}):
    _sid = ObjectId(study)
    q_factors = {'study': _sid}
    q_dts = {'study': _sid}
    if mfilter:
        q_factors.update(mfilter)

    d = pandas.DataFrame(
            columns=[el['variable'] for el in dbm.factors.find(q_factors)],
            index=[el['name'] for el in dbm.dataset.find({'study': _sid})],
            dtype=object)
    for dts in dbm.dataset.find(q_dts):
        idx = 0
        for factor in dts['factors']:
            if all([factor[key] == mfilter[key] for key in mfilter]):
                d[d.columns[idx]][dts['name']] = factor['rating']
                idx += 1
    return d


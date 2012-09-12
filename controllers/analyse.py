#!/usr/bin/python
# -*- coding: utf-8 -*-

import applications.market_segmentation.modules.plot as mplt
import pandas
import numpy as np
from  applications.market_segmentation.modules.analyse import mongo2pandas

def index():
    response.files.append(URL('static', 'js/jquery.zoomooz.js'))
    study = dbm.studies.find_one({'_id': ObjectId(session.cvars['study'])})
    return dict(mplt=mplt, study=study)

def manage():
    redirect(URL(r=request, c='analyse', f='index',
		args=request.args, vars=request.vars))

def bar_plot():
    study = ObjectId(request.vars.study)
    factors = dbm.factors.find({'study': study})
    return dict(factors=factors)

def bar_plot_compute():
    d = mongo2pandas(dbm, request.vars.study)
    return str(d.columns)#d[request.args])
    return mplt.bar_plot(d[request.args])

def compareNfactors():
    study = ObjectId(request.vars.study)
    factors = dbm.factors.find({'study': study})
    return dict(factors=factors)


def draw():
    return mplt.pcolor2d()




#!/usr/bin/python
# -*- coding: utf-8 -*-

import applications.mfa.modules.plot as mplt
import pandas
import numpy as np
from  applications.mfa.modules.analyse import mongo2pandas

def index():
    study = dbm.studies.find_one({'_id': ObjectId(session.study)})
    return dict(mplt=mplt, study=study)

def compare1factor():
    study = ObjectId(request.vars.study)
    factors = dbm.factors.find({'study': study})
    return dict(factors=factors)

def plot1factor():
    factor_name = request.args[0]
    d = mongo2pandas(dbm, request.vars.study)
    return mplt.plot1factor(d[factor_name])

def compareNfactors():
    study = ObjectId(request.vars.study)
    factors = dbm.factors.find({'study': study})
    return dict(factors=factors)


def draw():
    return mplt.pcolor2d()




#!/usr/bin/python
# -*- coding: utf-8 -*-
from applications.market_segmentation.modules.restricted import createFunction

def index():
    rows = dbm.studies.find()
    return dict(rows=rows)

def manage():
    study = dbm.studies.find_one({'_id': ObjectId(request.vars['study'])})

    cats = dbm.categories.find({'study': study['_id']})
    return dict(study=study, cats=cats)

def show():
    factors = dbm.factors.find({'study': ObjectId(request.vars.study),
                'category': ObjectId(request.vars.category)})
    width = sum([len(el['criteria'])+1 for el in factors])
    factors.rewind()
    datasets = dbm.dataset.find({'study': ObjectId(request.vars.study)})
    return dict(factors=factors, width=width, datasets=datasets)

def add():
    factors = dbm.factors.find({'study': ObjectId(request.vars.study)})
    row = {'study': ObjectId(request.vars.study), 'factors': [], 'name': ''}
    for factor in factors:
        mf_row = {'rating': 0, 'category': factor['category'],
                        '_id': factor['_id'], 'criteria': []}
        for crit in factor['criteria']:
            mf_row['criteria'].append({'_id' : crit['_id'], 'value': ''})
        row['factors'].append(mf_row)
    dbm.dataset.insert(row)
    return LOAD(c='dataset', f='show', vars=request.vars, ajax=False)


def edit():
    pars = request.vars.id.split('-')[1:]
    if len(pars) == 2:
        # we want to change the name
        dataset_id, _ = pars
        q = 'name'
        mvalue = request.vars.value
    else:
        dataset_id, factor_id, criterion_id = pars
        dts = dbm.dataset.find_one({'_id': ObjectId(dataset_id)})
        factor = dbm.factors.find_one({'_id': ObjectId(factor_id)})
        factor_pos = argidx_dict(dts['factors'], factor_id)
        if pars[-1] == 'rating':
            # we want to manualy set the rating
            mvalue = float(request.vars.value)
            q = 'factors.%s.rating' % factor_pos
        else:
            # we want to change one of the criteria
            crit_pos = argidx_dict(dts['factors'][factor_pos]['criteria'],
                                                        criterion_id)
            convert = {'integer': int , 'float': float, 'string': str}
            mcrit_type = factor['criteria'][crit_pos]['type']
            mvalue = convert[mcrit_type](request.vars.value)
            q = 'factors.%s.criteria.%s.value' % (factor_pos, crit_pos)
    dbm.dataset.update({'_id': ObjectId(dataset_id)},
        {"$set": { q : mvalue }})

    return mvalue

def recompute_rating():
    factor_id = request.vars.factor
    dataset_id = request.vars.dataset
    factor =  dbm.factors.find_one({"_id": ObjectId(factor_id)})
    crit_names = [crit['variable'] for crit in factor['criteria']]
    code = str(factor['algorithm'])
    compute_rating = createFunction(code, ', '.join(crit_names))
    if dataset_id is not None:
        q =  {"_id": ObjectId(dataset_id)}
    else:
        q = {"study": factor['study']}
    out = ''
    for dts in dbm.dataset.find(q):
        dataset_id = dts['_id']
        # ok all of this is needed to to get the arguments we want to
        # use
        factor_pos = argidx_dict(dts['factors'], factor_id)
        args = {}
        for crit_def, crit in zip(\
                factor['criteria'], dts['factors'][factor_pos]['criteria']):
            args[crit_def['variable']] =  crit['value']
        rating =  compute_rating(**args)
        dbm.dataset.update({'_id': dataset_id},
                {"$set": {'factors.%s.rating' % factor_pos : rating}})
        out += "$('td#dts-%s-%s-rating').text(%s); " % (dataset_id, factor_id, rating)
    if request.vars.silent is None:
        return out
    else:
        return 0

def fill_random_rating():
    from random import random
    study = ObjectId(session.study)
    for dts in dbm.dataset.find({'study': study}):
        for idx in range(len(dts['factors'])):
            dbm.dataset.update({'_id': dts['_id']}, {'$set': {
                'factors.%s.rating' % idx : random()}})
    return 0


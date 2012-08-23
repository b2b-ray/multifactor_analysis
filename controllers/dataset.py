#!/usr/bin/python
# -*- coding: utf-8 -*-

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
    return ''


def edit():
    pars = request.vars.id.split('-')[1:]
    if len(pars) == 2:
        # we want to change the name
        dataset_id, _ = pars
        dts = dbm.dataset.find_one({'_id': ObjectId(dataset_id)})
        dts['name'] = request.vars.value
    else:
        # we want to change one of the criteria
        dataset_id, factor_id, criterion_id = pars
        dts = dbm.dataset.find_one({'_id': ObjectId(dataset_id)})
        factor = dbm.factors.find_one({'_id': ObjectId(factor_id)})
        factor_pos = argidx_dict(dts['factors'], factor_id)
        crit_pos = argidx_dict(dts['factors'][factor_pos]['criteria'],
                                                    criterion_id)
        convert = {'integer': int , 'float': float, 'string': str}
        mcrit = dts['factors'][factor_pos]['criteria'][crit_pos]
        mcrit_type = factor['criteria'][crit_pos]['type']
        mcrit['value'] = convert[mcrit_type](request.vars.value)
        dbm.dataset.update({'_id': ObjectId(dataset_id)}, dts)

    return mcrit['value']

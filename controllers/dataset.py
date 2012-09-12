#!/usr/bin/python
# -*- coding: utf-8 -*-
from applications.market_segmentation.modules.algorithm_setup import createFunction, AlgorithmWrapper

convert_val = {'integer': lambda x: int(x or 0) ,
	'float': lambda x: float(x or 0),
	'string': str}

def index():
    rows = dbm.studies.find()
    return dict(rows=rows)

def manage():
    _append_files = [
      'js/jquery.dataTables.min.js',
      'css/jquery.dataTables.css',
      'css/jquery.dataTables_themeroller.css',
      'css/demo_table.css',
      'css/demo_table_jui.css',
      'js/jquery.jeditable.mini.js',
      'js/jquery.validate.js',
      'js/FixedColumns.min.js',
      'js/TableTools.min.js',
      'css/TableTools.css',
      ]
    for f in _append_files:
	response.files.append(URL('static', f))
    study = dbm.studies.find_one({'_id': ObjectId(request.vars['study'])})

    cats = dbm.categories.find({'study': study['_id']})
    return dict(study=study, cats=cats)

def show():
    factors = dbm.factors.find({'study': ObjectId(request.vars.study),
        'category': ObjectId(request.vars.category)}, sort=[('_id', 1)])
    width = sum([len(el['criteria'])+1 for el in factors])
    factors.rewind()
    datasets = dbm.dataset.find({'study': ObjectId(request.vars.study)})
    return dict(factors=factors, width=width, datasets=datasets)

def add():
    factors = dbm.factors.find({'study': ObjectId(request.vars.study)}, sort = [('_id', 1)])
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
            mcrit_type = factor['criteria'][crit_pos]['type']
            mvalue = convert_val[mcrit_type](request.vars.value)
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
            args[crit_def['variable']] =  convert_val[crit_def['type']](crit['value'])
        rating =  float(compute_rating(**args))
        dbm.dataset.update({'_id': dataset_id},
                {"$set": {'factors.%s.rating' % factor_pos : rating}})
        out += "$('td#dts-%s-%s-rating').text(%.3g); " % (dataset_id, factor_id, rating)
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

def check_factor_consitency():
    factors = dbm.factors.find({'study': ObjectId(request.vars.study),
        'category': ObjectId(request.vars.category)}, sort=[('_id', 1)])
    output = []
    for f in factors:
	e = []
	# checking that there is a variable
	if not f['variable']:
	    e.append(('error', "'variable' field is empty"))
	for crit in f['criteria']:
	    if not crit['variable']:
		e.append(('error',
		    'there is a criteria with no name, either delete it or give it a name'))
	    if crit['type'] == 'string':
		e.append(('warning',
		    XML("Criteria <b>%s </b> is of type <b>string</b>: you should rather use <b>float</b> or <b>integer</b> unless you know what you are doing..." % crit['variable'])))
	if f['rating_method'] == 'algorithm':
	    if not f['algorithm']:
		e.append(('error', "'algorithm' field should not be empty"))
	    algo = AlgorithmWrapper(f)
	    val = algo()
	    if val[1] is not None:
		e.append(('error',
		    'Failed to run algorithm with test parameters '+val[1]))
	output.append({"title": f['title'], 'errors': e})

    num_err = 0
    num_warn = 0
    for f in output:
	num_err += len(filter(lambda x: x[0]=='error', f['errors']))
	num_warn += len(filter(lambda x: x[0]=='error', f['errors']))
    passed = not num_err and ( not num_warn or request.vars.ignore_warnings)

    mvars = {'study': request.vars['study'],
			'category': request.vars['category']}
    if passed and request.vars.redirect_to_dataset:
	redirect(URL(c='dataset', f='show', vars=mvars))

    return dict(factors=output, passed=passed, mvars=mvars,
	    within_dataset=request.vars.redirect_to_dataset)




#!/usr/bin/python
# -*- coding: utf-8 -*-
def index():
    redirect(URL(r=request, c='default', f='index'))

def add():
    _id = ObjectId(request.args[0])
    _cid = ObjectId()
    dbm.factors.update( {'_id': _id}, {'$push':
        { 'criteria': {'_id': _cid, 'variable': '',
                    'type': '', 'description': '' }} })
    factor = dbm.factors.find_one({'_id': _id})
    dts = dbm.dataset.find_one({'study': factor['study']})
    if dts:
        factor_pos = argidx_dict(dts['factors'], _id)
        dbm.dataset.update( {'study': factor['study']}, {"$push" : {
            "factors.%s.criteria" % factor_pos: { '_id': _cid, 'value': ''} }}, multi=True)
    return "$('#add-criteria-%s').before('%s')" % ( _id,
            XML(DIV(LOAD(c='criteria', f='edit', vars=dict(_id=_id, _cid=_cid), ajax=True),
                _id='%s-criteria-%s' % (_id, _cid))
                ).replace( "'", r"\'").replace('\n', ' ') )

def test():
    return "$('#add-criteria-%s').before('%s')" % (request.args[0], 'DTSy')

def delete():
    _id = ObjectId(request.vars._id)
    _cid = ObjectId(request.vars._cid)

    # remove criteria from factors
    dbm.factors.update( {'_id': _id}, {'$pull' : {
        "criteria" : { "_id": _cid} }})
    # remove criteria from dataset
    factor = dbm.factors.find_one({'_id': _id})
    dts = dbm.dataset.find_one({'study': factor['study']})
    if dts:
        factor_pos = argidx_dict(dts['factors'], _id)
        dbm.dataset.update( {'study': factor['study']}, {"$pull" : {
            "factors.%s.criteria" % factor_pos: { '_id': _cid} }}, multi=True)
    return ''


def edit():
    return LOAD(c='criteria', f='edit_internal', args=request.args,
                        vars=request.vars, ajax=True)

def edit_internal():
    _id = ObjectId(request.vars._id)
    _cid = ObjectId(request.vars._cid)

    form = SQLFORM.factory(
        Field('variable', 'string', requires=IS_MATCH(r'[a-z][a-z0-9]*',
                            error_message='Should be matching [a-z][a-z0-9]*')),
        Field('description', 'string'),
        Field('type', 'string', requires=IS_IN_SET([ 'string', 'integer', 'float'],zero=None)),
        Field('min_val', 'double'),
        Field('max_val', 'double'),
        _class='criterion'
        )

    factor = dbm.factors.find_one({"_id": _id})
    criterion = filter(lambda x: x['_id'] == _cid,  factor['criteria'])[0]
    _crit_idx = factor['criteria'].index(criterion)
    form.vars.update(criterion)
    del form.vars['_id']
    # checking if update
    if form.process().accepted:
	fvars = {}
        for key in form.fields:
            if form.vars[key] is not None and key != '_id':
                fvars[key] = form.vars[key]
	# dict comprehension not compatible with python2.6
        #fvars = {key: form.vars[key]\
        #        for key in form.fields\
        #        if form.vars[key] is not None and key != '_id'}
        fvars['_id'] = criterion['_id']
        #factor['criteria'][_crit_idx] = fvars
        dbm.factors.update( {'_id': _id}, {'$set':\
            {'criteria.%s' % _crit_idx : fvars}})
        session.flash = 'Success'
        return LOAD(c='criteria', f='show', vars=dict(_id=_id, _cid=_cid))
    return dict(form=form, _id=str(_id), _cid=str(_cid))

def show():
    _id = ObjectId(request.vars._id)
    if request.vars._cid:
        _cid = ObjectId(request.vars._cid)
    else:
        _cid = None

    factor = dbm.factors.find_one({'_id': _id})
    if _cid:
        # now the '_id' is local to the criteria
        factor = filter(lambda x: x['_id'] == _cid,  factor['criteria'])[0]
    else:
        raise ValueError('Wrong arguments given to this function')
    return dict(factor=factor, _id=_id, _cid=_cid)



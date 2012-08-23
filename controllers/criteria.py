#!/usr/bin/python
# -*- coding: utf-8 -*-
def index():
    redirect(URL(r=request, c='default', f='index'))

def add():
    _id = ObjectId(request.args[0])
    _cid = ObjectId()
    factor = dbm.factors.find_one({"_id": _id})
    factor['criteria'].append({'_id': _cid, 'variable': '',
        'type': '', 'description': '' })
    dbm.factors.update( {'_id': _id}, factor)
    return "$('#add-criteria-%s').before('%s')" % ( _id,
            XML(DIV(LOAD(c='criteria', f='edit', vars=dict(_id=_id, _cid=_cid), ajax=True),
                _id='%s-criteria-%s' % (_id, _cid))
                ).replace( "'", r"\'").replace('\n', ' ') )

def test():
    return "$('#add-criteria-%s').before('%s')" % (request.args[0], 'DTSy')

def delete():
    _id = ObjectId(request.vars._id)
    _cid = ObjectId(request.vars._cid)
    factor = dbm.factors.find_one({"_id": _id})
    criterion = filter(lambda x: x['_id'] == _cid,  factor['criteria'])[0]
    _crit_idx = factor['criteria'].index(criterion)
    del factor['criteria'][_crit_idx]
    dbm.factors.update( {'_id': _id}, factor)
    return ''


def edit():
    return LOAD(c='criteria', f='edit_internal', args=request.args,
                        vars=request.vars, ajax=True)

def edit_internal():
    _id = ObjectId(request.vars._id)
    _cid = ObjectId(request.vars._cid)

    form = SQLFORM.factory(
        Field('variable', 'string'),
        Field('description', 'string'),
        Field('type', 'string', requires=IS_IN_SET(['integer', 'float', 'string'])),
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
        fvars = {key: form.vars[key]\
                for key in form.fields
                if form.vars[key] is not None and key != '_id'}
        fvars['_id'] = criterion['_id']
        factor['criteria'][_crit_idx] = fvars
        dbm.factors.update( {'_id': _id}, factor)
        session.flash = 'Success'
        return LOAD(c='criteria', f='show', vars=dict(_id=_id, _cid=_cid))
    return form

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



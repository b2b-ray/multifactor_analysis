#!/usr/bin/python
# -*- coding: utf-8 -*-

def index():
    redirect(URL(r=request, c='default', f='index'))

def add():
    mvars = request.vars
    for key in ['study', 'category']:
        mvars[key] = ObjectId(mvars[key])
    # fixes a weird behaviour of this parameter being passed multiple times
    if isinstance(mvars['title'], list):
        mvars['title'] = mvars['title'][-1]
    mvars['description'] = ''
    mvars['criteria'] = []
    mvars['algorithm_description'] = ''
    mvars['algorithm'] = ''
    mvars['variable'] = ''
    mvars['default_weight'] = 0
    mvars['rating_method'] = 'algorithm'
    _id = str(dbm.factors.insert(mvars))
    dbm.dataset.update( {'study': mvars['study']}, {"$push" : {
            'factors': {"_id": mvars['_id'], 'criteria': [],
                'category': mvars['category'], 'rating': 0}}})
    return "$('#factors').append('%s')" % (XML(
            H3(A(mvars['title']),_id=_id+"-title"))+
            XML(DIV( LOAD(c='factors', f='show', args=[_id], ajax=True),
                _class='factor-div', _id=_id+'-div')
                )).replace( "'", r"\'").replace('\n', ' '),

def show():
    factor = dbm.factors.find_one({'_id': ObjectId(request.args[0])})
    return dict(factor=factor)

def delete():
    _id = ObjectId(request.args[0])
    factor = dbm.factors.find_one({'_id': _id})
    dbm.factors.remove(_id)
    return str(dbm.dataset.update({'study': factor['study']},
        {"$pull": { "factors": {"_id" : _id}}}, safe=True))

    return ''


def edit():
    return LOAD(c='factors', f='edit_internal', args=request.args,
                        vars=request.vars, ajax=True)

def edit_internal():
    _id = {'_id' : ObjectId(request.args[0])}
    field = request.args[1]
    defaults = {'_class': field}
    if field == 'description':
        form = SQLFORM.factory(
            Field('description', 'text', requires=IS_NOT_EMPTY()),
            **defaults
            )
    if field == 'rating_method':
        form = SQLFORM.factory(
            Field('rating_method', 'string', requires=IS_IN_SET(['algorithm', 'manual'],zero=None)),
            **defaults
            )
    elif field == 'algorithm':
        form = SQLFORM.factory(
            Field('algorithm', 'text', requires=IS_NOT_EMPTY()),
            col3 = {'algorithm': 'test'},
            **defaults
            )
    elif field == 'algorithm_description':
        form = SQLFORM.factory(
            Field('algorithm_description', 'text', requires=IS_NOT_EMPTY()),
            col3 = {'algorithm_description': 'test'},
            **defaults
            )
    elif field == 'title':
        form = SQLFORM.factory(
            Field('title', 'string'),
            **defaults
            )
    elif field == 'default_weight':
        form = SQLFORM.factory(
            Field('default_weight', 'double', requires=IS_FLOAT_IN_RANGE(0, 100)),
            **defaults
            )
    elif field == 'variable':
        form = SQLFORM.factory(
            Field('variable', 'string', requires=IS_MATCH(r'[a-z][a-z0-9]+',
                error_message='Should be matching [a-z][a-z0-9]+')),
            **defaults
            )

    factor = dbm.factors.find_one(_id)
    if field in factor:
        form.vars.update({field: factor[field]})
    # checking if update
    if form.process().accepted:
        dbm.factors.update( _id, {"$set": { field: form.vars[field]}})
        if field == 'algorithm':
            LOAD(c='dataset', f='recompute_rating',
                    vars=dict(factor=factor['_id'], silent=True))
        session.flash = 'Success'
        return LOAD(c='factors', f='show_field', args=[ _id['_id'], field])
    return dict(form=form, field=field, _id=str(factor['_id']))

def show_field():
    _id = ObjectId(request.args[0])
    field = request.args[1]
    factor = dbm.factors.find_one({'_id': _id})

    return dict(field=field, factor=factor, _id=_id)


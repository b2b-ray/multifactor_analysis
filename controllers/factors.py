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
    mvars['default_weight'] = 0
    _id = str(dbm.factors.insert(mvars))
    return "$('#factors').append('%s')" % (XML(
            H3(A(mvars['title']),_id=_id+"-title"))+
            XML(DIV( LOAD(c='factors', f='show', args=[_id], ajax=True),
                _class='factor-div', _id=_id+'-div')
                )).replace( "'", r"\'").replace('\n', ' '),

def show():
    factor = dbm.factors.find_one({'_id': ObjectId(request.args[0])})
    return dict(factor=factor)

def delete():
    out = dbm.factors.remove(ObjectId(request.args[0]))
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
            Field('default_weight', 'double'),
            **defaults
            )

    factor = dbm.factors.find_one(_id)
    if field in factor:
        form.vars.update({field: factor[field]})
    # checking if update
    if form.process().accepted:
        factor[field] = form.vars[field]
        margs = [ _id['_id'], field]
        dbm.factors.update( _id, factor)
        session.flash = 'Success'
        return LOAD(c='factors', f='show_field', args=margs)
    return dict(form=form, field=field)

def show_field():
    _id = ObjectId(request.args[0])
    field = request.args[1]
    factor = dbm.factors.find_one({'_id': _id})

    return dict(field=field, factor=factor, _id=_id)


#!/usr/bin/python
# -*- coding: utf-8 -*-

def index():
    redirect(URL(r=request, c='default', f='index'))

def edit():
    form = SQLFORM.factory(
	# auth signature
        Field('title', requires=IS_NOT_EMPTY()),
	Field('description', 'text', requires=IS_NOT_EMPTY()),
	)
    # Inserting cancel button
    form[0][-1][1].insert(0, INPUT(_type="button", _value="Cancel",
	_onclick="location='%s';"%URL(r=request, c='studies', f='manage', vars=request.vars)))
    form[0][-1][1].insert(1, SPAN('', _style='padding: 0 30%;'))
    # checking if update
    if 'category' in request.vars:
	idx = {'_id': ObjectId(request.vars['category'])}
	form.vars.update(dbm.categories.find_one(idx))
	del form.vars['_id']
	del form.vars['study']
    if form.process().accepted:
        form.vars['study'] = ObjectId(request.vars['study'])
	if 'category' in request.vars:
	    dbm.categories.update(idx, form.vars)
	else:
            idx = {'_id': dbm.categories.insert(form.vars)}
	session.flash = 'Sucess!'
	redirect(URL(r=request, c='studies', f='manage',
            vars=dict(study=request.vars['study'], category=idx['_id'])))
    elif form.errors:
        response.flash = 'form has errors'
    return dict(form=form)

def delete():
    out = dbm.categories.remove(ObjectId(request.vars['category']))
    session.flash = 'Categories deleted.'
    redirect(URL(r=request, c='studies', f='manage', vars=dict(study=request.vars['study'])))



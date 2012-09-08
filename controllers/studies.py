#!/usr/bin/python
# -*- coding: utf-8 -*-

def index():
    """List all studies.
    """
    redirect(URL(r=request, c='default', f='index'))

def edit():
    filter_group = db.auth_group.role.like('user_%')
    form = SQLFORM.factory(
	# auth signature eventualy
        Field('title', requires=IS_NOT_EMPTY()),
	Field('description', 'text', requires=IS_NOT_EMPTY()),
	Field('admin_group', 'integer', 
	    requires=IS_IN_DB(db(filter_group), 'auth_group.id', '%(role)s'),
	    label='Give admin access to'),
	Field('user_group', 'integer', 
	    requires=IS_IN_DB(db(filter_group), 'auth_group.id', '%(role)s'),
	    label='Give user access to'),
	)
    # This is ugly but it inserts the cancel button in the form
    form[0][-1][1].insert(0, INPUT(_type="button", _value="Cancel",
	_onclick="location='%s';"%URL(r=request, f='index')))
    form[0][-1][1].insert(1, SPAN('', _style='padding: 0 30%;'))
    # if update prepopulate form with values from the database
    if 'study' in request.vars:
	idx = {'_id': ObjectId(request.vars['study'])}
	form.vars.update(dbm.studies.find_one(idx))
	del form.vars['_id']
    if form.process().accepted:
	session.flash = 'Sucess!'
	if 'study' in request.vars:
	    # means it's an update
	    dbm.studies.update(idx, form.vars)
            redirect(URL(r=request, f='manage', vars={'study': request.vars['study']}))
	else:
	    # otherwise just insert a new element
            idx = {'_id': dbm.studies.insert(form.vars)}
            redirect(URL(r=request, f='manage', vars={'study': idx['_id']}))
    elif form.errors:
        response.flash = 'form has errors'
    return dict(form=form)

def delete():
    """Delete a study. 
    """
    _id = ObjectId(request.vars['study'])
    dbm.studies.remove(_id)
    dbm.factors.remove({'study': _id})
    dbm.dataset.remove({'study': _id})
    session.flash = 'Study deleted.'
    redirect(URL(r=request, f='index'))


def manage():
    """This is the place where most of actual work on defining dataset structure
    is actually done.
    """
    study = dbm.studies.find_one({'_id': ObjectId(request.vars['study'])})

    cats = dbm.categories.find({'study': study['_id']})

    if 'category' in request.vars:
        factors = dbm.factors.find({'study': ObjectId(study['_id']),
                    'category': ObjectId(request.vars['category'])}, sort=[('_id',1)])
        return dict(study=study, cats=cats, factors=factors)
    else:
        return dict(study=study, cats=cats)

# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = 'Multi factor analysis framework'
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'B2B Ray <root@b2b-ray.com>'
response.meta.description = 'multifactror analysis application'
response.meta.keywords = 'marketing, B2B, multifactor analysis'
response.meta.copyright = 'Copyright 2011'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################
for key in ['study', 'category']:
    # storing current vars in session
    if 'cvars' not in session:
	session.cvars = {}
    if key in request.vars:
	session.cvars[key] = ObjectId(request.vars[key])

if request.controller in ['studies', 'dataset', 'analyse']:
    controller_next = request.controller
else:
    controller_next = 'studies'

response.menu = [
    (T('Home'), False, URL('default','index'), []),
    (T('Studies'), False, None,
	[(s['title'], False, URL(c=controller_next, f='manage', vars=dict(study=s['_id'])))\
		for s in dbm.studies.find()])
    ]

if session.cvars:
    response.menu += [
    (T('Setup'), False, URL(c='studies', f='manage', vars=session.cvars)),
    (T('Dataset'), False, URL(c='dataset', f='manage', vars=session.cvars)),
    (T('Analyse'), False, URL(c='analyse', f='index', vars=session.cvars))
	    ]

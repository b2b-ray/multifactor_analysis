#!/usr/bin/python
# -*- coding: utf-8 -*-

def argidx_dict(iterable, _id):
    """
    Finds the position of an element with a given key in a list.
     iterable: list
     _id: str or ObjectId

    >> a = [ {'_id': ObjectId('a31'), 'name': 'name2'},
	     {'_id': ObjectId('a22'), 'name': 'test'}]
    >> print argidx_dict(a, 'a22')
    1
    """
    if type(_id) is  str:
        _id = ObjectId(_id)
    val = filter(lambda x: x['_id'] == _id, iterable)[0]
    return iterable.index(val)

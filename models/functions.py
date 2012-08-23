#!/usr/bin/python
# -*- coding: utf-8 -*-

def argidx_dict(iterable, _id):
    if type(_id) is  str:
        _id = ObjectId(_id)
    val = filter(lambda x: x['_id'] == _id, iterable)[0]
    return iterable.index(val)

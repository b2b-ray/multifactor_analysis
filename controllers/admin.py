#!/usr/bin/python
# -*- coding: utf-8 -*-

def index():
    return dict()

def todolist():
    import os.path
    with open('applications/market_segmentation/todolist.rst', 'r') as f:
        txt = f.read()

    return dict(txt=txt)


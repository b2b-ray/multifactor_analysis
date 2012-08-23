#!/usr/bin/python
# -*- coding: utf-8 -*-

import applications.mfa.modules.plot as mplt

def index():
    return dict(mplt=mplt)

def draw():
    return mplt.pcolor2d()




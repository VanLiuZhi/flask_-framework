#!/usr/bin/env python
# encoding: utf-8

"""
@author: LiuZhi
@contact: 1441765847@qq.com
@software: PyCharm
@file: compat.py
@time: 2018-12-22 23:25
"""

import sys

PY2 = int(sys.version[0]) == 2

if PY2:
    text_type = 'utf-8'  # noqa
    binary_type = str
    string_types = (str, 'utf-8')  # noqa
    unicode = 'utf-8'  # noqa
    basestring = 'utf-8'  # noqa
else:
    text_type = str
    binary_type = bytes
    string_types = (str,)
    unicode = str
    basestring = (str, bytes)
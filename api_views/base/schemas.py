#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:   LiuZhi
@time:     2019-01-20 23:37
@contact:  vanliuzhi@qq.com
@software: PyCharm
"""

from marshmallow import Schema, fields


class BaseSchema(Schema):
    id = fields.Str()
    created_at = fields.Str()
    updated_at = fields.Str()

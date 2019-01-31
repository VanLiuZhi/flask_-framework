#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:   LiuZhi
@time:     2019-01-20 00:27
@contact:  vanliuzhi@qq.com
@software: PyCharm
"""

from marshmallow import fields

from api_views.base.schemas import BaseSchema


class PostListSchema(BaseSchema):
    title = fields.Str()
    abstract_content = fields.Str()
    orig_url = fields.Str()
    tags = fields.Str()
    n_likes = fields.Integer()
    n_comments = fields.Integer()
    n_collects = fields.Integer()
    is_liked = fields.Boolean()
    is_commented = fields.Boolean()
    is_collected = fields.Boolean()




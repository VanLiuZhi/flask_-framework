#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:   LiuZhi
@time:     2019-01-18 21:34
@contact:  vanliuzhi@qq.com
@software: PyCharm

扩展flask
"""

from werkzeug.utils import cached_property
from werkzeug.wrappers import Response
from flask import Flask as _Flask, Request as _Request
from flask_security import current_user

from models.user import User
from api_views.base.utils import ApiResult


class Request(_Request):
    @cached_property
    def user_id(self):
        user = current_user
        return user and (user.is_authenticated and user.id) or None

    @cached_property
    def user(self):
        return User.get(self.user_id) if self.user_id else None


class Flask(_Flask):
    # request类扩展，增加user_id，user属性
    # request_class = Request

    # 扩展flask的响应，接口数据直接返回json
    def make_response(self, rv):
        if isinstance(rv, Response):
            return rv

        status = 200

        if not isinstance(rv, ApiResult) and not isinstance(rv, dict) and \
                len(rv) == 2 and isinstance(rv[1], int):
            rv, status = rv
        if isinstance(rv, (dict, list)):
            dt = {'data': rv}
            rv = ApiResult(dt, status=status)
        if isinstance(rv, ApiResult):
            return rv.to_response()
        return _Flask.make_response(self, rv)

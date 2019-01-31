#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:   LiuZhi
@time:     2019-01-20 00:25
@contact:  vanliuzhi@qq.com
@software: PyCharm
"""

from functools import wraps

from flask import json
from werkzeug.wrappers import Response


def marshal(data, schema):
    if isinstance(data, (list, tuple)):
        return [marshal(d, schema) for d in data]

    result, errors = schema.dump(data)
    if errors:
        for item in errors.items():
            print('{}: {}'.format(*item))
    return result


class marshal_with(object):
    """
    序列化数据
    """

    def __init__(self, schema_cls):
        self.schema = schema_cls()

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            resp = f(*args, **kwargs)
            a = marshal(resp, self.schema)
            return a

        return wrapper


class ApiResult(object):
    """
    接口响应处理类
    """

    def __init__(self, value, status=200):
        self.value = value
        self.status = status

    def to_response(self):
        """
        在返回特定的数据的时候，自动调用该方法转换数据为json
        :return:
        """
        if 'r' not in self.value:
            self.value['r'] = 0
        return Response(json.dumps(self.value), mimetype='application/json',
                        status=200 if self.status > 204 else self.status)

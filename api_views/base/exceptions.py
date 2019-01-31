#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:   LiuZhi
@time:     2019-01-20 00:25
@contact:  vanliuzhi@qq.com
@software: PyCharm
"""

from .utils import ApiResult


class ApiException(Exception):
    """
    接口异常类，raise ApiException() 的时候使用
    """
    def __init__(self, error, real_message=None):
        self.code, self.message, self.status = error
        if real_message is not None:
            self.message = real_message

    def to_result(self):
        return ApiResult({'errmsg': self.message, 'r': self.code,
                          'status': self.status})

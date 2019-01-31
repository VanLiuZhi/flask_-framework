#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:   LiuZhi
@time:     2019-01-20 00:38
@contact:  vanliuzhi@qq.com
@software: PyCharm
"""

import re
from flask.views import MethodView

from .exceptions import ApiException
from api_views.base import errors


class APIHandelView(MethodView):

    def dispatch_request(self, *args, **kwargs):
        """
        重载 dispatch_request 实现动态接口路由
        """
        api_name = kwargs.get('api_name')
        api_method = getattr(self, api_name, None)
        if api_method is None:
            raise ApiException(errors.api_not_found)
        return api_method()

    def get(self, request, api_name):
        return self.post(request, api_name)

    def post(self, request, api_name):
        r = re.compile('[a-z]+')
        re_match = r.match(api_name)
        action = re_match and re_match[0] or None
        models_name = action and api_name[len(action):] or None
        api_object = self.get_api_method(api_name, action)
        if not api_object:
            return self.xml_response_for_json(self.error_response(msg='Method Not Found'))
        res = api_object(request, models_name)
        return res

    def get_api_method(self, api_name, action):
        if action and action in self.base_method_str:
            method_dict = {
                'list': self.api_list_method,
                'create': self.api_create_method,
                'edit': self.api_edit_method,
                'delete': self.api_delete_method,
            }
            return method_dict.get(action)
        else:
            return getattr(self, api_name, None)

    def api_list_method(self, request, models_name):
        """
        获取模型列表数据(分页)
        :return:
        """

        return self.xml_response_for_json(self.success_response(msg='获取成功'))

    def api_create_method(self, request, models_name):
        """
        添加数据到模型
        :param request:
        :param models_name:
        :return:
        """

        return self.xml_response_for_json(self.success_response(msg='添加成功'))

    def api_edit_method(self, request, models_name):
        """
        编辑模型数据
        :param request:
        :param models_name:
        :return:
        """

        return self.xml_response_for_json(self.success_response(msg='修改成功'))

    def api_delete_method(self, request, models_name):
        """
        删除模型的数据
        :param request: 参数结构举例 {'data': {'guid': 123}}
        :param models_name:
        :return:
        """

        return self.xml_response_for_json(self.success_response(msg='删除成功'))

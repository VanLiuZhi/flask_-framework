#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:   LiuZhi
@time:     2019-01-20 00:17
@contact:  vanliuzhi@qq.com
@software: PyCharm
"""

from flask import request
import logging

from api_views.base.api import APIHandelView
from api_views.base.utils import marshal_with, marshal
from .post_schema import PostListSchema
from models.core import Post, Tag, PostTag
from models.search import Item
from base.mc import cache


def get_params_to_dict(data, res_fields):
    fields = res_fields
    res = []
    for item in fields:
        value = data.get(item, None)
        res.append(value)
    return res


class PostAPI(APIHandelView):
    """
    post 数据相关接口
    """

    # @marshal_with(PostListSchema)
    def getPostList(self):
        logging.info('getPostList')
        data = request.json
        _fields = ['type', 'page', 'limit', 'query_str', 'orderby']
        type, page, limit, query_str, order_by = get_params_to_dict(data, _fields)
        if type == 'normal':
            res = Post.get_posts_list(page, limit, order_by)
            return {'items': marshal(res.items, PostListSchema()), 'total': res.total}
        elif type == 'search':
            return self.searchPost(query_str, page, limit, True)
        elif type == 'tag':
            tag = query_str.lower()
            res = PostTag.get_posts_by_tag(tag, page, limit)
            if not res:
                return {'items': [], 'total': 0}
            return {'items': marshal(res.items, PostListSchema()), 'total': res.total}

    # @marshal_with(PostListSchema)
    def searchPost(self, query=None, page=None, limit=None, _self=False):
        if not _self:
            data = request.json
            query, page, limit = get_params_to_dict(data, ['query', 'page', 'limit'])
        else:
            query, page, limit = query, page, limit
        res = Item.new_search(query, page=page, per_page=limit)
        total = res.total
        res = marshal(res.items, PostListSchema())
        for i in res:
            i['value'] = i.get('title')
        return {'items': res, 'total': total}

    def getPostForTag(self):
        data = request.json
        tag, page, limit = get_params_to_dict(data, ['tag', 'page', 'limit'])
        tag = tag.lower()
        res = PostTag.get_posts_by_tag(tag, page, limit)
        return {'items': marshal(res.items, PostListSchema()), 'total': res.total}

    # @cache('api_get_tag')
    def getTag(self, default=True):
        if not default:
            import random
            color_list = ['#FF895D', '#31bfb9', '#FF2E63', '#00BBF0', '#AC005D', '#0D7377', '#67c23a', '#e6a23c',
                          '#404802',
                          '#009a61']
            random.shuffle(color_list)
            query = Tag.query
            count = query.count()
            offset = 20 or int(random.uniform(0, count))
            query = Tag.query.offset(offset).limit(10).all()
            res = [{'name': item.name} for item in query]
            for index, item in enumerate(res):
                item.update({'color': color_list[index]})
            random.shuffle(res)
        else:
            res = [{'name': 'overflow', 'color': '#0D7377'}, {'name': 'editor', 'color': '#AC005D'},
                   {'name': 'height', 'color': '#009a61'}, {'name': 'selection', 'color': '#404802'},
                   {'name': 'display', 'color': '#67c23a'}, {'name': 'vuedirective', 'color': '#31bfb9'},
                   {'name': 'scrollheight', 'color': '#FF2E63'}, {'name': 'lodash', 'color': '#00BBF0'},
                   {'name': 'webpack', 'color': '#e6a23c'}, {'name': 'slidedown', 'color': '#FF895D'}]
        return res

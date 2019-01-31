#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:   LiuZhi
@time:     2019-01-11 18:28
@contact:  vanliuzhi@qq.com
@software: PyCharm
"""

import redis

from base.mc import rdb


def incr_key(stat_key, amount):
    try:
        total = rdb.incr(stat_key, amount)
    except redis.exceptions.ResponseError:
        rdb.delete(stat_key)
        total = rdb.incr(stat_key, amount)
    return total

def load_models():
    from models.like import LikeItem
    from models.comment import CommentItem
    from models.collect import CollectItem
    from models.user import User, Role, user_datastore
    from models.core import Post, Tag, PostTag
    from models.search import Item
    from models.contact import Contact, userFollowStats
    return locals()

if __name__ == '__main__':
    print(load_models())
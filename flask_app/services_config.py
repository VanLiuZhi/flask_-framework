#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: LiuZhi
@contact: 1441765847@qq.com
@software: PyCharm
@file: services_config.py
@time: 2018-12-24 23:30
"""

from flask_app.utils import get_env_value


class RedisConfig(object):

    @classmethod
    def redis_config_dict(cls):
        return {
            'CACHE_TYPE': 'redis',  # Use Redis
            'CACHE_REDIS_HOST': get_env_value('CACHE_REDIS_HOST', '127.0.0.1'),  # Host, default 'localhost'
            'CACHE_REDIS_PORT': get_env_value('CACHE_REDIS_PORT', 6379),  # Port, default 6379
            'CACHE_REDIS_PASSWORD': get_env_value('CACHE_REDIS_PASSWORD', ''),  # Password
            'CACHE_REDIS_DB': get_env_value('CACHE_REDIS_DB', '')  # DB, default 0
        }

    @classmethod
    def load_config(cls):
        is_use_redis = get_env_value('CACHE_TYPE') == 'redis' or False
        return is_use_redis and cls.redis_config_dict() or {}

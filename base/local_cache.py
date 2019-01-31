#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:   LiuZhi
@time:     2019-01-11 18:34
@contact:  vanliuzhi@qq.com
@software: PyCharm
"""


class LocalCache(object):
    def __init__(self, size=10000):
        self.dataset = {}  # 缓存数据
        self.size = size  # 最大缓存数

    def clear(self):
        self.dataset.clear()

    def _cache(self, key, value):
        """
        设置缓存，超过最大缓存数，先清空所有缓存再设置
        """
        if len(self.dataset) >= self.size:
            self.dataset.clear()
        self.dataset[key] = value

    def __repr__(self):
        return '<LocalCache>'

    def get(self, key) -> str:
        return self.dataset.get(key)

    def get_multi(self, keys: list) -> dict:
        """
        一次获取对个值，返回字典
        """
        ds = self.dataset
        ds_get = ds.get
        r = dict((k, ds_get(k)) for k in keys)
        return r

    def get_list(self, keys):
        """
        获取多个值，返回的是值的列表
        """
        rs = self.get_multi(keys)
        return [rs.get(k) for k in keys]

    def set(self, key, value, time=0, compress=True):
        self._cache(key, value)
        return True

    def __getattr__(self, name):
        """
        通过链式操作访问不存在的属性的处理
        """
        if name in ('add', 'replace', 'delete', 'incr', 'decr', 'prepend',
                    'append'):
            def func(key, *args, **kwargs):
                self.dataset.pop(key, None)
                return True

            return func
        elif name in ('append_multi', 'prepend_multi', 'delete_multi'):
            def func2(keys, *args, **kwargs):
                for k in keys:
                    self.dataset.pop(k, None)
                return True

            return func2
        raise AttributeError(name)


lc = LocalCache()

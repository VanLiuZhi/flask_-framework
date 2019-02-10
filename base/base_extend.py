#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:   LiuZhi
@time:     2019-01-11 23:45
@contact:  vanliuzhi@qq.com
@software: PyCharm

MySQL数据库相关扩展
"""

import functools
import hashlib
from datetime import datetime

from sqlalchemy import (
    Column, DateTime, Integer, event, inspect)
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm.interfaces import MapperOption
from sqlalchemy.orm.attributes import get_history
from sqlalchemy.ext.declarative import declared_attr
from dogpile.cache.region import make_region
from dogpile.cache.api import NO_VALUE
from flask import abort
from flask_sqlalchemy import (
    SQLAlchemy, Model, BaseQuery, DefaultMeta, _QueryProperty)
from flask_security import Security

from flask_app.utils import get_config
from .redis_db import PropsMixin, PropsItem

REDIS_URL = get_config().REDIS_URL  # 缓存服务地址


def md5_key_mangler(key):
    if key.startswith('SELECT '):
        key = hashlib.md5(key.encode('ascii')).hexdigest()
    return key


def memoize(obj):
    """
    py3 functools.lru_cache 的实现
    """
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]

    return memoizer


# 配置缓存服务，使用Redis
regions = dict(
    default=make_region(key_mangler=md5_key_mangler).configure(
        'dogpile.cache.redis',
        arguments={
            'url': REDIS_URL,
        }
    )
)


class CachingQuery(BaseQuery):
    def __init__(self, regions, entities, *args, **kw):
        self.cache_regions = regions
        BaseQuery.__init__(self, entities=entities, *args, **kw)

    def __iter__(self):
        if hasattr(self, '_cache_region'):
            return self.get_value(
                createfunc=lambda: list(BaseQuery.__iter__(self)))
        else:
            return BaseQuery.__iter__(self)

    def _get_cache_plus_key(self):
        dogpile_region = self.cache_regions[self._cache_region.region]
        if self._cache_region.cache_key:
            key = self._cache_region.cache_key
        else:
            key = _key_from_query(self)
        return dogpile_region, key

    def invalidate(self):
        dogpile_region, cache_key = self._get_cache_plus_key()
        dogpile_region.delete(cache_key)

    def get_value(self, merge=True, createfunc=None,
                  expiration_time=None, ignore_expiration=False):
        dogpile_region, cache_key = self._get_cache_plus_key()

        assert not ignore_expiration or not createfunc, \
            "Can't ignore expiration and also provide createfunc"

        if ignore_expiration or not createfunc:
            cached_value = dogpile_region.get(
                cache_key, expiration_time=expiration_time,
                ignore_expiration=ignore_expiration)
        else:
            cached_value = dogpile_region.get_or_create(
                cache_key,
                createfunc,
                expiration_time=expiration_time)

        if cached_value is NO_VALUE:
            raise KeyError(cache_key)
        if merge:
            cached_value = self.merge_result(cached_value, load=False)

        return cached_value

    def set_value(self, value):
        dogpile_region, cache_key = self._get_cache_plus_key()
        dogpile_region.set(cache_key, value)


def query_callable(regions, query_cls=CachingQuery):
    return functools.partial(query_cls, regions)


def _key_from_query(query, qualifier=None):
    stmt = query.with_labels().statement
    compiled = stmt.compile()
    params = compiled.params

    return " ".join(
        [str(compiled)] +
        [str(params[k]) for k in sorted(params)])


class FromCache(MapperOption):
    propagate_to_loaders = False

    def __init__(self, region="default", cache_key=None):
        self.region = region
        self.cache_key = cache_key

    def process_query(self, query):
        query._cache_region = self


class Query(object):
    def __init__(self, entities):
        self.entities = entities

    def __iter__(self):
        return self.entities

    def first(self):
        try:
            return self.entities.__next__()
        except StopIteration:
            return None

    def all(self):
        return list(self.entities)


class Cache(object):
    def __init__(self, model, regions, label):
        self.model = model
        self.regions = regions
        self.label = label
        self.pk = getattr(model, 'cache_pk', 'id')

    def get(self, pk):
        return self.model.query.options(self.from_cache(pk=pk)).get(pk)

    def count(self, **kwargs):
        if kwargs:
            if len(kwargs) > 1:
                raise TypeError(
                    'filter accept only one attribute for filtering')
            key, value = list(kwargs.items())[0]
            if key not in self._attrs():
                raise TypeError('%s does not have an attribute %s' % self, key)

        cache_key = self._count_cache_key(**kwargs)
        r = self.regions[self.label]
        count = r.get(cache_key)

        if count is NO_VALUE:
            count = self.model.query.filter_by(**kwargs).count()
            r.set(cache_key, count)
        return count

    def filter(self, order_by='asc', offset=None, limit=None, **kwargs):
        if kwargs:
            if len(kwargs) > 1:
                raise TypeError(
                    'filter accept only one attribute for filtering')
            key, value = list(kwargs.items())[0]
            if key not in self._attrs():
                raise TypeError('%s does not have an attribute %s' % self, key)

        cache_key = self._cache_key(**kwargs)
        r = self.regions[self.label]
        pks = r.get(cache_key)

        if pks is NO_VALUE:
            pks = [o.id for o in self.model.query.filter_by(**kwargs)
                .with_entities(getattr(self.model, self.pk))]
            r.set(cache_key, pks)

        if order_by == 'desc':
            pks.reverse()

        if offset is not None:
            pks = pks[offset:]

        if limit is not None:
            pks = pks[:limit]

        keys = [self._cache_key(id) for id in pks]
        return Query(self.gen_entities(pks, r.get_multi(keys)))

    def gen_entities(self, pks, objs):
        for pos, obj in enumerate(objs):
            if obj is NO_VALUE:
                yield self.get(pks[pos])
            else:
                yield obj[0]

    def flush(self, key):
        self.regions[self.label].delete(key)

    @memoize
    def _attrs(self):
        return [a.key for a in inspect(self.model).attrs if a.key != self.pk]

    @memoize
    def from_cache(self, cache_key=None, pk=None):
        if pk:
            cache_key = self._cache_key(pk)
        return FromCache(self.label, cache_key)

    @memoize
    def _count_cache_key(self, pk="all", **kwargs):
        return self._cache_key(pk, **kwargs) + '_count'

    @memoize
    def _cache_key(self, pk="all", **kwargs):
        q_filter = "".join("%s=%s" % (k, v)
                           for k, v in kwargs.items()) or self.pk
        return "%s.%s[%s]" % (self.model.__tablename__, q_filter, pk)

    def _flush_all(self, obj):
        for attr in self._attrs():
            added, unchanged, deleted = get_history(obj, attr)
            for value in list(deleted) + list(added):
                self.flush(self._cache_key(**{attr: value}))
        for key in (self._cache_key(), self._cache_key(getattr(obj, self.pk)),
                    self._count_cache_key(),
                    self._count_cache_key(getattr(obj, self.pk))):
            self.flush(key)


class BindDBPropertyMixin(object):
    def __init__(cls, name, bases, d):
        super(BindDBPropertyMixin, cls).__init__(name, bases, d)
        db_columns = []
        # 这个d是每个模型类的属性字典，应用启动初始化数据就会执行到这里，这样实现了对每个模型类的定制
        # 下面代码从模型类的属性中取出键值对，v就是类属性的值，
        # 这里判断使用PropsItem实例作为字段的模型将添加_db_columns属性
        for k, v in d.items():
            if isinstance(v, PropsItem):
                # k 为字段名称，v是实例对象
                db_columns.append((k, v.default))
        setattr(cls, '_db_columns', db_columns)


class CombinedMeta(BindDBPropertyMixin, DefaultMeta):
    """
    具体实现参考flask_sqlalchemy.DefaultMeta
    """
    pass


class BaseModel(PropsMixin, Model):
    cache_label = "default"
    cache_regions = regions
    query_class = query_callable(regions)

    __table_args__ = {'mysql_charset': 'utf8mb4'}

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=None)

    def get_uuid(self):
        return '/bran/{0.__class__.__name__}/{0.id}'.format(self)

    def __repr__(self):
        return '<{0} id: {1}>'.format(self.__class__.__name__, self.id)

    @declared_attr
    def cache(cls):
        return Cache(cls, cls.cache_regions, cls.cache_label)

    @classmethod
    def get(cls, id):
        return cls.query.get(id)

    @classmethod
    def get_or_404(cls, ident):
        rv = cls.get(ident)
        if rv is None:
            abort(404)
        return rv

    @classmethod
    def get_multi(cls, ids):
        return [cls.cache.get(id) for id in ids]

    def url(self):
        return '/{}/{}/'.format(self.__class__.__name__.lower(), self.id)

    def to_dict(self):
        columns = self.__table__.columns.keys() + ['kind']
        dct = {key: getattr(self, key, None) for key in columns}
        return dct

    @staticmethod
    def _flush_insert_event(mapper, connection, target):
        target._flush_event(mapper, connection, target)
        if hasattr(target, 'kind'):
            from handler.tasks import reindex
            reindex.delay(target.id, target.kind, op_type='create')
        target.__flush_insert_event__(target)

    @staticmethod
    def _flush_after_update_event(mapper, connection, target):
        target._flush_event(mapper, connection, target)
        if hasattr(target, 'kind'):
            from handler.tasks import reindex
            reindex.delay(target.id, target.kind, op_type='update')
        target.__flush_after_update_event__(target)

    @staticmethod
    def _flush_before_update_event(mapper, connection, target):
        target._flush_event(mapper, connection, target)
        target.__flush_before_update_event__(target)

    @staticmethod
    def _flush_delete_event(mapper, connection, target):
        target._flush_event(mapper, connection, target)
        if hasattr(target, 'kind'):
            from handler.tasks import reindex
            reindex.delay(target.id, target.kind, op_type='delete')
        target.__flush_delete_event__(target)

    @staticmethod
    def _flush_event(mapper, connection, target):
        target.cache._flush_all(target)
        target.__flush_event__(target)

    @classmethod
    def __flush_event__(cls, target):
        pass

    @classmethod
    def __flush_delete_event__(cls, target):
        pass

    @classmethod
    def __flush_insert_event__(cls, target):
        pass

    @classmethod
    def __flush_after_update_event__(cls, target):
        pass

    @classmethod
    def __flush_before_update_event__(cls, target):
        pass

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, 'after_delete', cls._flush_delete_event)
        event.listen(cls, 'after_update', cls._flush_after_update_event)
        event.listen(cls, 'before_update', cls._flush_before_update_event)
        event.listen(cls, 'after_insert', cls._flush_insert_event)


class UnLockedAlchemy(SQLAlchemy):
    def make_declarative_base(self, model, metadata=None):
        if not isinstance(model, DeclarativeMeta):
            model = declarative_base(
                cls=model,
                name='Model',
                metadata=metadata,
                metaclass=CombinedMeta
            )

        if metadata is not None and model.metadata is not metadata:
            model.metadata = metadata

        if not getattr(model, 'query_class', None):
            model.query_class = self.Query

        model.query = _QueryProperty(self)
        return model

    def apply_driver_hacks(self, app, info, options):
        if 'isolation_level' not in options:
            options['isolation_level'] = 'READ COMMITTED'
        return super(UnLockedAlchemy, self).apply_driver_hacks(
            app, info, options)


security = Security()
db = UnLockedAlchemy(model_class=BaseModel)

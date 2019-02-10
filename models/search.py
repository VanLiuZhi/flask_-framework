from collections import defaultdict

from elasticsearch_dsl import Document, Integer, Text, Boolean, Q, Keyword, SF, Date
from elasticsearch_dsl.connections import connections
from elasticsearch.helpers import parallel_bulk
from elasticsearch.exceptions import ConflictError
from flask_sqlalchemy import Pagination

from base.mc import rdb, cache

from flask_app.utils import get_config
from models.consts import K_POST, ONE_HOUR
from models.core import Post

CONFIG = get_config()
ES_HOSTS, PER_PAGE = CONFIG.ES_HOSTS, CONFIG.PER_PAGE

connections.create_connection(hosts=ES_HOSTS)

ITEM_MC_KEY = 'core:search:{}:{}'
POST_IDS_BY_TAG_MC_KEY = 'core:search:post_ids_by_tag:%s:%s:%s:%s'
SEARCH_FIELDS = ['title^10', 'tags^5', 'content^2']
TARGET_MAPPER = {
    K_POST: Post
}

gauss_sf = SF('gauss', created_at={
    'origin': 'now', 'offset': '7d', 'scale': '10d'
})

score_sf = SF('script_score', script={
    'lang': 'painless',
    'inline': ("doc['n_likes'].value * 2 + doc['n_collects'].value")
})


def get_item_data(item):
    """
    组合item对象的数据，这里的item是通过feedparser抓取来的
    """
    try:
        content = item.content
    except AttributeError:
        content = ''

    try:
        tags = [tag.name for tag in item.tags]
    except AttributeError:
        tags = []

    return {
        'id': item.id,
        'tags': tags,
        'content': content,
        'title': item.title,
        'kind': item.kind,
        'n_likes': item.n_likes,
        'n_comments': item.n_comments,
        'n_collects': item.n_collects,
    }


class Item(Document):
    id = Integer()
    title = Text()
    kind = Integer()
    content = Text()
    n_likes = Integer()
    n_collects = Integer()
    n_comments = Integer()
    can_show = Boolean()
    created_at = Date()
    tags = Text(fields={'raw': Keyword()})

    class Index:
        name = 'test'

    @classmethod
    def add(cls, item):
        obj = cls(**get_item_data(item))
        obj.save()
        obj.clear_mc(item.id, item.kind)
        return obj

    @classmethod
    @cache(ITEM_MC_KEY.format('{id}', '{kind}'))
    def get(cls, id, kind):
        s = cls.search()
        s.query = Q('bool', must=[Q('term', id=id),
                                  Q('term', kind=kind)])
        rs = s.execute()
        if rs:
            return rs.hits[0]

    @classmethod
    def clear_mc(cls, id, kind):
        rdb.delete(ITEM_MC_KEY.format(id, kind))

    @classmethod
    def delete(cls, item):
        rs = cls.get(item.id, item.kind)
        if rs:
            super(cls, rs).delete()
            cls.clear_mc(item.id, item.kind)
            return True
        return False

    @classmethod
    def update_item(cls, item):
        obj = cls.get(item.id, item.kind)
        if obj is None:
            return cls.add(item)
        if not obj:
            return

        kw = get_item_data(item)

        try:
            obj.update(**kw)
        except ConflictError:
            obj.clear_mc(item.id, item.kind)
            obj = cls.get(item.id, item.kind)
            obj.update(**kw)
        obj.clear_mc(item.id, item.kind)
        return True

    @classmethod
    def get_es(cls):
        """
        获取客户端
        """
        search = cls.search()
        return connections.get_connection(search._using)

    @classmethod
    def bulk_update(cls, items, chunk_size=5000, op_type='update', **kwargs):
        """
        批量更新，
        """
        index = cls._index._name # 当前类返回 test
        type = cls._doc_type.name # 当前类返回 doc，继承的是Document

        objects = ({
            '_op_type': op_type,
            '_id': f'{doc.id}_{doc.kind}',
            '_index': index,
            '_type': type,
            '_source': doc.to_dict()
        } for doc in items)
        client = cls.get_es()
        rs = list(parallel_bulk(client, objects,
                                chunk_size=chunk_size, **kwargs))
        for item in items:
            cls.clear_mc(item.id, item.kind)
        return rs

    @classmethod
    def new_search(cls, query, page, order_by=None, per_page=PER_PAGE):
        """
        创建一个查询实例，查询结果并分页返回，这里的query就是查询参数
        """
        s = cls.search()
        s = s.query('multi_match', query=query,
                    fields=SEARCH_FIELDS) # 设置搜索规则，SEARCH_FIELDS为匹配的权重

        if page < 1:
            page = 1
        start = (page - 1) * PER_PAGE
        s = s.extra(**{'from': start, 'size': per_page})
        if order_by is not None:
            s = s.sort(order_by)
        # 这里是rs是搜索的Response对象，结果存在hits中，可以迭代对象
        rs = s.execute()
        dct = defaultdict(list) # 使用标准库来创建字典，可以实现get不存在的key的时候，返回空list
        for i in rs:
            dct[i.kind].append(i.id) # 分类数据，(由于当前只有一种类型数据，即post，不是很明显)

        items = []

        for kind, ids in dct.items():
            target_cls = TARGET_MAPPER.get(kind) # 通过TARGET_MAPPER决定要操作的模型对象，上面已经通过kind进行分类了
            if target_cls:
                items_ = target_cls.get_multi(ids)
                items.extend(items_)

        return Pagination(query, page, per_page, rs.hits.total, items)

    @classmethod
    @cache(POST_IDS_BY_TAG_MC_KEY % ('{tag}', '{page}', '{order_by}',
                                     '{per_page}'), ONE_HOUR)
    def get_post_ids_by_tag(cls, tag, page, order_by=None, per_page=PER_PAGE):
        s = cls.search()
        # s = s.query(Q('bool', must=Q('term', tags=tag)))
        s = s.query(Q('bool', must=Q('term', kind=K_POST)))
        start = (page - 1) * PER_PAGE
        if page < 1:
            page = 1
        start = (page - 1) * PER_PAGE
        s = s.extra(**{'from': start, 'size': per_page})
        if order_by is not None:
            if order_by == 'hot':
                s = s.query(Q('function_score', functions=[gauss_sf, score_sf]))  # noqa
            else:
                s = s.sort(order_by)
        rs = s.execute()
        ids = [obj.id for obj in rs]
        return Pagination(tag, page, per_page, rs.hits.total, ids)


if __name__ == '__main__':
    # res = Item.get(2, 1001)
    from flask_app.app import app
    with app.test_request_context():
        res = Item.new_search('python', page=1)

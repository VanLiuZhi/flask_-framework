#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:   LiuZhi
@time:     2019-01-13 23:16
@contact:  vanliuzhi@qq.com
@software: PyCharm
"""

from datetime import datetime
from html.parser import HTMLParser

import feedparser

from auto_app import app
from models.core import Post, PostTag, Tag, db
from models.search import Item


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def fetch(url):
    d = feedparser.parse(url)
    entries = d.entries

    posts = []

    for entry in entries:
        try:
            content = entry.content and entry.content[0].value
        except AttributeError:
            try:
                content = entry.summary
            except AttributeError:
                content = entry.title
        try:
            created_at = datetime.strptime(entry.published, '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            try:
                created_at = datetime.strptime(entry.published, '%Y-%m-%dT%H:%M:%S%fZ')
            except ValueError:
                created_at = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
        try:
            tags = entry.tags
        except AttributeError:
            tags = ['other']
        ok, post = Post.create_or_update(
            author_id=2, title=entry.title or 'other', orig_url=entry.link,
            content=strip_tags(content), created_at=created_at,
            tags=[tag.term for tag in tags if tag])
        if ok:
            posts.append(post)
            # Item.add(post)
    # 批量更新索引
    # Item.bulk_update(posts, op_type='create')


def main():
    with app.test_request_context():
        Item._index.delete(ignore=404)  # 删除Elasticsearch索引，销毁全部数据
        Item.init()
        for model in (Post, Tag, PostTag):
            model.query.delete()  # 数据库操作要通过SQLAlchemy，不要直接链接数据库操作
        db.session.commit()

        for site in ('https://imys.net/atom.xml', ):
            fetch(site)


if __name__ == '__main__':
    main()

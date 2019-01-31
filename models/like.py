#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:   LiuZhi
@time:     2019-01-13 23:24
@contact:  vanliuzhi@qq.com
@software: PyCharm
"""

from base.base_extend import db
from models.consts import K_POST, HOT_THRESHOLD
from base.mixin import ActionMixin


class LikeItem(ActionMixin, db.Model):
    __tablename__ = 'like_items'
    user_id = db.Column(db.Integer)
    target_id = db.Column(db.Integer)
    target_kind = db.Column(db.Integer)

    action_type = 'like'

    __table_args__ = (
        db.Index('idx_ti', target_id, target_kind, user_id),
    )


class LikeMixin:
    def like(self, user_id):
        item = LikeItem.get_by_target(user_id, self.id, self.kind)
        if item:
            return False
        ok, _ = LikeItem.create(user_id=user_id, target_id=self.id,
                                target_kind=self.kind)
        if ok and self.n_likes > HOT_THRESHOLD and self.kind == K_POST:
            from handler.tasks import add_to_activity_feed
            add_to_activity_feed.delay(self.target_id)
        return ok

    def unlike(self, user_id):
        item = LikeItem.get_by_target(user_id, self.id, self.kind)
        if item:
            item.delete()
            return True
        return False

    @property
    def n_likes(self):
        return int(LikeItem.get_count_by_target(self.id, self.kind))

    def is_liked_by(self, user_id):
        return LikeItem.is_action_by(user_id, self.id, self.kind)

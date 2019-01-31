#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:   LiuZhi
@time:     2019-01-13 23:10
@contact:  vanliuzhi@qq.com
@software: PyCharm
"""

from flask_app.app import app
from flask_migrate import Migrate

from base.base_extend import db


def include_object(object, name, type_, reflected, compare_to):
    """
    模型管理器include规则
    """
    if type_ == 'table' and name.startswith('social_auth'):
        return False
    return True


migrate = Migrate(app, db, include_object=include_object)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

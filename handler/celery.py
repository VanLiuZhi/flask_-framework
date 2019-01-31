#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:   LiuZhi
@time:     2019-01-18 21:43
@contact:  vanliuzhi@qq.com
@software: PyCharm
"""

from celery import Celery

from flask_app.settings import DevConfig

app = Celery('handler', include=['handler.tasks'])
app.config_from_object(DevConfig)

if __name__ == '__main__':
    app.start()

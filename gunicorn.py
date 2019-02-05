#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:   LiuZhi
@time:     2019-02-03 10:51
@contact:  vanliuzhi@qq.com
@software: PyCharm

about: https://github.com/benoitc/gunicorn/blob/master/examples/example_config.py

"""

import multiprocessing, datetime

bind = '0.0.0.0:5000'
backlog = 2048

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'
worker_connections = 1000
timeout = 60
keepalive = 2

#   spew - Install a trace function that spews every line of Python
#       that is executed when running the server. This is the
#       nuclear option.
#
#       True or False

spew = False

daemon = False
# raw_env = [
#     'DJANGO_SECRET_KEY=something',
#     'SPAM=eggs',
# ]
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# 日志配置

#  A string of "debug", "info", "warning", "error", "critical"
loglevel = 'debug'

now_time = datetime.datetime.now().strftime("%Y-%m-%d")
app_name = 'falsk_app'

accesslog = f'./logs/gunicorn/{app_name}-acess-{now_time}.log'
errorlog = f'./logs/gunicorn/{app_name}-error-{now_time}.log'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

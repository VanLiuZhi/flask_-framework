#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: LiuZhi
@contact: 1441765847@qq.com
@software: PyCharm
@file: logging_filter.py
@time: 2018-12-23 20:36
"""

import logging
import flask
from flask_logconfig import request_context_from_record


class UrlFormatter(logging.Formatter):
    def format(self, record):
        with request_context_from_record(record):
            print(flask.request.url)
            return flask.request.url


def url_formatter_factory():
    return UrlFormatter()

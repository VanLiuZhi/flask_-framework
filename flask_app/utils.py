#!/usr/bin/env python
# encoding: utf-8

"""
@author: LiuZhi
@contact: 1441765847@qq.com
@software: PyCharm
@file: utils.py
@time: 2018-12-22 23:25
"""

from flask import flash
from dotenv import find_dotenv, load_dotenv
import os


def flash_errors(form, category='warning'):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash('{0} - {1}'.format(getattr(form, field).label.text, error), category)


def get_env_value(key: str, default='') -> str:
    return os.environ.get(key, False) or default


def load_env_value():
    """
    load environment variable from .env
    """
    load_dotenv(find_dotenv())  # 相当于把.env配置的变量导入，pipenv依赖于python-dotenv


def test():
    from models.user import User, UserMixin
    return locals()

if __name__ == '__main__':

    print(load_env_value())
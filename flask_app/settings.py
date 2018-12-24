#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: LiuZhi
@contact: 1441765847@qq.com
@software: PyCharm
@file: settings.py
@time: 2018-12-22 23:19
"""

import datetime
import os


# from celery.schedules import crontab


class Config(object):
    """Base configuration."""

    SECRET_KEY = os.environ.get('USER', 'secret-key')  # get方法获取系统变量"USER"作为SECRET_KEY，默认值：secret-key
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))  # Parent directory
    ASSETS_DEBUG = False  # 是否编译静态文件，使用flask_assets模块
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc. Flask-Cache

    # 设置常量
    BAI_DU_URL = "http://https://www.baidu.com"

    # 指定日志的格式，按照每天一个日志文件的方式
    LOG_FILE = PROJECT_ROOT + '/logs/{0}-{1}.log'.format('flask_app', datetime.datetime.now().strftime("%Y-%m-%d"))

    LOGCONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'url': {
                'format': 'logconfig.logging_filter.url_formatter_factory'
            },
            'simple': {
                'format': '[%(levelname)s] %(module)s : %(message)s'
            },
            'verbose': {
                'format':
                    '[%(asctime)s] [%(levelname)s] %(module)s : %(message)s'
            }
        },
        # 'filters': {
        #     'email': {
        #         '()': 'flask_app.logging.RequestFilter'
        #     }
        # },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'simple',
                # 'stream': 'ext://sys.stderr'
            },
            'file': {
                'class': 'logging.FileHandler',
                'level': 'DEBUG',
                'formatter': 'verbose',
                'filename': LOG_FILE,
                'mode': 'a',
            }
        },
        'loggers': {
            '': {
                'handlers': ['file', 'console'],
                'level': 'DEBUG',
                'propagate': True,
            }
        }
    }

    def load_other_config(self, config_list: 'config class list'):
        for config_class in config_list:
            self.__dict__.update(config_class.load_config())


class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'
    DEBUG = False
    # mysql config
    SQLALCHEMY_RECORD_QUERIES = True
    FLASKY_DB_QUERY_TIMEOUT = 1
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root1234@localhost/flask_app?charset=utf8'
    SQLALCHEMY_POOL_SIZE = 100

    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    JSON_AS_ASCII = False
    multisubnetfailover = True


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root1234@localhost/flask_app?charset=utf8'
    SQLALCHEMY_POOL_SIZE = 100
    FLASKY_DB_QUERY_TIMEOUT = 1  # second level
    # mysql config，debug use
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = False
    SQLALCHEMY_ECHO = False

    DEBUG_TB_ENABLED = True
    ASSETS_DEBUG = True  # Don't bundle/minify static assets
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    JSON_AS_ASCII = False


class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    BCRYPT_LOG_ROUNDS = 4  # For faster tests; needs at least 4 to avoid "ValueError: Invalid rounds"
    WTF_CSRF_ENABLED = False  # Allows form testing

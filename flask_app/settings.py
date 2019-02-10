#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:   LiuZhi
@contact:  1441765847@qq.com
@software: PyCharm
@time:     2018-12-22 23:19

配置文件内容，使用类的形式配置，flask应用初始化读取配置文件(配置文件为一个对象即可，把对象的值复制给当前实例)
另外flask也提供from_envvar方法从环境变量加载数据
"""

import datetime
import os
from datetime import timedelta
from .utils import get_env_value


# from celery.schedules import crontab


class Config(object):
    """Base configuration."""

    # 基本环境设置
    SECRET_KEY = os.environ.get('USER', 'secret-key')  # get方法获取系统变量"USER"作为SECRET_KEY，默认值：secret-key
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))  # Parent directory
    ASSETS_DEBUG = False  # 是否编译静态文件，使用flask_assets模块

    # debug工具设置
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # 缓存类型，如果要使用Redis等缓存服务，开发配置中覆盖即可
    CACHE_TYPE = 'simple'

    # 设置常量
    BAI_DU_URL = "http://https://www.baidu.com"

    # 日志配置，每天生成一个日志文件
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
        # 'filters': {
        #     'email': {
        #         '()': 'flask_app.logging.RequestFilter'
        #     }
        # },
    }

    # 邮件Flask-Mail configuration
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = True
    MAIL_USERNAME = '144176584@qq.com'
    MAIL_PASSWORD = ''
    MAIL_DEFAULT_SENDER = 'flask@example.com'

    # 时区配置
    CELERY_TIMEZONE = 'Asia/Shanghai'


class DevConfig(Config):
    """Development configuration."""

    # 基本配置
    ENV = 'dev'
    DEBUG = True
    WTF_CSRF_CHECK_DEFAULT = False # 全局取消CSRF校验

    # redis 配置
    REDIS_URL = 'redis://localhost:6379'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_TYPE = 'redis'

    # celery 配置
    BROKER_URL = 'pyamqp://developer:dev1234@localhost:5672'  # 使用RabbitMQ作为消息代理
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'  # 把任务结果存在了Redis
    CELERY_TASK_SERIALIZER = 'msgpack'  # 任务序列化和反序列化使用msgpack方案
    CELERY_RESULT_SERIALIZER = 'json'  # 读取任务结果一般性能要求不高，所以使用了可读性更好的JSON
    CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24  # 任务过期时间，不建议直接写86400，应该让这样的magic数字表述更明显
    CELERY_ACCEPT_CONTENT = ['json', 'msgpack']  # 指定接受的内容类型

    # celery 任务调度器
    CELERYBEAT_SCHEDULE = {
        'ptask': {
            # 'task': 'flask_app.celery_app.tasks.period_task',
            'task': 'flask_app.celery_app.task.period_task',
            'schedule': timedelta(seconds=5),
        },
    }

    # upload目录
    UPLOAD_FOLDER = os.path.join(Config.PROJECT_ROOT, 'permdir')

    # MySQL配置
    DATABASE_QUERY_TIMEOUT = 0.5
    FLASKY_DB_QUERY_TIMEOUT = 1  # second level

    SQLALCHEMY_RECORD_QUERIES = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root1234@localhost/starlight?charset=utf8mb4'


    # flask-security 配置
    SECURITY_CONFIRMABLE = True
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_TRACKABLE = True
    SECURITY_POST_REGISTER_VIEW = SECURITY_POST_RESET_VIEW = SECURITY_POST_CONFIRM_VIEW = 'account.landing'  # noqa
    SECURITY_PASSWORD_SALT = '234'

    SECURITY_EMAIL_SUBJECT_CONFIRM = '请确认邮件 -  头条'
    SECURITY_EMAIL_SUBJECT_REGISTER = '欢迎 - 头条'
    SECURITY_EMAIL_SUBJECT_PASSWORD_RESET = '重置密码 - 头条'
    SECURITY_EMAIL_SUBJECT_PASSWORD_CHANGE_NOTICE = '密码已改变 - 头条'
    SECURITY_EMAIL_SUBJECT_PASSWORD_NOTICE = '密码已被重置 - 头条'

    SECURITY_MSG_UNAUTHORIZED = ('你没有权限访问这个资源', 'error')
    SECURITY_MSG_PASSWORD_MISMATCH = ('密码不匹配', 'error')
    SECURITY_MSG_PASSWORD_RESET_EXPIRED = (
        ('You did not reset your password within %(within)s. '
         'New instructions have been sent to %(email)s.'), 'error')
    SECURITY_MSG_DISABLED_ACCOUNT = ('账号被禁用了.', 'error')
    SECURITY_MSG_INVALID_EMAIL_ADDRESS = ('邮箱地址错误', 'error')
    SECURITY_MSG_PASSWORD_INVALID_LENGTH = ('错误的密码长度', 'error')
    SECURITY_MSG_PASSWORD_IS_THE_SAME = ('新密码要和旧密码不一致', 'error')
    SECURITY_MSG_EMAIL_NOT_PROVIDED = ('需要填写邮箱地址', 'error')
    SECURITY_MSG_ALREADY_CONFIRMED = ('邮箱已经被确认', 'info')
    SECURITY_MSG_PASSWORD_NOT_PROVIDED = ('需要输入密码', 'error')
    SECURITY_MSG_USER_DOES_NOT_EXIST = ('用户不存在或者密码错误', 'error')
    SECURITY_MSG_EMAIL_ALREADY_ASSOCIATED = ('%(email)s 已经被关联了', 'error')
    SECURITY_MSG_CONFIRMATION_REQUIRED = ('登录前请先邮箱确认', 'error')
    SECURITY_MSG_INVALID_PASSWORD = ('账号或者密码错误', 'error')
    SECURITY_MSG_RETYPE_PASSWORD_MISMATCH = ('2次密码输入不一致', 'error')
    SECURITY_USER_IDENTITY_ATTRIBUTES = ('email', 'name')

    SECURITY_CONFIRM_EMAIL_WITHIN = SECURITY_RESET_PASSWORD_WITHIN = '6 hours'

    # 第三方登录鉴权
    SOCIAL_AUTH_USER_MODEL = 'models.user.User'
    SOCIAL_AUTH_AUTHENTICATION_BACKENDS = (
        'social_core.backends.github.GithubOAuth2',
        'social_core.backends.weibo.WeiboOAuth2',
        'social_core.backends.weixin.WeixinOAuth2'
    )

    SOCIAL_AUTH_GITHUB_KEY = ''
    SOCIAL_AUTH_GITHUB_SECRET = ''
    SOCIAL_AUTH_WEIBO_KEY = ''
    SOCIAL_AUTH_WEIBO_SECRET = ''
    SOCIAL_AUTH_WEIBO_DOMAIN_AS_USERNAME = True
    SOCIAL_AUTH_WEIXIN_KEY = ''
    SOCIAL_AUTH_WEIXIN_SECRET = ''
    SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
    CLEAN_USERNAMES = False
    SOCIAL_AUTH_REMEMBER_SESSION_NAME = 'remember_me'
    SOCIAL_AUTH_FIELDS_STORED_IN_SESSION = ['keep']


    # 其它配置项，覆盖配置等
    DEBUG_TB_ENABLED = True
    ASSETS_DEBUG = True  # Don't bundle/minify static assets
    JSON_AS_ASCII = False
    TEMPLATES_AUTO_RELOAD = True

    ## 邮件服务
    FROM_USER = '1441765847@qq.com'
    EXMAIL_PASSWORD = get_env_value('EXMAIL_PASSWORD')

    ES_HOSTS = ['localhost']
    PER_PAGE = 2


class ProdConfig(Config):
    """Production configuration."""

    # 基本配置
    ENV = 'prod'
    DEBUG = False
    WTF_CSRF_CHECK_DEFAULT = False  # 全局取消CSRF校验

    # redis 配置
    REDIS_URL = 'redis://master_redis:6379'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_TYPE = 'redis'

    # celery 配置
    BROKER_URL = 'pyamqp://developer:dev1234@rabbitmq:5672'  # 使用RabbitMQ作为消息代理
    CELERY_RESULT_BACKEND = 'redis://master_redis:6379/1'  # 把任务结果存在了Redis
    CELERY_TASK_SERIALIZER = 'msgpack'  # 任务序列化和反序列化使用msgpack方案
    CELERY_RESULT_SERIALIZER = 'json'  # 读取任务结果一般性能要求不高，所以使用了可读性更好的JSON
    CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24  # 任务过期时间，不建议直接写86400，应该让这样的magic数字表述更明显
    CELERY_ACCEPT_CONTENT = ['json', 'msgpack']  # 指定接受的内容类型

    # celery 任务调度器
    CELERYBEAT_SCHEDULE = {
        'ptask': {
            # 'task': 'flask_app.celery_app.tasks.period_task',
            'task': 'flask_app.celery_app.task.period_task',
            'schedule': timedelta(seconds=5),
        },
    }

    # upload目录
    UPLOAD_FOLDER = os.path.join(Config.PROJECT_ROOT, 'permdir')

    # MySQL配置
    DATABASE_QUERY_TIMEOUT = 0.5
    FLASKY_DB_QUERY_TIMEOUT = 1  # second level

    SQLALCHEMY_RECORD_QUERIES = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root1234@masterdb/starlight?charset=utf8mb4'

    # flask-security 配置
    SECURITY_CONFIRMABLE = True
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_TRACKABLE = True
    SECURITY_POST_REGISTER_VIEW = SECURITY_POST_RESET_VIEW = SECURITY_POST_CONFIRM_VIEW = 'account.landing'  # noqa
    SECURITY_PASSWORD_SALT = '234'

    SECURITY_EMAIL_SUBJECT_CONFIRM = '请确认邮件 -  头条'
    SECURITY_EMAIL_SUBJECT_REGISTER = '欢迎 - 头条'
    SECURITY_EMAIL_SUBJECT_PASSWORD_RESET = '重置密码 - 头条'
    SECURITY_EMAIL_SUBJECT_PASSWORD_CHANGE_NOTICE = '密码已改变 - 头条'
    SECURITY_EMAIL_SUBJECT_PASSWORD_NOTICE = '密码已被重置 - 头条'

    SECURITY_MSG_UNAUTHORIZED = ('你没有权限访问这个资源', 'error')
    SECURITY_MSG_PASSWORD_MISMATCH = ('密码不匹配', 'error')
    SECURITY_MSG_PASSWORD_RESET_EXPIRED = (
        ('You did not reset your password within %(within)s. '
         'New instructions have been sent to %(email)s.'), 'error')
    SECURITY_MSG_DISABLED_ACCOUNT = ('账号被禁用了.', 'error')
    SECURITY_MSG_INVALID_EMAIL_ADDRESS = ('邮箱地址错误', 'error')
    SECURITY_MSG_PASSWORD_INVALID_LENGTH = ('错误的密码长度', 'error')
    SECURITY_MSG_PASSWORD_IS_THE_SAME = ('新密码要和旧密码不一致', 'error')
    SECURITY_MSG_EMAIL_NOT_PROVIDED = ('需要填写邮箱地址', 'error')
    SECURITY_MSG_ALREADY_CONFIRMED = ('邮箱已经被确认', 'info')
    SECURITY_MSG_PASSWORD_NOT_PROVIDED = ('需要输入密码', 'error')
    SECURITY_MSG_USER_DOES_NOT_EXIST = ('用户不存在或者密码错误', 'error')
    SECURITY_MSG_EMAIL_ALREADY_ASSOCIATED = ('%(email)s 已经被关联了', 'error')
    SECURITY_MSG_CONFIRMATION_REQUIRED = ('登录前请先邮箱确认', 'error')
    SECURITY_MSG_INVALID_PASSWORD = ('账号或者密码错误', 'error')
    SECURITY_MSG_RETYPE_PASSWORD_MISMATCH = ('2次密码输入不一致', 'error')
    SECURITY_USER_IDENTITY_ATTRIBUTES = ('email', 'name')

    SECURITY_CONFIRM_EMAIL_WITHIN = SECURITY_RESET_PASSWORD_WITHIN = '6 hours'

    # 第三方登录鉴权
    SOCIAL_AUTH_USER_MODEL = 'models.user.User'
    SOCIAL_AUTH_AUTHENTICATION_BACKENDS = (
        'social_core.backends.github.GithubOAuth2',
        'social_core.backends.weibo.WeiboOAuth2',
        'social_core.backends.weixin.WeixinOAuth2'
    )

    SOCIAL_AUTH_GITHUB_KEY = ''
    SOCIAL_AUTH_GITHUB_SECRET = ''
    SOCIAL_AUTH_WEIBO_KEY = ''
    SOCIAL_AUTH_WEIBO_SECRET = ''
    SOCIAL_AUTH_WEIBO_DOMAIN_AS_USERNAME = True
    SOCIAL_AUTH_WEIXIN_KEY = ''
    SOCIAL_AUTH_WEIXIN_SECRET = ''
    SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
    CLEAN_USERNAMES = False
    SOCIAL_AUTH_REMEMBER_SESSION_NAME = 'remember_me'
    SOCIAL_AUTH_FIELDS_STORED_IN_SESSION = ['keep']

    # 其它配置项，覆盖配置等
    DEBUG_TB_ENABLED = False
    ASSETS_DEBUG = True  # Don't bundle/minify static assets
    JSON_AS_ASCII = False
    TEMPLATES_AUTO_RELOAD = True

    ## 邮件服务
    FROM_USER = '1441765847@qq.com'
    EXMAIL_PASSWORD = get_env_value('EXMAIL_PASSWORD')

    ES_HOSTS = ['elasticsearch_server']
    PER_PAGE = 2


class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    BCRYPT_LOG_ROUNDS = 4  # For faster tests; needs at least 4 to avoid "ValueError: Invalid rounds"
    WTF_CSRF_ENABLED = False  # Allows form testing


if __name__ == '__main__':
    print(Config.PROJECT_ROOT)
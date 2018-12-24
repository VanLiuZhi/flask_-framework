#!/usr/bin/env python
# encoding: utf-8

"""
@author: LiuZhi
@contact: 1441765847@qq.com
@software: PyCharm
@file: auto_app.py
@time: 2018-12-23 17:07
"""

from flask_app.app import create_app
from flask_script import Manager
from flask_app.settings import DevConfig, ProdConfig
from flask.helpers import get_debug_flag
from flask_app.services_config import RedisConfig

CONFIG = DevConfig if get_debug_flag() else ProdConfig
config = CONFIG()
config.load_other_config([RedisConfig])
print(dir(config))
app = create_app(config)
manager = Manager(app)

if __name__ == '__main__':
    manager.run()
    # app.run(host='0.0.0.0', port=5000, debug=True)

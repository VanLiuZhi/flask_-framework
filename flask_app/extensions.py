#!/usr/bin/env python
# encoding: utf-8

"""
@author: LiuZhi
@contact: 1441765847@qq.com
@software: PyCharm
@file: extensions.py
@time: 2018-12-22 23:25
Extensions module. Each extension is initialized in the app factory located in app.py
"""

from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_logconfig import LogConfig
from flask_mail import Mail

# 可先创建实例，通过self.init_app方法完成初始化（using lazy instantiation）

csrf_protect = CSRFProtect()
login_manager = LoginManager()
debug_toolbar = DebugToolbarExtension()
# webpack = Webpack()
log_cfg = LogConfig()  # LOG
mail = Mail()

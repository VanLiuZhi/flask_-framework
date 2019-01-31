#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:   LiuZhi
@time:     2019-01-20 00:28
@contact:  vanliuzhi@qq.com
@software: PyCharm
"""

from flask import render_template, send_from_directory, abort, request
from flask.blueprints import Blueprint
from flask_security import login_required

index_bp = Blueprint('index', __name__, url_prefix='/index', template_folder='/templates')


@index_bp.route('/')
# @login_required
def index():
    return render_template('index.html')

#!/usr/bin/env python
# encoding: utf-8

"""
@author: LiuZhi
@contact: 1441765847@qq.com
@software: PyCharm
@file: app.py
@time: 2018-12-22 23:18
"""

from flask import Flask, render_template
import sys

import IPython
from IPython.terminal.ipapp import load_default_config
from traitlets.config.loader import Config
from social_flask_sqlalchemy.models import init_social
import click
from flask.cli import with_appcontext

# import public, user
from flask_app import commands
from flask_app.extensions import csrf_protect, debug_toolbar, login_manager, mail, log_cfg
from flask_app.utils import load_env_value
from flask_app.settings import DevConfig
from models.utils import load_models
from models.user import user_datastore
from forms.register import ExtendedLoginForm, ExtendedRegisterForm
from base.exmail import send_mail_task as _send_mail_task
from base.base_extend import db, security
from base.flask import Flask
from api_views.base.api import APIHandelView
from api_views.base.utils import ApiResult
from api_views.base.exceptions import ApiException
from api_views import post_api
from views.index import index_bp


def create_app(config_object):
    """An application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.
    :param config_object: The configuration object to use.
    """
    app = Flask('flask_app')
    print(__file__.split('/'))
    app.config.from_object(config_object)
    app.root_path = app.config['PROJECT_ROOT']
    pass
    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    # register_errorhandlers(app)
    return app


def register_extensions(app):
    """Register Flask extensions."""

    # 数据库
    db.init_app(app)
    load_models()
    # 用户模型扩展
    init_social(app, db.session)
    _state = security.init_app(app, user_datastore,
                               confirm_register_form=ExtendedRegisterForm,
                               login_form=ExtendedLoginForm)
    security._state = _state
    app.security = security
    security.send_mail_task(_send_mail_task)
    # other
    csrf_protect.init_app(app)
    login_manager.init_app(app)
    debug_toolbar.init_app(app)
    log_cfg.init_app(app)
    mail.init_app(app)

    app.add_url_rule('/user/<api_name>',
                     view_func=APIHandelView.as_view('follow'), methods=['POST', 'GET'])
    app.add_url_rule('/api/post/<api_name>',
                     view_func=post_api.PostAPI.as_view('post_api'), methods=['POST', 'GET'])
    return None


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(index_bp)
    # app.register_blueprint(user.views.blueprint)
    return None


def register_errorhandlers(app):
    """Register error handlers."""

    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, 'code', 500)
        return render_template('{0}.html'.format(error_code)), error_code

    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.lint)
    app.cli.add_command(commands.clean)
    app.cli.add_command(commands.urls)


# 从.env中加载环境变量
load_env_value()

CONFIG = DevConfig

app = create_app(CONFIG)


# 接口异常处理，raise ApiException() 触发接口异常
@app.errorhandler(ApiException)
def api_error_handler(error):
    return error.to_result()


# 响应码异常处理
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(500)
def error_handler(error):
    if hasattr(error, 'name'):
        status = error.code
        if status == 403:
            msg = '无权限'
        else:
            msg = error.name
    else:
        msg = error.message
        status = 500
    return ApiResult({'errmsg': msg, 'r': 1, 'status': status})


# ipython 交互环境，自动导入模型对象
@app.cli.command('ishell', short_help='Runs a IPython shell in the app context.')
@click.argument('ipython_args', nargs=-1, type=click.UNPROCESSED)
@with_appcontext
def ishell(ipython_args):
    from models.utils import load_models
    models_dict = load_models()
    if 'IPYTHON_CONFIG' in app.config:
        config = Config(app.config['IPYTHON_CONFIG'])
    else:
        config = load_default_config()
    user_ns = app.make_shell_context()
    user_ns.update(models_dict)
    config.TerminalInteractiveShell.banner1 = '''Python %s on %s
IPython: %s
App: %s%s
Instance: %s''' % (sys.version,
                   sys.platform,
                   IPython.__version__,
                   app.import_name,
                   app.debug and ' [debug]' or '',
                   app.instance_path)

    IPython.start_ipython(user_ns=user_ns, config=config, argv=ipython_args)


# social相关数据库创建命令
@app.cli.command()
@with_appcontext
def create_social_db():
    from social_flask_sqlalchemy import models as models_
    engine = db.get_engine()
    models_.PSABase.metadata.drop_all(engine)
    models_.PSABase.metadata.create_all(engine)
    click.echo('Create social DB Finished!')


# 初始化数据库
@app.cli.command()
def initdb():
    from social_flask_sqlalchemy import models as models_
    engine = db.get_engine()
    models_.PSABase.metadata.drop_all(engine)
    db.session.commit()
    db.drop_all()
    db.create_all()
    models_.PSABase.metadata.create_all(engine)
    click.echo('Init Finished!')

if __name__ == '__main__':
    print(__file__.split('/')[-3])

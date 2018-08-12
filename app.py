from flask import Flask,render_template,session,redirect,g
from models import db,UserInfo
import logging
from logging.handlers import RotatingFileHandler
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
import redis
from view_news import news_blueprint
from view_user import user_blueprint
from view_admin import admin_blueprint
import re


def create(config):
    app = Flask(__name__)

    # 加载配置
    app.config.from_object(config)

    # 初始化数据库连接
    db.init_app(app)

    # CSRF保护
    CSRFProtect(app)

    # 采用redis保存session
    Session(app)

    # 添加redis对象
    app.redis_cli = redis.StrictRedis(config.REDIS_HOST, config.REDIS_PORT, config.REDIS_DB)

    # 添加日志
    # 设置日志的记录等级
    logging.basicConfig(level=logging.DEBUG)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler(config.BASE_DIR + "/logs/news.log", maxBytes=1024 * 1024 * 100,backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)
    app.logger_xjzx = logging

    # 注册蓝图
    app.register_blueprint(news_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(admin_blueprint)

    # 处理404错误
    @app.errorhandler(404)
    def handle404(e):
        # 验证登陆
        if 'user_id' not in session:
            return redirect('/')
        user_id = session.get('user_id')
        g.user = UserInfo.query.get(user_id)
        return render_template('news/404.html',title='404')

    return app

    # 过滤掉数据中div标签
    # @app.template_filter('resub')
    # def re_sub(content):
    #     regex = r'<div.*?>'
    #     return re.sub(regex,'',content)
    #
    # app.add_template_filter(re_sub, 'resub')
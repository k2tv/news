from flask import Blueprint, request, g, jsonify
from flask import redirect, current_app
from flask import render_template
from flask import session
from datetime import datetime
import time,random
from utils.qcloud_cos import qlcoud_cos

from models import UserInfo, NewsInfo, NewsCategory, db

admin_blueprint = Blueprint('admin', __name__, url_prefix='/admin')


@admin_blueprint.route('/m/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('admin/login.html')
    # post请求，查询数据
    name = request.form.get('username')
    pwd = request.form.get('password')

    if not all([name, pwd]):
        return render_template('admin/login.html', msg='请填写用户名、密码')

    user = UserInfo.query.filter_by(mobile=name, isAdmin=True).first()
    if user:
        if user.check_pwd(pwd):
            # 登录成功
            session['admin_id'] = user.id
            return redirect('/admin/m')
        else:
            return render_template('admin/login.html', msg='密码错误')
    else:
        return render_template('admin/login.html', msg='用户名错误')


# @app.before_request
@admin_blueprint.before_request
def login_valid():
    # 当大部分视图都执行一段代码时，则将这段代码封装到请求勾子函数中
    # 排除小部分视图
    ignore_list = ['/admin/m/login', ]
    if request.path not in ignore_list:
        if 'admin_id' not in session:
            return redirect('/admin/m/login')
        g.user = UserInfo.query.get(session.get('admin_id'))


@admin_blueprint.route('/m')
def index():
    return render_template('admin/index.html')


@admin_blueprint.route('/logout')
def logout():
    del session['admin_id']
    return redirect('/admin/m/login')


# 用户统计
@admin_blueprint.route('/usercount')
def usercount():
    # 用户总数
    total_count = UserInfo.query.filter_by(isAdmin=False).count()

    now = datetime.now()

    # 用户月新增数：本月注册的用户数量
    month_first = datetime(now.year, now.month, 1)
    month_count = UserInfo.query. \
        filter_by(isAdmin=False). \
        filter(UserInfo.create_time >= month_first). \
        count()

    # 用户日新增数：今天注册的用户数量
    day_first = datetime(now.year, now.month, now.day)
    day_count = UserInfo.query. \
        filter_by(isAdmin=False). \
        filter(UserInfo.create_time >= day_first). \
        count()

    # 用户登录活跃数
    key = 'login' + now.strftime('%Y%m%d')
    redis_cli = current_app.redis_cli
    times = redis_cli.hkeys(key)
    counts = redis_cli.hvals(key)
    # 从redis中读取出来的数据，是bytes类型
    # print(times)[b'08:00', b'09:00', b'10:00'。。。]
    # print(counts)[b'356', b'410', b'284',。。。]

    # 将bytes转换成str  字符串.encode()   字节.decode()
    times = [item.decode() for item in times]
    # print(times)
    # 将bytes转换成int
    counts = [int(item) for item in counts]
    # print(counts)

    return render_template(
        'admin/user_count.html',
        total_count=total_count,
        month_count=month_count,
        day_count=day_count,
        times=times,
        counts=counts
    )


# 新闻审核列表
@admin_blueprint.route('/news_review')
def news_review1():
    return render_template('admin/news_review.html')


# 新闻审核列表数据
@admin_blueprint.route('/news_review2')
def news_review2():
    # 搜索关键字
    title = request.args.get('title')
    # 页码
    page = int(request.args.get('page', 1))

    type = int(request.args.get('type', 1))

    # 拼接查询语句
    query = NewsInfo.query
    if title:
        # 查询新闻标题包括指定字符串的数据
        query = query.filter(NewsInfo.title.contains(title))
    if type==2:
        pagination = query.order_by(NewsInfo.status.asc(), NewsInfo.id.desc()).paginate(page, 10, False)
    else:
        pagination = query.order_by(NewsInfo.id.desc()).filter_by(status=2).paginate(page, 10, False)
    # 获取当前页的数据
    news_list = pagination.items
    # 获取总页数
    total_page = pagination.pages

    # 最终返回json数据，需要将news_list转成字典
    news_list2 = []
    for news in news_list:
        news_list2.append({
            'id': news.id,
            'title': news.title,
            'create_time': news.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': news.status
        })

    return jsonify(news_list=news_list2, total_page=total_page)


@admin_blueprint.route('/type_list')
def type_list():
    return render_template('admin/news_type.html')


@admin_blueprint.route('/type_list_json')
def type_list_json():
    # 查询
    category_list = NewsCategory.query.all()

    # 对象转字典
    category_list2 = []
    for category in category_list:
        category_list2.append({
            'id': category.id,
            'name': category.name
        })

    # 返回json
    return jsonify(category_list=category_list2)


@admin_blueprint.route('/type_add', methods=['POST'])
def type_add():
    # 接收
    name = request.form.get('name')

    # 验证
    # 1.非空
    if not name:
        return jsonify(result=1)
    # 2.是否存在此名称
    if NewsCategory.query.filter_by(name=name).count() > 0:
        return jsonify(result=2)

    # 处理：添加
    category = NewsCategory()
    category.name = name
    db.session.add(category)
    db.session.commit()

    # 响应
    return jsonify(result=3)


@admin_blueprint.route('/type_edit/<int:category_id>', methods=['POST'])
def type_edit(category_id):
    # 参数：主键，name
    name = request.form.get('name')

    # 验证
    if not name:
        return jsonify(result=1)
    # 是否重复:如果未修改则提示请修改，如果修改为重复别称，则提示重复
    category = NewsCategory.query.get(category_id)
    # 未修改直接提交
    if category.name == name:
        return jsonify(result=2)
    # 修改后，如果名称重复，则返回
    if NewsCategory.query.filter_by(name=name).count() > 0:
        return jsonify(result=3)

    # 处理：修改
    category.name = name
    db.session.commit()

    # 响应
    return jsonify(result=4)


# 用户列表
@admin_blueprint.route('/user_list')
def user_list():
    page = int(request.args.get('page', 1))
    users = UserInfo.query.filter_by(isAdmin=False).paginate(page, 10, False)
    users_list = users.items
    users_list_pages = users.pages
    return render_template('admin/user_list.html', page=page, users_list=users_list, users_list_pages=users_list_pages)


# 新闻编辑
@admin_blueprint.route('/news_edit')
def news_edit():
    return render_template('admin/news_edit.html')

# 新闻编辑页面
@admin_blueprint.route('/news_edit/<int:news_id>', methods=['GET', 'POST'])
def news_edit_detail(news_id):
    if request.method == 'GET':
        news = NewsInfo.query.get(news_id)
        category = NewsCategory.query.all()
        return render_template('admin/news_edit_detail.html', news=news,category=category)

    title = request.form.get('title')
    category = request.form.get('category')
    summary = request.form.get('summary')
    content = request.form.get('content')
    pic = request.files.get('pic')
    news = NewsInfo.query.get(news_id)
    if pic:
        # 将图片上传到腾讯云
        nowTime = lambda: int(round(time.time() * 1000))
        file_name = str(random.random()) + str(nowTime()) + pic.filename
        qlcoud_cos.upload_img(pic, file_name)
        news.pic = file_name;

    news.title = title
    news.category_id = category
    news.summary = summary
    news.context = content
    db.session.commit()
    return redirect('/admin/news_edit')

# 新闻审核
@admin_blueprint.route('/news_review_detail/<int:news_id>', methods=['GET', 'POST'])
def news_review_detail(news_id):
    if request.method == 'GET':
        news = NewsInfo.query.get(news_id)
        category = NewsCategory.query.get(news.category_id)
        return render_template('admin/news_review_detail.html', news=news,category=category)
    # 更新数据
    action = int(request.form.get('action',2))
    reason = request.form.get('reason','reason')
    news = NewsInfo.query.get(news_id)
    # 用户文章数+1
    user = UserInfo.query.get(news.user_id)
    if action == 2:
        user.public_count += 1
    else:
        if news.status == 2:
            user.public_count -= 1
    # 新闻更新
    news.status = action
    news.reason = reason

    # 向数据库添加数据
    db.session.commit()

    return redirect('/admin/news_review')

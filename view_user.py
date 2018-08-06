from flask import Blueprint, session, make_response, request, jsonify, render_template, redirect, g, current_app
from utils.captcha.captcha import captcha
from models import UserInfo, db, NewsInfo, NewsCategory
import functools
import time
import random
from utils.qcloud_cos import qlcoud_cos
from utils.qcloudsms_py import qcloud_sms
import math

user_blueprint = Blueprint('user', __name__, url_prefix='/user')


def fun_login_valid(view_fun):
    @functools.wraps(view_fun)
    def fun_in(*args, **kwargs):
        # 验证登陆
        if 'user_id' not in session:
            return redirect('/')
        user_id = session.get('user_id')
        g.user = UserInfo.query.get(user_id)
        # 将视图函数的响应内容返回给客户端
        return view_fun(*args, **kwargs)

    return fun_in


@user_blueprint.route('/get_img_code')
def get_img_code():
    name, text, image = captcha.generate_captcha()
    session['image_code'] = text
    response = make_response(image)
    response.content_type = 'image/png'
    return response


@user_blueprint.route('/get_sms_code')
def get_sms_code():
    mobile = request.args.get('mobile')
    img_code = request.args.get('imgcode')
    if mobile and img_code:
        img_code_session = session.get('image_code')
        del session['image_code']

        if UserInfo.query.filter_by(mobile=mobile).first():
            return jsonify(res=4)

        if not img_code_session:
            return jsonify(res=3)
        if img_code.upper() != img_code_session.upper():
            print(img_code_session, img_code)
            return jsonify(res=2)
        # 处理
        # 1.生成随机的验证码
        smscode = str(random.randint(100000, 999999))
        # 2.保存验证码，用于后续验证
        session['sms_code'] = smscode
        # 3 腾讯接口
        qcloud_sms.send_sms_code(mobile, smscode)

        # 响应
        return jsonify(res=1)
    return jsonify(res=3)


@user_blueprint.route('/register', methods=['POST'])
def register():
    mobile = request.form.get('mobile')
    smscode = request.form.get('smscode')
    passwd = request.form.get('passwd')
    sms_session = session.get('sms_code')
    if smscode not in sms_session:
        return jsonify(res=1)
    del session['sms_code']
    if smscode == sms_session:
        user = UserInfo()
        if user.query.filter_by(mobile=mobile).count() > 0:
            return jsonify(res=3)
        user.password = passwd
        user.mobile = mobile
        user.nick_name = mobile
        db.session.add(user)
        db.session.commit()
        return jsonify(res=2)


@user_blueprint.route('/login', methods=['POST'])
def login():
    mobile = request.form.get('mobile')
    passwd = request.form.get('passwd')
    user = UserInfo().query.filter_by(mobile=mobile).first()
    if user and user.check_pwd(passwd):
        session['user_id'] = user.id;
        return jsonify(res=2, nick_name=user.nick_name, avatar=user.avatar)
    return jsonify(res=1)


@user_blueprint.route('/logout')
def logout():
    # 退出，就是删除登录成功时的标记
    if 'user_id' in session:
        del session['user_id']
    return jsonify(res=1)


@user_blueprint.route('/')
@fun_login_valid
def index():
    return render_template('news/user.html', title='用户中心')


# 修改用户信息
@user_blueprint.route('/user_base_info', methods=['GET', 'POST'])
@fun_login_valid
def user_base_info():
    if request.method == 'GET':
        return render_template('news/user_base_info.html')
    # TODO 修改用户信息
    signature = request.form.get('signature')
    nick_name = request.form.get('nick_name')
    gender = bool(int(request.form.get('gender')))
    g.user.signature = signature
    g.user.nick_name = nick_name
    g.user.gender = gender
    db.session.commit()
    return jsonify(res=1, nick_name=nick_name)


# 修改头像
@user_blueprint.route('/user_pic_info', methods=['GET', 'POST'])
@fun_login_valid
def user_pic_info():
    if request.method == 'GET':
        return render_template('news/user_pic_info.html')
    pic_file = request.files.get('avatar')
    user_id = session.get('user_id')
    f_name = str(user_id) + pic_file.filename
    pic_file.save(current_app.config.get('AVATAR_PATH') + f_name)
    user = g.user
    user.avatar = f_name
    db.session.commit()
    return jsonify(res=f_name)


# 修改密码
@user_blueprint.route('/user_pass_info', methods=['GET', 'POST'])
def user_pass_info():
    if request.method == 'GET':
        return render_template('news/user_pass_info.html')
    passwd_old = request.form.get('passwd_old')
    passwd_new = request.form.get('passwd_new')
    user_id = session.get('user_id')
    user = UserInfo().query.get(user_id)
    if user.check_pwd(passwd_old):
        user.password = passwd_new
        db.session.commit()
        del session['user_id']
        return jsonify(res=1)
    return jsonify(res=2)


# 新闻发布
@user_blueprint.route('/user_news_release', methods=['GET', 'POST'])
@fun_login_valid
def user_news_release():
    if request.method == 'GET':
        category_list = NewsCategory().query.all()
        return render_template('news/user_news_release.html', list=category_list)
    title = request.form.get('title')
    category_id = request.form.get('category_id')
    summary = request.form.get('summary')
    context = request.form.get('content')
    pic = request.files.get('pic')
    news = NewsInfo()
    if pic:
        # 将图片上传到腾讯云
        nowTime = lambda: int(round(time.time() * 1000))
        file_name = str(random.random()) + str(nowTime()) + pic.filename
        qlcoud_cos.upload_img(pic, file_name)
        news.pic = file_name;
    # 向数据库添加数据
    news.title = title
    news.category_id = category_id
    news.summary = summary
    news.context = context
    news.user_id = g.user.id;

    db.session.add(news)
    db.session.commit()

    return jsonify(res=1)


# 我的关注
@user_blueprint.route('/user_follow')
def user_follow():
    return render_template('news/user_follow.html')

# 新闻列表
@user_blueprint.route('/user_news_list')
@fun_login_valid
def user_news_list():
    current_page = int(request.args.get('page', 1))
    news_list = NewsInfo.query.order_by('id desc').filter_by(user_id=g.user.id).paginate(current_page, 10, False)
    news_list_items = news_list.items
    total_page = news_list.pages
    return render_template('news/user_news_list.html', news_list=news_list_items, total_page=total_page,
                           current_page=current_page)

# 收藏列表
@user_blueprint.route('/user_collection')
@fun_login_valid
def user_collection():
    current_page = int(request.args.get('page', 1))
    item_num = 8
    news_list = g.user.news_collect.all()[::-1]
    news_total = len(news_list)
    news_list_items = news_list[(current_page-1)*item_num:(current_page-1)*item_num+item_num]
    total_page = math.ceil(news_total/item_num)


    return render_template('news/user_collection.html', news_list=news_list_items, total_page=total_page,
                           current_page=current_page)
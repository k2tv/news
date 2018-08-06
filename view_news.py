from flask import Blueprint, render_template, session, g, request, send_from_directory, current_app, jsonify, abort
from models import db, UserInfo, NewsInfo, NewsCategory, NewsComment
import re
import functools
import os
import ifeng
from threading import Thread

news_blueprint = Blueprint('news', __name__)


# 验证登陆
def func_check_login(func):
    @functools.wraps(func)
    def func_in(*args, **kwargs):
        if 'user_id' in session:
            user_id = session.get('user_id')
            g.user = UserInfo.query.get(user_id)
        return func(*args, **kwargs)

    return func_in


# 首页
@news_blueprint.route('/')
@func_check_login
def index():
    pagination = get_news_list(1, 1)
    news_list = pagination.items
    click_list = get_click_list()
    category_list = get_category()
    if checkMobile(request):
        return render_template('mobile/index.html')
    return render_template('news/index.html', title='首页', news_list=news_list, click_list=click_list,
                           category_list=category_list)


# 根据类型和页数获取新闻列表
def get_news_list(page, category_id):
    return NewsInfo.query.order_by(NewsInfo.id.desc()).filter_by(category_id=category_id,status=2).paginate(page, 5, False)


# 根据类型和页数获取新闻列表 视图
@news_blueprint.route('/get_news_list_other_category')
def get_news_list_other_category():
    page = int(request.args.get('page', 1))
    category_id = int(request.args.get('category_id', 1))
    pagination = get_news_list(page, category_id)
    news_list = pagination.items
    list = []
    for news in news_list:
        list.append({
            'id': news.id,
            'pic': news.pic_url,
            'title': news.title,
            'summary': news.summary,
            'user_id': news.user.id,
            'avatar': news.user.avatar,
            'nick_name': news.user.nick_name,
            # python中的Datetime类型有个方法strftime()日期格式化，转成字符串
            'create_time': news.create_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    total_page = pagination.pages
    return jsonify(news_list=list, total_page=total_page)


# 点击排行列表
def get_click_list():
    return NewsInfo.query.order_by(NewsInfo.click_count.desc()).filter_by(status=2)[:9]


# 分类菜单信息列表
def get_category():
    return NewsCategory.query.all()


# 新闻详情
@news_blueprint.route('/detail/<int:news_id>.html')
@func_check_login
def detail(news_id):
    news = NewsInfo.query.get(news_id)
    if news:
        click_list = get_click_list()
        news.click_count += 1
        db.session.commit()
        public_news_count = NewsInfo.query.filter_by(status=2,user_id=news.user.id).count()
        if checkMobile(request):
            return render_template('mobile/detail.html', title='详情')
        return render_template('news/detail.html', title=news.title, news=news, click_list=click_list,public_news_count=public_news_count)
    else:
        abort(404)


# 作者详情
@news_blueprint.route('/author/<int:user_id>.html')
@func_check_login
def author(user_id):
    page = int(request.args.get('page', 1))
    user_info = UserInfo.query.get(user_id)
    if user_info:
        news_info_pagination = NewsInfo.query.order_by(NewsInfo.id.desc()).filter_by(user_id=user_id).paginate(page, 10,
                                                                                                               False)
        news_info_items = news_info_pagination.items
        news_info_total_page = news_info_pagination.pages
        return render_template('news/other.html', user_info=user_info, news_info_items=news_info_items,
                               current_page=page,
                               total_page=news_info_total_page,title=user_info.nick_name)
    else:
        abort(404)


# 小图标
@news_blueprint.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(current_app.root_path, 'static/news/images'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


# 收藏文章
@news_blueprint.route('/db_user_news')
def db_user_news():
    if 'user_id' not in session:
        abort(404)
    news_id = request.args.get('news_id')
    news_item = NewsInfo.query.get(news_id)
    user = UserInfo.query.get(session['user_id'])
    if news_item in user.news_collect:
        user.news_collect.remove(news_item)
    else:
        user.news_collect.append(news_item)
    db.session.commit()
    return jsonify(res=1)

# 添加评论
@news_blueprint.route('/comment_add', methods=['POST'])
def comment_add():
    # 接收
    msg = request.form.get('msg')
    news_id = request.form.get('news_id')
    # 如果是评论则不传递此数据，如果是回复，则传递此数据
    comment_id = int(request.form.get('comment_id', 0))

    # 验证
    # 1.非空
    if not all([msg, news_id]):
        return jsonify(result=1)
    # 2.是否登录
    if 'user_id' not in session:
        return jsonify(result=2)

    # 处理：添加
    comment = NewsComment()
    comment.msg = msg
    comment.news_id = int(news_id)
    comment.user_id = session.get('user_id')

    # 判断是否有评论编号，如果有则添加
    # 添加评论时，不传递此参数
    # 添加回复时，传递此参数
    if comment_id > 0:
        comment.comment_id = comment_id
    db.session.add(comment)
    db.session.commit()

    # 响应
    return jsonify(result=3)

# 添加列表
@news_blueprint.route('/comment_list/<int:news_id>')
def comment_list(news_id):
    # 处理：查询指定新闻的评论信息
    list1 = NewsComment.query. \
        filter_by(news_id=news_id, comment_id=None). \
        order_by(NewsComment.like_count.desc(),NewsComment.id.desc())
    # 将对象转字典
    list2 = []
    total_comment = 0
    for comment in list1:
        # 根据评论对象comment获取所有的回复对象
        back_list = []
        total_comment += 1
        for back in comment.backs:
            back_list.append({
                'id': back.id,
                'msg': back.msg,
                'nick_name': back.user.nick_name,
            })

        list2.append({
            'id': comment.id,
            'msg': comment.msg,
            'avatar': comment.user.avatar,
            'nick_name': comment.user.nick_name,
            'create_time': comment.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'like_count': comment.like_count,
            'back_list': back_list
        })

    # 响应
    return jsonify(list=list2,total_comment=total_comment)


# 评论点赞
@news_blueprint.route('/comment_like')
def comment_like():
    comment_id = request.args.get('like_id')
    # 添加点赞计数
    comment = NewsComment.query.filter_by(id=comment_id).first()
    comment.like_count+=1
    db.session.commit()
    return jsonify(res=1)

# 判断网站来自mobile还是pc
def checkMobile(request):
    """
    demo :
        @app.route('/m')
        def is_from_mobile():
            if checkMobile(request):
                return 'mobile'
            else:
                return 'pc'
    :param request:
    :return:
    """
    userAgent = request.headers['User-Agent']
    # userAgent = env.get('HTTP_USER_AGENT')

    _long_matches = r'googlebot-mobile|android|avantgo|blackberry|blazer|elaine|hiptop|ip(hone|od)|kindle|midp|mmp|mobile|o2|opera mini|palm( os)?|pda|plucker|pocket|psp|smartphone|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce; (iemobile|ppc)|xiino|maemo|fennec'
    _long_matches = re.compile(_long_matches, re.IGNORECASE)
    _short_matches = r'1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|e\-|e\/|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(di|rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|xda(\-|2|g)|yas\-|your|zeto|zte\-'
    _short_matches = re.compile(_short_matches, re.IGNORECASE)

    if _long_matches.search(userAgent) != None:
        return True
    user_agent = userAgent[0:4]
    if _short_matches.search(user_agent) != None:
        return True
    return False

# 关注
@news_blueprint.route('/follow', methods=['POST'])
def follow():
    # 接收
    author_id = request.form.get('author_id')

    # 验证
    # 1.作者编号非空
    if not author_id:
        return jsonify(result=1)
    # 2.用户登录
    if 'user_id' not in session:
        return jsonify(result=2)
    user_id = session.get('user_id')
    # 查询对象
    user = UserInfo.query.get(user_id)
    author = UserInfo.query.get(author_id)

    # 处理：判断是否关注
    if author in user.authors:
        # 取消
        user.authors.remove(author)
        # 粉丝数-1
        author.follow_count -= 1
    else:
        # 关注
        user.authors.append(author)
        # 粉丝数+1
        author.follow_count += 1
    # 提交到数据库
    db.session.commit()

    # 响应
    return jsonify(result=3)
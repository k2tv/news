from flask import Blueprint, session, make_response, request, jsonify
from utils.captcha.captcha import captcha
import random
from utils.ytx_sdk.ytx_send import sendTemplateSMS

user_blueprint = Blueprint('user', __name__, url_prefix='/user')


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
        if not img_code_session:
            return jsonify(res=3)
        if img_code != img_code_session:
            print(img_code_session,img_code)
            return jsonify(res=2)
        # 处理
        # 1.生成随机的验证码
        smscode = str(random.randint(100000, 999999))
        # 2.保存验证码，用于后续验证
        session['sms_code'] = smscode
        # 3.发送短信
        sendTemplateSMS(mobile, [smscode, '10'], 1)
        # print(smscode)
        # 响应
        return jsonify(res=1)
    return jsonify(res=3)

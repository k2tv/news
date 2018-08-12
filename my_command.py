from flask_script.commands import Command
from models import UserInfo, db
from flask import current_app
from datetime import datetime
import random


class CreateAdmin(Command):
    def run(self):
        name = input('请输入用户名：')
        pwd = input('请输入密码：')

        user = UserInfo()
        user.mobile = name
        user.nick_name = name
        user.password = pwd
        user.isAdmin = True
        db.session.add(user)
        db.session.commit()

        print('管理员创建成功')


class LoginTest(Command):
    def run(self):
        now = datetime.now()

        redis_cli = current_app.redis_cli
        key = 'login' + now.strftime('%Y%m%d')  # 'login年月日'
        # redis_cli.hset(key,'08:00',100)
        # redis_cli.hset(key,'09:00',200)
        # redis_cli.hset(key,'10:00',300)
        # ...
        # redis_cli.hset(key,'19:00',200)
        for index in range(8, 20):
            redis_cli.hset(key, '%02d:00' % index, random.randint(200, 500))

        print('ok')

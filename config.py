import redis
import os

class Config(object):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql://name:password@host:port/database'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # redis配置
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 8
    # session
    SECRET_KEY = "hellomengf"
    # flask_session的配置信息
    SESSION_TYPE = "redis"  # 指定 session 保存到 redis 中
    SESSION_USE_SIGNER = True  # 让 cookie 中的 session_id 被加密签名处理
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)  # 使用 redis 的实例
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 14  # session 的有效期，单位是秒
    # 项目在磁盘上的目录
    #__file__====>'config.py'
    #os.path.abspath('')==>文件的绝对路径，如/home/python/Desktop/sy8/sy8_flask/xjzx/config.py
    #os.path.dirname('')==>获取目录名，如/home/python/Desktop/sy8/sy8_flask/xjzx
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # 头像保存路径
    AVATAR_PATH = os.path.join(BASE_DIR, 'static/news/images/avatar/')

    # 腾讯云cos配置

    # 腾讯云短信配置



class DevelopConfig(Config):
    DEBUG = True



class ProductConfig(Config):
    pass


class Setting(object):

    # 爬虫相关的一些参数

    HEADERS = [{'User-Agent': 'Opera/9.80(WindowsNT6.1;U;en)Presto/2.8.131Version/11.11'},
               {'User-Agent': 'Mozilla/5.0(Macintosh;IntelMacOSX10_7_0)AppleWebKit/535.11(KHTML,likeGecko)Chrome/17.0.963.56Safari/535.11'},
               {'User-Agent': 'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;Maxthon2.0)'},
               {'User-Agent': 'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;TencentTraveler4.0)'},
               {'User-Agent': 'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1)'},
               {'User-Agent': 'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;TheWorld)'},
               {'User-Agent': 'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;Trident/4.0;SE2.XMetaSr1.0;SE2.XMetaSr1.0;.NETCLR2.0.50727;SE2.XMetaSr1.0)'},
               {'User-Agent': 'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;360SE)'},
               {'User-Agent': 'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;AvantBrowser)'},
               {'User-Agent': 'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1)'},
               {'User-Agent': 'Mozilla/5.0(iPhone;U;CPUiPhoneOS4_3_3likeMacOSX;en-us)AppleWebKit/533.17.9(KHTML,likeGecko)Version/5.0.2Mobile/8J2Safari/6533.18.5'},
               {'User-Agent': 'Mozilla/5.0(iPod;U;CPUiPhoneOS4_3_3likeMacOSX;en-us)AppleWebKit/533.17.9(KHTML,likeGecko)Version/5.0.2Mobile/8J2Safari/6533.18.5'},
               {'User-Agent': 'Mozilla/5.0(iPad;U;CPUOS4_3_3likeMacOSX;en-us)AppleWebKit/533.17.9(KHTML,likeGecko)Version/5.0.2Mobile/8J2Safari/6533.18.5'},
               {'User-Agent': 'Mozilla/5.0(Linux;U;Android2.3.7;en-us;NexusOneBuild/FRF91)AppleWebKit/533.1(KHTML,likeGecko)Version/4.0MobileSafari/533.1'},
               {'User-Agent': 'MQQBrowser/26Mozilla/5.0(Linux;U;Android2.3.7;zh-cn;MB200Build/GRJ22;CyanogenMod-7)AppleWebKit/533.1(KHTML,likeGecko)Version/4.0MobileSafari/533.1'},
               {'User-Agent': 'Opera/9.80(Android2.3.4;Linux;OperaMobi/build-1107180945;U;en-GB)Presto/2.8.149Version/11.10'},
               {'User-Agent': 'Mozilla/5.0(Linux;U;Android3.0;en-us;XoomBuild/HRI39)AppleWebKit/534.13(KHTML,likeGecko)Version/4.0Safari/534.13'},
               {'User-Agent': 'Mozilla/5.0(BlackBerry;U;BlackBerry9800;en)AppleWebKit/534.1+(KHTML,likeGecko)Version/6.0.0.337MobileSafari/534.1+'},
               {'User-Agent': 'Mozilla/5.0(hp-tablet;Linux;hpwOS/3.0.0;U;en-US)AppleWebKit/534.6(KHTML,likeGecko)wOSBrowser/233.70Safari/534.6TouchPad/1.0'},
               {'User-Agent': 'Mozilla/5.0(SymbianOS/9.4;Series60/5.0NokiaN97-1/20.0.019;Profile/MIDP-2.1Configuration/CLDC-1.1)AppleWebKit/525(KHTML,likeGecko)BrowserNG/7.1.18124'},
               {'User-Agent': 'Mozilla/5.0(compatible;MSIE9.0;WindowsPhoneOS7.5;Trident/5.0;IEMobile/9.0;HTC;Titan)'},
               {'User-Agent': 'UCWEB7.0.2.37/28/999'}, {'User-Agent': 'NOKIA5700/UCWEB7.0.2.37/28/999'},
               {'User-Agent': 'Openwave/UCWEB7.0.2.37/28/999'},
               {'User-Agent': 'Mozilla/4.0(compatible;MSIE6.0;)Opera/UCWEB7.0.2.37/28/999'}]

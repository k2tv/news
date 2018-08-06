from utils.qcloudsms_py import SmsSingleSender
from utils.qcloudsms_py.httpclient import HTTPError
from config import Config


def send_sms_code(phone_numbers, smscode):
    template_id = 167451;
    ssender = SmsSingleSender(Config.QCLOUD_sms_appid, Config.QCLOUD_sms_appkey)
    params = [smscode]
    try:
        ssender.send_with_param(86, phone_numbers, template_id, params)
    except HTTPError:
        pass
    except Exception:
        pass

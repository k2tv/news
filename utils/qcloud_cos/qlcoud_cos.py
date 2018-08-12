# appid已在配置中移除,请在参数Bucket中带上appid。Bucket由bucketname-appid组成
# 1. 设置用户配置, 包括 secretId，secretKey 以及 Region
# -*- coding=utf-8
from utils.qcloud_cos import CosConfig, CosS3Client

import sys
import logging
from config import Config

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

secret_id = Config.QCLOUD_secret_id  # 替换为用户的 secretId
secret_key = Config.QCLOUD_secret_key  # 替换为用户的 secretKey
region = Config.QCLOUD_region  # 替换为用户的 Region
token = Config.QCLOUD_token  # 使用临时密钥需要传入 Token，默认为空，可不填
config = CosConfig(Secret_id=secret_id, Secret_key=secret_key, Region=region, Token=token)
# 2. 获取客户端对象
client = CosS3Client(config)


# 参照下文的描述。或者参照 Demo程序，详见 https://github.com/tencentyun/cos-python-sdk-v5/blob/master/qcloud_cos/demo.py

# 文件上传
def upload_img(fp, file_name):
    response = client.put_object(
        Bucket=Config.QCLOUD_Bucket,
        Body=fp,
        Key=file_name,
    )

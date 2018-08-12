# coding:utf-8
"""
实现ifeng热点新闻爬取
地址 http://news.ifeng.com/hotnews/
爬取 标题 内容 点击量
并且返回json格式数据或者直接添加数据库
by:孟峰
date:2018-08-04
"""

import urllib.request  # 爬虫
import re  # 正则匹配
from config import Setting,Config
import random
import time
from datetime import datetime
from pymysql import *
import redis
import math

class InfoSpider(object):
    def __init__(self):
        url = Setting.START_URL_sina
        self.headers = random.choice(Setting.HEADERS)
        self.request = urllib.request.Request(url=url, headers=self.headers)
        # redis去重redis_cli

        # self.redis_cli = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=Config.REDIS_DB)
        # self.request_url = self.redis_cli.smembers('netease')
        # self.request_url_list = [item.decode() for item in self.request_url]
        self.request_url_list = []

        # self.conn = connect(host='localhost', database='flask_news', port=3306, user='test', password='mysql',
        #                     charset='utf8')
        # self.cs = self.conn.cursor()

    def get_data(self):
        try:
            data = urllib.request.urlopen(self.request, timeout=3).read().decode('gbk')  # 读取页面数据 并转换成str类型

            # 与匹配相关的正则表达式
            regex_table = r'<table.*?">[\s\S]*?</table>'
            regex_table_in = r'<td.*?<span>.*?href="(.*?)".*?>(.*?)</a>.*?</td>[\s\S]*?<td.*?>(.*?)</td>'
            regex_summary = r'<.*?>|&.*?;'
            regex_img = r'<img.*?src="(.*?)".*?/>'
            res_table = re.findall(regex_table, data)
            index = 0
            for res_item in res_table:
                index += 1;
                if index != 1:
                    continue
                res_table_in = re.findall(regex_table_in, res_item)
                for index_item in range(len(res_table_in)):
                    res = res_table_in[index_item]
                    link = res[0]

                    if link not in self.request_url_list and link:
                        content = self.get_detail(link)
                        self.request_url_list.append(link)
                        # self.redis_cli.sadd('netease',link)
                        if content:
                            title = res[1]
                            content = content.strip()
                            # 获取封面图片
                            img = re.search(regex_img, content)
                            if not img:
                                img = 'news_pic.jpg'
                            else:
                                img = img.group(1)
                            # 获取摘要
                            summary = content[:200]
                            summary = re.sub(regex_summary, '', summary)
                            if not self.judge_zh(summary):
                                summary = '图片内容：' + title
                            print('source:', index)
                            print('title:', title)
                            print('click_count:', res[2])
                            print('link:', link)
                            print('img:', img)
                            print('summary:', summary)
                            print('content:', content)
                            # t = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            # params = [title, res[2], img, summary, content, 2, math.ceil(index/2), '凤凰咨询',2,t,t]
                            # self.cs.execute(
                            #     'insert into news_info(title,click_count,pic,summary,context,user_id,category_id,source,status,create_time,update_time,comment_count) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0)',
                            #     params)
                            # self.conn.commit()
                            print('____________________采集数据库完成____________________')
                        time.sleep(random.random())
            # self.cs.close()
            # self.conn.close()
        except Exception as e:
            print(e)
            pass
            # print('error')

    def judge_zh(self, data):
        regex_no_zh = u'[\u4e00-\u9fa5]+'
        res_has_no_zh = re.search(regex_no_zh, data)
        if res_has_no_zh:
            return True
        else:
            return False

    def get_detail(self, link):
        try:
            data_detail = urllib.request.urlopen(urllib.request.Request(url=link, headers=self.headers),
                                                 timeout=3).read().decode()  # 读取页面数据 并转换成str类型
            regex_detail = r'<div.*?lass="post_text.*?id="endText.*?>([\s\S]*)</div>'
            res_detail = re.findall(regex_detail, data_detail)
            # return res_detail[0]
            # 去掉凤凰logo
            regex_replace = r'(.*)<span class="ifengLogo">(.*?)</span>(.*)'
            res = re.findall(regex_replace, res_detail[0])[0]
            res_no_logo = res[0] + res[2]
            # 根据是否含有汉字 去掉纯视频 或者纯英文报道
            if self.judge_zh(res_no_logo):
                return res_no_logo
            else:
                return False
        except:
            return False


def run_ifeng_spider():
    info_spider = InfoSpider()
    info_spider.get_data()


if __name__ == '__main__':
    run_ifeng_spider()
    # info_spider = InfoSpider()
    # info_spider.get_detail('http://news.ifeng.com/a/20180604/58565046_0.shtml')

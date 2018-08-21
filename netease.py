"""
实现网易热点新闻爬取
爬取 标题 内容 点击量
并且返回json格式数据或者直接添加数据库
by:孟峰
date:2018-08-04
"""

import urllib.request  # 爬虫
import re  # 正则匹配
from config import Setting, Config
import random
import time
from datetime import datetime
from pymysql import *
import redis
from datetime import datetime


class InfoSpider(object):
    def __init__(self):
        url = Setting.START_URL_163
        self.headers = {
            'User-Agent': 'Mozilla/5.0(Macintosh;U;IntelMacOSX10_6_8;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50'}
        self.request = urllib.request.Request(url=url, headers=self.headers)
        # redis去重redis_cli
        self.redis_cli = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=Config.REDIS_DB)
        self.request_url = self.redis_cli.smembers('netease')
        self.request_url_list = [item.decode() for item in self.request_url]

        self.conn = connect(host='localhost', database='flask_news', port=3306, user='test', password='mysql',
                            charset='utf8')
        self.cs = self.conn.cursor()

    def get_data(self):
        try:
            data = urllib.request.urlopen(self.request, timeout=3).read().decode('gbk')  # 读取页面数据 并转换成str类型

            # 与匹配相关的正则表达式
            regex_table = r'<table.*?">[\s\S]*?</table>'
            regex_table_in = r'<td.*?<span>.*?href="(.*?)".*?>(.*?)</a>.*?</td>[\s\S]*?<td.*?>(.*?)</td>'
            regex_summary = r'<[\S\s]*?>|&.*?;'
            regex_img = r'<img.*?src="(.*?)".*?/>'
            regex_div = r'<div.*?>|</div>'
            res_table = re.findall(regex_table, data)
            index = 0
            for res_item in res_table:
                index += 1;
                cat_id = 1
                # if index != 31:
                #     continue
                if index > 78:
                    break
                # 娱乐: 3  13 - 18
                # id 4
                if index >= 13 and index <= 18:
                    cat_id = 4
                # 体育: 4 19 - 24
                # id 3
                elif index >= 19 and index <= 24:
                    cat_id = 3
                # 财经: 5 25 - 30
                # id  5
                elif index >= 25 and index <= 30:
                    cat_id = 5
                # 科技: 6 31 - 36
                # id 2
                elif index >= 31 and index <= 36:
                    cat_id = 2

                res_table_in = re.findall(regex_table_in, res_item)
                for index_item in range(len(res_table_in)):
                    res = res_table_in[index_item]
                    link = res[0]

                    if link not in self.request_url_list and link:
                        content = self.get_detail(link)
                        self.request_url_list.append(link)
                        self.redis_cli.sadd('netease', link)
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
                            summary = content[:150].strip()
                            summary = re.sub(regex_summary, '', summary)
                            content = re.sub(regex_div, '', content)
                            if not self.judge_zh(summary):
                                summary = '原标题：' + title
                                content += title
                            # print('source:', index, ' cat:', cat_id)
                            # print('title:', title)
                            # print('click_count:', res[2])
                            # print('link:', link)
                            # print('img:', img)
                            # print('summary:', summary)
                            # print('content:', content)
                            t = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            # 3 为网易用户ID
                            params = [title, res[2], img, summary, content, 3, cat_id, '网易', 2, t, t]
                            try:
                                self.cs.execute(
                                    'insert into news_info(title,click_count,pic,summary,context,user_id,category_id,source,status,create_time,update_time,comment_count) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0)',
                                    params)
                                self.conn.commit()
                            except Exception as e:
                                print('database error:', end='')
                                print(e)
                            # print('____________________采集数据完成____________________')
                            print('source:', index, ' cat:', cat_id, ' title:', title)
                        # t = random.random() * 10
                        # print(t)
                        time.sleep(random.random() * 60)  # 0-60s随机采集
        except Exception as e:
            print('get_data error:', end='')
            print(e)
            # print('error')

    def __del__(self):
        self.cs.close()
        self.conn.close()

    def judge_zh(self, data):
        regex_no_zh = u'[\u4e00-\u9fa5]+'
        res_has_no_zh = re.search(regex_no_zh, data)
        if res_has_no_zh:
            return True
        else:
            # if re.search(r'<img',data):
            #     return False
            # else:
            return True

    def get_detail(self, link):
        try:
            data_detail = urllib.request.urlopen(urllib.request.Request(url=link, headers=self.headers),
                                                 timeout=3).read().decode('gbk')  # 读取页面数据 并转换成str类型
            regex_detail = r'<div.*?post_text.*?>([\s\S]*?)</div>'
            res_detail = re.findall(regex_detail, data_detail)
            # return res_detail[0]
            # 去掉凤凰logo
            # regex_replace = r'(.*)<span class="ifengLogo">(.*?)</span>(.*)'
            # res = re.findall(regex_replace, res_detail[0])[0]
            # res_no_logo = res[0] + res[2]
            # 根据是否含有汉字 去掉纯视频 或者纯英文报道
            if self.judge_zh(res_detail[0]):
                return res_detail[0]
            else:
                return False
        except Exception as e:
            print('get_detail error:', end='')
            print(e)
            return False


def run_ifeng_spider():
    try:
        info_spider = InfoSpider()
        info_spider.get_data()
    except Exception as e:
        print('run_ifeng_spider error', end='')
        print(e)


if __name__ == '__main__':
    while True:
        t = datetime.now()
        h = int(t.strftime('%H'))
        if h >= 22 or h < 5:
            time.sleep(60 * 30)
            continue
        print(t)
        run_ifeng_spider()
        time.sleep(60 * 30)  # 每次间隔30分钟  

    # info_spider = InfoSpider()
    # info_spider.get_detail('http://news.ifeng.com/a/20180604/58565046_0.shtml')

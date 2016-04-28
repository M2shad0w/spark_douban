# -*- coding: utf-8 -*-
# !/usr/bin/env python
__author__ = 'm2shad0w'

import string
import re
import urllib2
import bs4
import os
import time
import requests


class DouBanSpider(object):

    def __init__(self):
        # https://movie.douban.com/subject/1292052/reviews?start=1&filter=&limit=10
        self.page = 1
        self.cur_url = "https://movie.douban.com/top250?start=%s&filter=" #"https://movie.douban.com/review/best/?start={top}"
        self.cur_url2 = "https://movie.douban.com/subject/%s/comments?start=%s&limit=20&sort=new_score" #https://movie.douban.com/subject/%s/collections?start=%s"#"https://movie.douban.com/subject/%s/reviews?start=%s&filter=&limit=20"
        self.datas = []
        self.length = 0
        self.movie_id = []
        self.user_data = []
        print "豆瓣电影爬虫准备就绪, 准备爬取数据..."

    def login_douban(self):
        print "正在登录豆瓣..."

        # -- Login Start --
        postUrl = 'https://accounts.douban.com/login?source=movie'
        originUrl = "https://accounts.douban.com"
        user_agent = 'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0'
        headers = {'User-Agent': user_agent,
                    'Connection': 'keep-alive',
                    'Referer': postUrl,
                    'origin': originUrl
                   }
        self.s = requests.Session()
        # Get userName and password
        userName = "912657650@qq.com" #raw_input('Enter your userName:')
        password = raw_input('Enter your password:')
        # Post loginform
        payload = {'source': 'movie',
                    'alias': userName,
                    'form_password': password,
                    'form_email': userName,
                    'login': u'登录'
                    }
        r = self.s.post(postUrl, data=payload, headers=headers)
        if r.ok:
            print "登录成功"
        # print r.raise_for_status()  # check status code

        # -- Login End --
    def get_page(self, cur_page, url):
        """
        根据当前页码爬取网页HTML
        Args:
            cur_page: 表示当前所抓取的网站页码
        Returns:
            返回抓取到整个页面的HTML(unicode编码)
        Raises:
            URLError:url引发的异常
        """
        try:
            # print url.format(top=(cur_page - 1) * 10)
            print url.format(top=(cur_page - 1) * 25)
            my_page = urllib2.urlopen(url.format(top=(cur_page - 1) * 25)).read().decode("utf-8")
        except urllib2.URLError, e:
            if hasattr(e, "code"):
                print "The server couldn't fulfill the request."
                print "Error code: %s" % e.code
            elif hasattr(e, "reason"):
                print "We failed to reach a server. Please check your url and read the Reason"
                print "Reason: %s" % e.reason
        return my_page

    def get_sec_page(self, url):
        try:
            # print url.format(top=(cur_page - 1) * 10)
            my_page = urllib2.urlopen(url).read().decode("utf-8")
        except urllib2.URLError, e:
            if hasattr(e, "code"):
                print "The server couldn't fulfill the request."
                print "Error code: %s" % e.code
            elif hasattr(e, "reason"):
                print "We failed to reach a server. Please check your url and read the Reason"
                print "Reason: %s" % e.reason
        return my_page

    def find_title(self, my_page):
        """
        通过返回的整个网页HTML, 正则匹配前100的电影名称

        Args:
            my_page: 传入页面的HTML文本用于正则匹配
        """
        '''
        <div class="item">
        <div class="pic">
        <em class="">1</em>
        <a href="https://movie.douban.com/subject/1292052/">
        <img alt="肖申克的救赎" class="" src="https://img3.doubanio.com/view/movie_poster_cover/ipst/public/p480747492.jpg"/>
        </a>
        </div>
        <div class="info">
        <div class="hd">
        <a class="" href="https://movie.douban.com/subject/1292052/">
        <span class="title">肖申克的救赎</span>
        <span class="title"> / The Shawshank Redemption</span>
        <span class="other"> / 月黑高飞(港)  /  刺激1995(台)</span>
        </a>
        <span class="playable">[可播放]</span>
        </div>
        <div class="bd">
        <p class="">
                                    导演: 弗兰克·德拉邦特 Frank Darabont   主演: 蒂姆·罗宾斯 Tim Robbins /...<br/>
                                    1994 / 美国 / 犯罪 剧情
                                </p>
        <div class="star">
        <span class="rating5-t"></span>
        <span class="rating_num" property="v:average">9.6</span>
        <span content="10.0" property="v:best"></span>
        <span>688195人评价</span>
        </div>
        <p class="quote">
        <span class="inq">希望让人自由。</span>
        </p>
        </div>
        </div>
        </div>
        '''
        temp_data = []
        soup = bs4.BeautifulSoup(my_page, "lxml")
        items = soup.select(".item")
        print "#######"
        for i in items:
            movie_id = i.a.get("href").split("/")[-2]
            title = i.span.string
            e = i.select(".star")
            for ee in e:
                eee = ee.find_all("span")
                score = eee[1].get_text().strip()
                total_score_person = re.sub(r'\D', "", eee[3].get_text())  # i.span["rating_num"].string[:-3]
            # print movie_id, title, score, total_score_person
            a = [movie_id, title, score, total_score_person]
            temp_data.append(a)
        self.datas.extend(temp_data)

    def start_spider(self):
        """
        爬虫入口, 并控制爬虫抓取页面的范围
        """

        while self.page <= 10:
            # my_page = self.get_page(self.page, self.cur_url)
            url = self.cur_url % (self.page)
            print url
            r = self.s.get(url)
            if r.status_code == 200:
                my_page = r.text
            else:
                print "get my_page error, continue"
                continue
            self.find_title(my_page)
            self.page += 1
            time.sleep(0.1)

    def get_page_length(self, url):
        length = 0
        try:
            # print url
            my_page = urllib2.urlopen(url).read().decode("utf-8")
            soup = bs4.BeautifulSoup(my_page, "lxml")
            length = re.sub(r'\D', "", soup.h1.string)
        except urllib2.URLError, e:
            if hasattr(e, "code"):
                print "The server couldn't fulfill the request."
                print "Error code: %s" % e.code
            elif hasattr(e, "reason"):
                print "We failed to reach a server. Please check your url and read the Reason"
                print "Reason: %s" % e.reason
        return int(length)

    def start_score(self):
        # https://movie.douban.com/subject/1292052/reviews
        # get deep length
        print "正在获取 %s 部电影的用户评分..." % (self.datas.__len__())
        jjj = 0
        for i in self.datas:
            jjj += 1
            # url = "https://movie.douban.com/subject/%s/reviews" % (id)
            url = self.cur_url2 % (i[0], 20)
            r = self.s.get(url)
            if r.ok:
                my_page = r.text
                soup = bs4.BeautifulSoup(my_page, "lxml")
                # print soup.select(".total")
                l = soup.select(".total")[0].string
                # print l

                llen = int(re.sub(r'\D', "", l))
                print llen
            else:
                llen = 0
            # llen = self.get_page_length(url)
            # llen = int(i[3])
            print "第%s部电影 %s 有 %s 条评论" %(jjj, i[1].encode("utf-8"), llen)
            # score = 0
            temp_data = []
            # print len
            deep = llen / 20
            step = 0
            if llen == 0:
                continue

            while step <= deep:
                # user_l = []
                # score_l = []
                print "电影%s, 步长%s, 第%s条评论到%s评论..."%(i[1].encode("utf-8"), step, 20*step, 20*(step + 1))
                time.sleep(2)
                # print self.cur_url2
                cur_url2 = self.cur_url2 % (i[0], step * 20)
                print cur_url2
                # my_page = self.get_sec_page(cur_url2)
                r = self.s.get(cur_url2)
                if r.status_code == 200:
                    my_page = r.text
                else:
                    print "get my_page error continue"
                    step += 1
                    continue
                # print my_page
                soup = bs4.BeautifulSoup(my_page, "lxml")
                item = soup.select('.comment-info')
                for j in item:
                    user_id = j.a.get("href").split("/")[-2]
                    class_info = j.span.attrs.get("class")
                    if class_info:
                        score = "3"
                    else:
                        score = class_info[0][-2]
                    temp_data.append(",".join([i[0], user_id, score]))
                step += 1
                # 最多400个评论就走了
                if step > 20:
                    break
                # break
            # break
        self.user_data.extend(temp_data)


if __name__ == '__main__':
    # main()
    print """
    ###############################
        一个简单的豆瓣电影top250爬虫
        Author:M2shad0w
    ###############################
    """
    my_spider = DouBanSpider()
    my_spider.login_douban()

    print "查找top250电影"
    my_spider.start_spider()
    if not os.path.exists("./data/"):
        os.makedirs("./data/")
    # 找到热门电影
    f = open("data/douba_film_name_top_250.txt", 'w')
    try:
        for item in my_spider.datas:
            f.write(",".join(item).encode("utf-8") + "\n")
            print item
    except IOError as e:
        print e
    finally:
        print "get all top 250 movie and writing 2 file ..."
        f.close()
    # 找到用户评分
    # print "查找这些电影的用户评分"
    my_spider.start_score()
    i = 0
    try:
        f = open("data/user_score.txt", 'w')
        for item in my_spider.user_data:
            print item
            f.write(item.encode("utf-8")+"\n")
            i += 1
    except IOError as e:
        print(e)
    finally:
        print "将评论存入文件..."
        f.close()
    print i
    print "豆瓣爬虫爬取结束..."

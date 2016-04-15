# -*- coding: utf-8 -*-
# !/usr/bin/env python
__author__ = 'm2shad0w'

import string
import re
import urllib2
import bs4
import os
import time


class DouBanSpider(object):
    """类的简要说明
    本类主要用于抓取豆瓣热门电影
    """

    def __init__(self):
        # https://movie.douban.com/subject/1292052/reviews?start=1&filter=&limit=10
        self.page = 1
        self.cur_url = "https://movie.douban.com/review/best/?start={top}"
        self.cur_url2 = "https://movie.douban.com/subject/%s/reviews?start=%s&filter=&limit=20"
        self.datas = []
        self.length = 0
        self.movie_id = []
        self.user_data = []
        print "豆瓣电影爬虫准备就绪, 准备爬取数据..."

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
            my_page = urllib2.urlopen(url.format(top=(cur_page - 1) * 10)).read().decode("utf-8")
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
        <span class="pl ll obss">
            <span class="starb">
                <a href="https://www.douban.com/people/58847654/">回望长安已苍老</a>
            </span>
            评论: <a href="https://movie.douban.com/subject/25760615/"> 《回溯迷踪》</a>
            <span class="allstar20" title="较差"></span>
        </span>
        '''
        temp_data = []
        soup = bs4.BeautifulSoup(my_page, "lxml")
        items = soup.select(".obss")
        # print "#######"
        for i in items:
            score = 0
            jj = i.find_all("span")
            for j in jj:
                cc = j.attrs.get("class")[0]
                # print cc
                if cc[:3] == "all":
                    score = cc[-2:-1]
                    # print "score %s" % (cc[-2:-1])
            e = i.find_all('a')
            # print type(e)
            data = e[1].get("href").split("/")[-2]
            text = e[1].get_text().strip()
            # print data, text, score
            self.movie_id.append(data)
            temp_data.append(data + "," + text + "," + score)
        self.datas.extend(temp_data)

    def start_spider(self):
        """
        爬虫入口, 并控制爬虫抓取页面的范围
        """

        while self.page <= 5:
            my_page = self.get_page(self.page, self.cur_url)
            self.find_title(my_page)
            self.page += 1
            # time.sleep(0.1)

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
        print "正在获取 %s 部电影的用户评分..." % (self.movie_id.__len__())
        jjj = 0
        for id in self.movie_id:
            jjj += 1
            url = "https://movie.douban.com/subject/%s/reviews" % (id)
            llen = self.get_page_length(url)
            print "第%s部电影 %s 有 %s 条评论" %(jjj, int(id), llen)
            score = 0
            temp_data = []
            # print len
            deep = llen / 20
            step = 0
            while step <= deep:
                print "电影%s, 步长%s, 第%s条评论到%s评论..."%(id, step, step*20, (step + 1)*20)
                time.sleep(0.2)
                # print self.cur_url2
                cur_url2 = self.cur_url2 % (id, step * 20)
                # print cur_url2
                my_page = self.get_sec_page(cur_url2)
                # print my_page
                soup = bs4.BeautifulSoup(my_page, "lxml")
                item = soup.select(".review-hd-info")
                '''
                <div class="review-hd-info">
                    <a class="" href="https://www.douban.com/people/141383200/">打扰</a>
                    2016-03-13 18:37:50
                    <span class="allstar50" title="力荐"></span>
                </div>
                '''
                for i in item:
                    user_id = i.a.get("href").split("/")[-2]
                    cc = i.span.attrs.get("class")[0]
                    if cc[:3] == "all":
                        score = cc[-2]
                        # print score
                    temp_data.append(user_id + "," + id + "," + score)
                # break
            #     self.find_user_movieid_score(my_page)
                step += 1
            # break
        self.user_data.extend(temp_data)

def main():
        print """
            ###############################
                一个简单的豆瓣电影热门爬虫
                Author:M2shad0w
            ###############################
        """
        my_spider = DouBanSpider()
        print "查找热门电影"
        my_spider.start_spider()
        if not os.path.exists("./data/"):
            os.makedirs("./data/")
        # 找到热门电影
        # f = open("data/douba_film_name_100.txt", 'w')
        # try:
        #     for item in my_spider.datas:
        #         f.write(item.encode("utf-8")+"\n")
        #         print item
        # except IOError as e:
        #     print e
        # finally:
        #     f.close()
        # 找到用户评分
        print "查找这些电影的用户评分"
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
            f.close()
        print i
        print "豆瓣爬虫爬取结束..."

if __name__ == '__main__':
    main()

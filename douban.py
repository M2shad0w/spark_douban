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
    本类主要用于抓取豆瓣前100的电影名称

    Attributes:
        page: 用于表示当前所处的抓取页面
        cur_url: 用于表示当前争取抓取页面的url
        datas: 存储处理好的抓取到的电影名称
        _top_num: 用于记录当前的top号码
    """

    def __init__(self):
        self.page = 1
        self.cur_url = "https://movie.douban.com/review/best/?start={top}"
        self.cur_url2 = "https://movie.douban.com/subject/{move_id}/reviews?start=21&filter=&limit=20"
        self.datas = []
        self._top_num = 1
        print "豆瓣电影爬虫准备就绪, 准备爬取数据..."

    def get_page(self, cur_page):
        """
        根据当前页码爬取网页HTML
        Args:
            cur_page: 表示当前所抓取的网站页码
        Returns:
            返回抓取到整个页面的HTML(unicode编码)
        Raises:
            URLError:url引发的异常
        """
        url = self.cur_url
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
        print "#######"
        for i in items:
            score = 0
            # print i
            # print i.attrs["class"]
            jj = i.find_all("span")
            for j in jj:
                cc = j.attrs.get("class")[0]
                # print cc
                if cc[:3] == "all":
                    score = cc[-2:-1]
                    print "score %s" % (cc[-2:-1])
            # print i.a.string
            # print i
            e = i.find_all('a')
            # print type(e)
            data = e[1].get("href").split("/")[-2]
            text = e[1].get_text().strip()
            # print data, text, score
            temp_data.append(data + "," + text + "," + score)
            # for ii in e:
            #     print type(ii)
            #     data = ii.get("href")
            #     text = ii
            #     print data, text
        # items = soup.select(".ilst a")
        # for i in items:
        #     print i
        #     e = i.attrs.get("href").split("/")[-2:-1]
        #     print e
        #     title = i.attrs.get("title")
        #     temp_data.append(e[0] + "," + title)
        # print(temp_data)
        # for index, item in enumerate(items):
        #     print index, item
        # print my_page
        # temp_data = []
        # <li class="ilst" style="clear:both;">
        # movie_items = re.findall(r'<li class="ilst".*?>(.*?)</li>', my_page, re.S)
        # print movie_items
        # for index, item in enumerate(movie_items):
        #     print index, item
        #     if item.find("&nbsp") == -1 :
        #         temp_data.append("Top" + str(self._top_num) + " " + item)
        #         self._top_num += 1
        self.datas.extend(temp_data)

    def start_spider(self):
        """
        爬虫入口, 并控制爬虫抓取页面的范围
        """

        while self.page <= 5:
            my_page = self.get_page(self.page)
            self.find_title(my_page)
            self.page += 1
            time.sleep(0.1)


def main():
        print """
            ###############################
                一个简单的豆瓣电影热门爬虫
                Author:M2shad0w
            ###############################
        """
        my_spider = DouBanSpider()
        my_spider.start_spider()
        if not os.path.exists("./data/"):
            os.makedirs("./data/")
        f = open("data/douba_film_name_100.txt", 'w')
        try:
            for item in my_spider.datas:
                f.write(item.encode("utf-8")+"\n")
                print item
        except IOError as e:
            print e
        finally:
            f.close()
            print "豆瓣爬虫爬取结束..."

if __name__ == '__main__':
    main()

# coding=utf-8
import requests
import feedparser
import difflib
import re
from datetime import timedelta
from datetime import date
from bs4 import BeautifulSoup, Comment
import psycopg2


def update_naver_rss():
    con = psycopg2.connect(dbname='postgres', host="61.43.139.70",port=5432, user='postgres', password='postgres')
    cur = con.cursor()

    fp = open('naver', "r+")
    for r in fp.readlines():
        #print r[:-1]
        cur.execute("""insert into rss (rss_url, post_date, crawl_date, crawl_id, type) values ('%s',0,0,0,2);""" % r[:-1])

    con.commit()
    con.close()

update_naver_rss()
exit(0)

def get_url(url):
    return requests.get(url).text.encode("utf-8")


def get_naver_rss():
    s = set()
    for i in range(5,35):
        print i
        for j in range(1,21):
            rst = get_url("""http://section.blog.naver.com/sub/PostListByDirectory.nhn?
            option.page.currentPage=%s&
            option.templateKind=0&
            option.directorySeq=%s&
            option.viewType=default&option.orderBy=quality&option.latestOnly=1""" % (j,i))

            dom = BeautifulSoup(rst)
            for x in dom.find_all("a", {"href":re.compile(r".*?\?Redirect.*")}):

                x = re.findall(r"(.*?)\?Redirect.*", x.get('href'))[0]
                #print x
                x= x.replace("blog.naver", "blog.rss.naver")
                x = x + ".xml"
                s.add(x)


    fp = open('naver', "a+")
    for x in s:
        fp.write(str(x) + '\n')

    print(s.__len__())

# coding=utf-8
import requests
import feedparser
import re
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_SERIALIZABLE
from datetime import timedelta
from datetime import date
from time import strftime
from bs4 import BeautifulSoup, Comment
import socket
import traceback
import time
import datetime
import multiprocessing
import xmlrpclib
from time import sleep

#server = xmlrpclib.ServerProxy("http://61.43.139.70:9004")
#print server.BuzzniTagger.segmentRpc("안녕하세요?")
#exit(0)


def register_crawl():
    con = psycopg2.connect(dbname='postgres', host="61.43.139.70",port=5432, user='postgres', password='postgres')
    cur = con.cursor()

    host = socket.gethostname()

    cur.execute("""lock crawler;""")
    cur.execute("""select count(*) from crawler;""")
    rst = cur.fetchone()
    crawl_id = rst[0]+1
    cur.execute("""insert into crawler (crawl_host, crawl_id) values (%s, %s);""", (host,crawl_id))
    con.commit()
    con.close()
    return crawl_id



def get_url(url):
    ret =  requests.get(url);
    if(ret.status_code != requests.codes.ok):
        raise Exception("Requests fail, url = %s, status code = %s" % (url, ret.status_code))

    return ret.text.encode("utf-8")

def flatten(dom):
    #comment erase
    comments = dom.find_all(text=lambda text:isinstance(text, Comment))
    [comment.extract() for comment in comments]

    #script decompose
    [s.decompose() for s in dom('script')]

    #for s in dom('img'):
    #    if(s.get('src') and (s['src'].startswith("http") or  s['src'].startswith("/"))):
    #        s.replace_with(" " + s['src'] + " ")

    for s in dom('a'):
        s.replace_with("")

    for s in dom('br'):
        s.replace_with("\n")

    return dom




def init(is_Super=False):
    con = psycopg2.connect(dbname='postgres', host="61.43.139.70",port=5432, user='postgres', password='postgres')
    cur = con.cursor()


    cur.execute("""update rss set crawl_id=0;""")
    cur.execute("""delete from crawler;""")

    if(is_Super):
        cur.execute("""delete from blog;""")
        cur.execute("""update rss set post_date=0, crawl_date=0;""")
        cur.execute("""alter sequence blog_id_seq  restart with 1;""")
    con.commit()

    exit(0)

def crawl():
    server = xmlrpclib.ServerProxy("http://61.43.139.70:9004")
    serv = xmlrpclib.ServerProxy("http://61.43.139.70:11002")

    crawl_id = register_crawl()
    print "crawler number : " + str(crawl_id)
    con = psycopg2.connect(dbname='postgres', host="61.43.139.70",port=5432, user='postgres', password='postgres')
    cur = con.cursor()

    fp = open("logs", "a+")
    while True:
        now =   datetime.datetime.today()
        delay = now - datetime.timedelta(hours=1)
        now = now.strftime("%Y%m%d%H%M%S")
        delay = delay.strftime("%Y%m%d%H%M%S")

        cur.execute("""lock rss in ACCESS EXCLUSIVE mode;""")
        cur.execute("""select * from rss where crawl_date < %s and crawl_id = 0 order by crawl_date asc limit 10;""" % (delay))

        list = cur.fetchall()

        if(len(list)==0):
            print "...."
            sleep(600)


        for record in list:
            cur.execute("""update rss set crawl_id=%s where id=%s;""" % (crawl_id, record[4]))

        con.commit()


        try:
            for record in list:

                cur.execute("""update rss set crawl_date=%s where id=%s;""" % (now, record[4]))
                con.commit()

                feed = feedparser.parse(get_url(record[0]))

                try:
                    for entry in reversed(feed.entries):
                        #print entry.link
                        post_date = long(strftime("%Y%m%d%H%M%S",entry.published_parsed))
                        #compare last post_date
                        if(post_date > record[1]):

                            if(record[5] == 1):
                                dom = BeautifulSoup(get_url(entry.link))

                                article = dom.find('div', {'class':'article'})

                                if(article):

                                    #erase ccl
                                    [s.decompose() for s in article.find_all("div", {"class" : re.compile(r"entry-ccl")})]

                                    #erase another category
                                    [s.decompose() for s in article.find_all("div", {"class" : re.compile(r"another_category.*")})]

                                    #erase tt-plugin
                                    [s.decompose() for s in article.find_all("div", {"class" : re.compile(r"tt-plugin.*")})]


                                    article = flatten(article)

                                    article_text = article.get_text().strip()
                                    #article = article.replace("크리에이티브 커먼즈 라이선스이 저작물은 에 따라 이용하실 수 있습니다.", "")


                            elif(record[5] == 2):

                                src = re.findall(".*?com/(.*?)/(.*)",entry.link)[0]
                                dom = BeautifulSoup(get_url("""http://blog.naver.com/PostView.nhn?blogId=%s&logNo=%s""" % (src[0], src[1])))



                                article = dom.find('div', {'class':re.compile(r"post-view.*")})

                                if(article):
                                    article = flatten(article)
                                    article_text = article.get_text().strip()


                            if(article):

                                buf = article_text
                                #buf = re.sub(u"[^a-z0-9\s가-힣ㄱ-ㅎㅏ-ㅣ]+", "", buf)
                                #buf = re.sub(u"[^ \uAC00-\uD7A3]+", "", buf)
                                #buf = re.sub("/", "", buf)
                                buf = re.sub("\s+", " ", buf)
                                buf = buf.lower()
                                article = buf.strip()

                                segmented= server.BuzzniTagger.segmentRpc(article)
                                subject =serv.TopicClassify.classifyTopic(article)[0]
                                score = subject['score']
                                subject= re.sub(u"[^a-z]", "" , subject['topic'])


                                cur.execute("""
                                INSERT INTO blog (post_url,post_date,post_title,post_content,post_html,category,tag,id,segmented,subject,score)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, nextval('blog_id_seq'), %s, %s, %s);""",
                                (entry.link, post_date, entry.title, article, article_text, 'category', 'tag', segmented, subject, score))
                                cur.execute("""update rss set post_date=%s, crawl_date=%s where id=%s;""" , (post_date, now, record[4]))
                                con.commit()

                            else:
                                raise Exception("No content founded, url=%s", (entry.link))



                except Exception, err:
                    cur.execute("""INSERT INTO error (rss_id,error)
                                    VALUES (%s, %s);""" , (record[4], traceback.format_exc()))
                    con.commit()

                cur.execute("""update rss set crawl_id=%s where id=%s;""" , (0, record[4]))
                con.commit()


            sleep(10)
        except Exception,err:

            traceback.print_exc(None,fp)

            #time.sleep(1)


def connection_test():
    while True:
        get_url('http://coran.co.kr/rss')
        print "test!!"



#init()
#crawl()
#exit(0)

jobs = []
for i in range(4):
    p = multiprocessing.Process(target=crawl)
    jobs.append(p)
    p.start()


for i in jobs:
    i.join()

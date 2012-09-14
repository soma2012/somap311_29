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
import traceback
import os
import codecs
from SimpleXMLRPCServer import SimpleXMLRPCServer


import sys
from jsonrpc.proxy import JSONRPCProxy



from twisted.internet import reactor, ssl
from twisted.web import server
import traceback

from jsonrpc.server import ServerEvents, JSON_RPC

import MySQLdb
import psycopg2
import xmlrpclib
from psycopg2 import pool
import psycopg2.extras
from datetime import datetime, timedelta
import PySQLPool
from jsonrpc.proxy import JSONRPCProxy
import MySQLdb.cursors
import traceback
#my_pool = PySQLPool.getNewConnection(db='twit_manager', host="61.43.139.70",user='twit', passwd='1rmdwjd', charset="UTF8")
#lucene = xmlrpclib.ServerProxy("http://61.43.139.70:7777")
#print lucene.reader2.query("안녕","")
#lucene = xmlrpclib.ServerProxy("http://61.43.139.70:7777")
#lucene = xmlrpclib.ServerProxy("http://61.43.139.70:7777")
lucene = xmlrpclib.ServerProxy("http://127.0.0.1:7777")
#print lucene.reader.query("안녕", "")
#exit(0)

pg_pool = psycopg2.pool.ThreadedConnectionPool(20,50, dbname='postgres', host="61.43.139.70",port=5432, user='postgres', password='postgres')

#con2 = psycopg2.connect(dbname='postgres', host="61.43.139.70",port=5432, user='postgres', password='postgres')
#cur2 = con2.cursor()

buznni = JSONRPCProxy("http://office2.buzzni.com:10100")
#polarity = buznni.opn_classify("화려한 그래픽 정말 좋았다")
seg = xmlrpclib.ServerProxy("http://61.43.139.70:9002")
polar = xmlrpclib.ServerProxy("http://61.43.139.70:11001")
def simpleTime(date):
    now = datetime.now() - timedelta(days=date)
    return now.strftime("%Y%m%d") + "000000"

class ExampleServer(ServerEvents):
    # inherited hooks
    def log(self, responses, txrequest, error):
        return


    def findmethod(self, method):
        if method in self.methods:
            return getattr(self, method)
        else:
            return None

    def get_polar(self, str):
        global polar
        ret = polar.TopicClassify.classifyTopic(str)


        ret=ret[0]

        score=float(ret['score'])
        if(ret['topic']=='neg'):
            score = -score-100

        score = round(3.5+ score/150, 1)
        return score

    # helper methods
    methods = set(['recent_twitter', 'recent_blog', 'recent', 'search', 'search_blog','search_twitter','get_pmi', 'get_blog_size'])
    def _get_msg(self, response):
        return ' '.join(str(x) for x in [response.id, response.result or response.error])

    def recent_twitter(self):
        print "start! recent twitter"
        con = MySQLdb.connect(db='twit_manager', host="61.43.139.70",user='twit', passwd='1rmdwjd', charset="UTF8")
        cur = con.cursor(cursorclass=MySQLdb.cursors.DictCursor)

        #cur.execute("select username, concat(substring(tweet,1,100),'...') from tweet_data order by update_time desc limit 50")
        #cur = PySQLPool.getNewQuery(my_pool)

        cur.execute("select * from tweet_analysis order by no desc limit 25")
        #print "G"
        ret = []
        for row in cur.fetchall():
            #print "select concat('http://twitter.com/', twitid, '/status/' , timestamp) as url, twitid as id, concat(substring(tweet,1,100),'...') as content, timestamp as date, 0 as type from tweet_data where no=%s limit 1"%(row['no'])
            cur.execute("select concat('http://twitter.com/', twitid, '/status/' , timestamp) as url, twitid as id, no, concat(substring(tweet,1,100),'...') as content, timestamp as date, 0 as type from tweet_data where no=%s limit 1"%(row['no']))

            buf = cur.fetchone()
            buf['polarity'] = row['polarity']
            #print buf['no']
            ret.append(buf)


        for c in ret:
            #print "select tweet_time as date from tweet_timedata where timestamp<=%s order by timestamp "%(c['date'])
            cur.execute("select tweet_time as date from tweet_timedata where timestamp<=%s order by timestamp desc limit 1 "%(c['date']))
            c['date']= str(cur.fetchone()['date'])


        return ret

    def recent_blog(self):

        print "start! recent blog"
        global pg_pool
        con = pg_pool.getconn()
        cur2 = con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur2.execute("select post_url as url, substring(post_content,0,100) || '...' as content, post_title as id, post_date as date, subject, 1 as type from blog order by post_date desc limit 25")
        ret =  cur2.fetchall()

        pg_pool.putconn(con)
        return ret

    def recent(self):
        print "start! recent"
        ret = []

        for x in self.recent_twitter():
            ret.append(x)


        for x in self.recent_blog():
            ret.append(x)

            try:
                for x in ret:
                    x['polarity'] = self.get_polar(x['content'])
            except:
                traceback.print_exc()

        return ret


    def search_blog(self,str, subject, fm, to):
        print "start! search blog"
        global lucene
        return lucene.reader.query(str,subject, fm,to)


    def search_twitter(self,str,subject, fm, to):
        print "start! search twitter"
        global lucene

        return lucene.reader2.query(str, subject, fm, to)

    def search(self,str, subject,fm, to):
        print "start! search"
        str =  seg.BuzzniTagger.segmentRpc(str)
        ret = []
        print lucene
        for x in self.search_blog(str, subject, fm, to):
            x['type']='blog'
            ret.append(x)

        for x in self.search_twitter(str, subject, fm, to):
            x['type']='twitter'
            ret.append(x)


        try:
            for x in ret:
                x['polarity'] = self.get_polar(x['content'])
        except:
            traceback.print_exc()

        print "end! search"

        return ret


    def get_pmi(self, subject, date):
        print "start! get_pmi"
        global pg_pool
        con = pg_pool.getconn()
        cur2 = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

        before = simpleTime(date)
        after = simpleTime(date-1)
        if(subject):
            cur2.execute("select * from pmi_keyword where date>=%s and date<%s and subject=%s limit 50",(before,after,subject))
        else:
            cur2.execute("select * from pmi_keyword where date>=%s and date<%s and subject!='none' and subject!='commercial' limit 50",(before,after))

        ret = cur2.fetchall()
        pg_pool.putconn(con)
        print "end! get_end"
        return ret

    def get_blog_size(self):
        global pg_pool
        con = pg_pool.getconn()
        cur = con.cursor()
        cur.execute("select count(*) from blog")
        ret = cur.fetchone()[0]
        pg_pool.putconn(con)
        return ret




root = JSON_RPC().customize(ExampleServer)
site = server.Site(root)


# 8007 is the port you want to run under. Choose something >1024
PORT = 8000
print('Listening on port %d...' % PORT)
reactor.listenTCP(PORT, site)
reactor.run()
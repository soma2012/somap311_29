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
from svmlight import SVMLight
from jsonrpc.proxy import JSONRPCProxy

"""
server = xmlrpclib.ServerProxy("http://61.43.139.70:9002")
print server.BuzzniTagger.segmentRpc("김성모")
exit(0)
"""

#t = xmlrpclib.ServerProxy("http://61.43.139.70:" + str(0+10028))
#serv = JSONRPCProxy("http://127.0.0.1:8000")

lucene = xmlrpclib.ServerProxy("http://61.43.139.70:7777")
#lucene = xmlrpclib.ServerProxy("http://127.0.0.1:7777")
for x in lucene.reader2.query("월북","", "", ""):
   print x
exit(0)
#exit(0)
#print reader.reader.get_pmi_relate(2, "바보")요
server = JSONRPCProxy("http://61.43.139.70:8000")
#for x in server.get_pmi("",0):
#    print x['word']

#print serv.reader2.query("안철수", "")[0]
#exit(0)
#print serv.query("안철수", "")
#exit(0)금
#server = JSONRPCProxy("http://127.0.0.1:8000")
#server = JSONRPCProxy("http://61.43.139.70:8000")
#가장 최근 트윗 한개를 가져옴 tuple의 번호는 db 레코드 번호와 일치
#print server.get_blog_size()
server.search_twitter("월북", "", "", "")
exit(0)

#for x in server.recent_twitter():
#    x['polarity'] = get_polar(x['content'])
#    print x
#exit(0)

#for x in server.search_twitter("북창동", "", "20120911000000", "20120912000000"):
for x in server.search("출신지", "", "20120906000000", "20120913000000"):
#for x in server.search_twitter("", "", "", ""):
    #print x['sub_score']
    print x['date']
    print x['url']
    print x['id']
    print x['subject'] + "####"
    print x['content']
exit(0)
#print server.recent()

#l =  server.recent_twitter()
exit(0)
for x in l:
    print x['date'] + x['content']
#print server.get_pmi(None,7)
#가장 최근 블로그 글 한개를 가져옴 tuple의 번호는 db 레코드 번호와 일치
#print server.recent_blog()[0]
#print server.search_blog("안철수", "")
exit(0)
#검색 결과를 반환 검색은 이중 배열로 되어있으며(20x3) 다만 검색결과가 부족하면 20개가 다 없을 수 있음
#2차 배열은 0은 id 1은 매칭된 점수 2는 강조된 본문 내용임
for x in server.search_blog("김포시아파트"):
    print x[0] + " " + x[2]
    print t.TopicClassify.classifyTopic(x[0])


server = xmlrpclib.ServerProxy("http://61.43.139.70:9009")
print server.BuzzniTagger.segmentRpc("안녕하세요")

#print server.reader.query("안철수출마")
exit(0)

server = xmlrpclib.ServerProxy("http://0.0.0.0:7777")
print server.reader.query("안철수출마")
exit(0)

num=0;

def refesh(start, end):
    global num
    num+=1

    con = psycopg2.connect(dbname='postgres', host="61.43.139.70",port=5432, user='postgres', password='postgres')
    cur = con.cursor()

    current = start
    chunk_size=5000
    #server = xmlrpclib.ServerProxy("http://61.43.139.70:1002" + str(num%4+8))
    server = xmlrpclib.ServerProxy("http://17.buzzni.com:10028/xmlrpc")
    while(True):


        cur.execute("select * from blog where id>%s and id<=%s order by id desc limit %s", (current,end, chunk_size))
        arr = cur.fetchall()
        if not arr:
            break

        for row in arr:

            """
            dom = BeautifulSoup(row[4])
            buf = dom.get_text()
            buf += " "
            buf = re.sub("http://.*?\s+", "", buf)
            buf = re.sub(u"[^0-9 가-힣ㄱ-ㅎㅏ-ㅣ]+", "", buf)
            buf = re.sub("\s+", " ", buf)
            buf = re.sub("", "", buf)
            buf = buf.lower()
            buf = buf.strip()
            #print buf
            #exit(0)
            buf2 = server.BuzzniTagger.segmentRpc(buf)
            cur.execute("update blog set post_content=%s, segmented=%s where id=%s", (buf,buf2, row[8]))
            """

            if(row[3]):
                print row[3]
                subject= server.TopicClassify.classifyTopic(row[3][0:1000])[0]

                cur.execute("update blog set subject=%s, score=%s where id=%s", (subject['topic'],subject['score'], row[8]))
                #print "######################"



        con.commit()
        current+=chunk_size
        print("finish row " + str(current))

def precision(start,end):
    total=0
    match=0
    #adult animation book car childcare commercial economy fashion food game health it love movie pet politics science sports travel world
    sub = ("food","food","game", "movie", "it", "food", "movie", "none", "it", "it", "food", "none", "movie", "none", "it", "")
    con = psycopg2.connect(dbname='postgres', host="61.43.139.70",port=5432, user='postgres', password='postgres')
    cur = con.cursor()

    current = start
    chunk_size=25000
    #server = xmlrpclib.ServerProxy("http://61.43.139.70:900" + str(start/25000+1))
    server2 = xmlrpclib.ServerProxy("http://office2.buzzni.com:10030")
    server = xmlrpclib.ServerProxy("http://127.0.0.1:8080")
    server3 = xmlrpclib.ServerProxy("http://17.buzzni.com:10028/xmlrpc")
    while(True):


        cur.execute("select * from blog where id>%s and id<=%s order by id asc limit %s", (current,end, chunk_size))
        arr = cur.fetchall()
        if not arr:
            break

        for row in arr:

            """
            dom = BeautifulSoup(row[4])
            buf = dom.get_text()
            buf += " "
            buf = re.sub("http://.*?\s+", "", buf)
            buf = re.sub(u"[^0-9 가-힣ㄱ-ㅎㅏ-ㅣ]+", "", buf)
            buf = re.sub("\s+", " ", buf)
            buf = re.sub("", "", buf)
            buf = buf.lower()
            buf = buf.strip()
            #print buf
            #exit(0)
            buf2 = server.BuzzniTagger.segmentRpc(buf)
            cur.execute("update blog set post_content=%s, segmented=%s where id=%s", (buf,buf2, row[8]))
            """


            if(row[9]):
                total+=1

                sp = server2.BuzzniTagger.segmentRpc(row[3])
                men = server3.TopicClassify.classifyTopic(row[3])
                my = server.classify(row[3])


                if(men):
                    print row[3][0:500]
                    print men[0]['topic']
                    print my
                    print "################################"

                    s = input()
                    if(s==1):
                        cur.execute("update blog set subject=%s where id=%s", (sp[0], row[8]))
                        con.commit()
                        match+=1
                    elif(s!=2):
                        break
                        #print row[10]
                        #print server.subject.getSubject(row[9])
                        #print "######################"



        con.commit()
        current+=chunk_size
        print("finish row " + str(match/(total/1.0)*100))

#precision(310,400)
#exit(0)

"""
jobs = []
for i in range(0,209115, 25000):
    p = multiprocessing.Process(target=refesh, args=(i,i+25000))
    jobs.append(p)
    p.start()

for i in jobs:
    i.join()
"""

jobs = []
for i in range(0,161069, 5000):
    p = multiprocessing.Process(target=refesh, args=(i,i+5000))
    jobs.append(p)
    p.start()

for i in jobs:
    i.join()

print("end job!")


exit(0)

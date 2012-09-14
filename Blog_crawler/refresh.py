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
from random import choice

def refresh(start, end):
    idx=choice(range(0,4))
    con = psycopg2.connect(dbname='postgres', host="61.43.139.70",port=5432, user='postgres', password='postgres')
    cur = con.cursor()

    current = start
    chunk_size=25000
    print "http://61.43.139.70:" + str(idx+10028)
    server = xmlrpclib.ServerProxy("http://61.43.139.70:" + str(idx+10028))
    #server = xmlrpclib.ServerProxy("http://17.buzzni.com:10028/xmlrpc")
    while(True):


        cur.execute("select * from blog where id>%s and id<=%s and subject is null order by id desc limit %s", (current,end, chunk_size))
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
            from time import sleep
            if(row[3]):
                retrynum=0
                while True:
                    try:
                        subject= server.TopicClassify.classifyTopic(row[3].decode("utf-8")[0:500].encode("utf-8"))[0]
                        #print subject
                        cur.execute("update blog set subject=%s, score=%s where id=%s", (subject['topic'],subject['score'], row[8]))
                        con.commit()
                        break
                        #print "######################"
                    except Exception,e:
                        if retrynum>3:
                            break
                        print e
                        sleep(60*5)
                        retrynum+=1




        current+=chunk_size
        print("finish row " + str(current))

#refresh(1,1000)
#exit(0)

jobs = []
for i in range(0,161069, 25000):
    p = multiprocessing.Process(target=refresh, args=(i,i+25000))
    jobs.append(p)
    p.start()

for i in jobs:
    i.join()

print("end job!")

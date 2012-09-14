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
import MySQLdb
from jsonrpc.proxy import JSONRPCProxy
from time import sleep



server = xmlrpclib.ServerProxy("http://61.43.139.70:11001")
def refresh(start, end):
    global server
    idx=choice(range(0,4))
    con = MySQLdb.connect(db='twit_manager', host="61.43.139.70",user='twit', passwd='1rmdwjd', charset="UTF8")
    cur = con.cursor()

    current = start
    chunk_size=100
    #print "http://61.43.139.70:" + str(idx+10028)
    #server = xmlrpclib.ServerProxy("http://61.43.139.70:" + str(idx+10028))
    #server = xmlrpclib.ServerProxy("http://17.buzzni.com:10028/xmlrpc")
    #server = JSONRPCProxy("http://office2.buzzni.com:10100")

    while(True):


        cur.execute("select no, tweet from tweet_data where no>=%s and no<%s order by timestamp asc limit %s", (start, end, chunk_size))

        arr = cur.fetchall()
        #print len(arr)
        if(len(arr)==0):
            return -1
        #print "XX"
        for row in arr:
            print row[0]
            cur.execute("select * from tweet_analysis where polarity is not null and no=%s limit 1", (row[0]))
            arr2 = cur.fetchone()

            if(arr2):
                continue


            if(row[1]):
                retrynum=0
                while True:
                    try:
                        #print row[1].decode("utf-8").encode("utf-8")

                        ret = server.TopicClassify.classifyTopic(row[1])[0]
                        score=float(ret['score'])

                        if(ret['topic']=='neg'):
                            score = -score

                        #print row[0]
                        score = round(3.5+ score/100, 1)
                        #if(float(ret['score'])>50 and ret['topic']=='neg'):
                        cur.execute("insert into tweet_analysis (no,polarity) values (%s, %s)", (row[0],score))
                        con.commit()
                        break
                        #print "######################"
                    except Exception,e:
                        if retrynum>3:
                            break
                        print e
                        retrynum+=1



        current+=chunk_size
        print("finish row " + str(current))
        return 0

i=30006163
while(True):
    ret = refresh(i,i+100)

    if ret == -1:
        print "X"
        sleep(60);
    else:
        i+=100

#exit(0)

jobs = []
for i in range(0,161069, 25000):
    p = multiprocessing.Process(target=refresh, args=(i,i+25000))
    jobs.append(p)
    p.start()

for i in jobs:
    i.join()

print("end job!")

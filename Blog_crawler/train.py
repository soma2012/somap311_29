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
from SimpleXMLRPCServer import SimpleXMLRPCServer

import rpcutil
import sys
from jsonrpc.proxy import JSONRPCProxy

def make_train_data():

    _QA_RPC = rpcutil.Client("http://office2.buzzni.com:10100")

    #{adult,animation,baseball,basketball,book,car,childcare,commercial,economy,entertainment,fashion,food,game,health,infotech,love,
    # movie,pet,politics,science,soccer,sports,travel,volleyball,world}

    eng = ["animation", "baseball", "basketball", "book", "car", "childcare", "commercial", "economy", "entertainment",
           "fashion", "food", "game", "health", "infotech", "love", "movie", "pet", "politics", "science", "soccer","sports" "travel", "volleyball", "world"]

    keywordlist = ["애니메이마션 -파워포인트", "야구", "농구", "책", "신차 -중고차", "육아", "급매 아파트 원룸", "경제 -인강", "드라마 예능 공연",
                   "패션", "음식 맛집", "게임", "헬스", "IT 소프트웨어 플랫폼 스마트", "사랑 연애", "영화", "애완 강아지 고양이 -용품",  "정치", "과학", "축구","스포츠", "여행", "배구", "국제 뉴스 토픽"]

    #keywordlist = ["IT 소프트웨어 플랫폼 스마트","스포츠", "드라마 예능 공연"]
    #eng = ["infotech", "sports", "entertainment"]

    encode ="euc-kr"
    import re
    split_re = re.compile("[\n|.|!]")

    idx=0
    for keyword in keywordlist:
        print keyword
        print "##############################################"

        fp = open("/home/xorox90/tp/"+eng[idx], "w+")

        datalist,num = _QA_RPC.search(**{"query":keyword,"page":50})
        for each in datalist:


            content= _QA_RPC.get_content(**{"url":each['link']})
            if(content==None):
                content =""

            content = content.replace(","," ").replace(u"앱으로 보기 작게 크게","")
            content = re.sub("http://[a-z0-9/.\?&=_]*\s", "", content)
            slist = split_re.split(content)
            for sen in slist:
                if len(sen) < 10 or len(sen)>1500:
                    continue

                fp.write(sen.encode("utf-8")+"\n")
                #print sen
                #polarity = server.opn_classify(sen)
                #if polarity==None or (polarity>2 and polarity <4):
                #    continue
                #print polarity,sen
        idx+=1

def make_polar_train_data():
    server = JSONRPCProxy("http://office2.buzzni.com:10100")

    eng = ["animation", "baseball", "basketball", "book", "car", "childcare", "commercial", "economy", "entertainment",
           "fashion", "food", "game", "health", "infotech", "love", "movie", "pet", "science", "politics", "soccer", "travel", "volley", "world"]

    for x in eng:
        pros=[]
        cons=[]

        fp = open("/home/xorox90/tp/"+x, "r")
        fp2 = open("/home/xorox90/tp/polar/p_"+x, "a")
        fp3 = open("/home/xorox90/tp/polar/c_"+x, "a")

        for line in fp.read().split("\n"):
            idx=0
            while(True):
                try:
                    #print line
                    polarity = server.opn_classify(line)

                    if polarity==None or (polarity>2 and polarity <4):
                        break
                    elif(polarity <= 2):
                        cons.append(str(polarity) + " " +  line)
                    else:
                        pros.append(str(polarity) + " " + line)

                    break

                except Exception, err:
                    traceback.print_exc()
                    idx+=1
                    if(idx==3):
                        break



        print x
        for x in pros:
            fp2.write(x + "\n")

        for x in cons:
            fp3.writelines(x + "\n")
            #print len(pros) + "   " + len(cons)



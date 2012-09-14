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
import re
import sys
from jsonrpc.proxy import JSONRPCProxy

from psycopg2 import extras

#9001
#9000
"""
server = xmlrpclib.ServerProxy("http://61.43.139.70:9008")
print server.BuzzniTagger.segmentRpc("안녕하세요")
exit(0)
"""

server = xmlrpclib.ServerProxy("http://61.43.139.70:9003")
#subs = ("adult","animation", "book", "car", "childcare", "commercial", "economy", "fashion", "food", "game", "health", "it", "love", "movie", "pet", "politics", "science", "sports", "travel", "world")


#{adult,animation,baseball,basketball,book,car,childcare,commercial,economy,entertainment,
# fashion,food,game,health,infotech,love,movie,pet,politics,science,soccer,sports,travel,volleyball,world}

subs = ("animation", "baseball", "basketball", "book", "car", "childcare", "commercial", "economy", "entertainment",
       "fashion", "food", "game", "health", "infotech", "love", "movie", "pet", 'politics', "science", "soccer", "sports", "travel", "volleyball", "world")

def read_dic(sub):


    file = "/home/xorox90/tp/%s"%(sub,)
    #os.path.exists(file)
    fp = codecs.open(file, "r", encoding="utf-8")

    ret = fp.read()

    ret = re.sub(u"[^\s\u3040-\u309F\u30A0-\u30FF\u31F0-\u31FF0-9A-Za-z가-힣]", " ", ret)
    ret = re.sub("(\s)+", r"\1", ret)
    arr =[]
    for x in ret.split("\n"):
        if(len(x)>20):
            arr.append(x)


    #ret = re.sub("(\s)+", r"\1", ret)
    return arr


def make_dic(subs):
    global server

    dic = codecs.open("/home/xorox90/sub_dic", "w+", encoding="utf-8")

    s = set()

    for sub in subs:
        print sub
        for line in read_dic(sub):
            #line = re.sub("(\s)+", " ", line)

            line = server.BuzzniTagger.segmentRpc(line)
            line = line.strip()

            for word in re.split("\s", line):
                s.add(word)

    for word in s:
        dic.write(word + " ")



def load_dic():
    dic = {}
    fp = codecs.open("/home/xorox90/sub_dic","r", encoding="utf-8")

    index=1
    for word in fp.read().split():
        dic[word]=index
        dic[index]=word
        index+=1


    return dic

def process_dic(x):
    dic = {}
    fp = codecs.open("/home/xorox90/%s_dic"%(x),"r", encoding="utf-8")
    fp2 = codecs.open("/home/xorox90/%s_dic_p"%(x),"w+", encoding="utf-8")
    index=1

    for word in fp.read().split():
        dic[index]=word
        index+=1

    for x in range(1,index):
        fp2.write(str(x) + ":" + dic[x] + "\n")



def apply_dic(dic, str):
    #global server
    #str = server.BuzzniTagger.segmentRpc(str)
    str = str.strip()

    l = {}
    index=1
    for word in re.split("\s", str):
        if(dic.has_key(word)):
            l[dic[word]]=1
        index+=1

    return l;

def classify_init():
    #make_dic(subs)
    dic = load_dic()

    x = []
    y = []
    cid = 1
    for sub in subs:
        print sub
        lines = read_dic(sub)
        for line in lines:
            x.append(apply_dic(dic, line))
            y.append(cid)
        cid+=1


    svm = SVMLight("/home/xorox90/svm", labels=y, vectors=x)
    print "END!"




def classify(str):
    global dic
    global subs
    svm = SVMLight("/home/xorox90/svm", model="sub_model", cleanup=True)
    x = []
    x.append(apply_dic(dic,str))

    return subs[svm.classify(vectors=x)[0]-1]

def test():
    my = xmlrpclib.ServerProxy("http://61.43.139.70:11002")
    con = psycopg2.connect(dbname='postgres', host="61.43.139.70",port=5432, user='postgres', password='postgres')
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("select segmented,subject,score from blog order by id asc limit 5000")
    for sub in cur.fetchall():
        sub['segmented'] = re.sub(u"[^\s\u3040-\u309F\u30A0-\u30FF\u31F0-\u31FF0-9A-Za-z가-힣]", " ", sub['segmented'].decode("utf-8"))
        sub['segmented'] = re.sub("(\s)+", r" ", sub['segmented'])
        print my.TopicClassify.classifyTopic(sub['segmented'])[0]
        print sub['segmented']


test()
exit(0)

#process_dic("sub")
#process_dic("polar")
#exit(0)
#classify_init()
#print "ENDEND!!!"
#exit(0)
con = psycopg2.connect(dbname='postgres', host="61.43.139.70",port=5432, user='postgres', password='postgres')
cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

cur.execute("select segmented,subject,score from blog order by id asc limit 5000")


dic = load_dic()
svm = SVMLight("/home/xorox90/svm", model="sub_model", cleanup=True)
ans = []
gold = []
x = []
y = []
index =1




for sub in cur.fetchall():

    sub['segmented'] = re.sub(u"[^\s\u3040-\u309F\u30A0-\u30FF\u31F0-\u31FF0-9A-Za-z가-힣]", " ", sub['segmented'].decode("utf-8"))
    sub['segmented'] = re.sub("(\s)+", r" ", sub['segmented'])
    #print sub['subject']


    if(sub['subject']=='adult' or len(sub['segmented'])==0):
        continue

    x.append(apply_dic(dic, sub['segmented']))
    gold.append(sub['subject'])
    y.append(sub['segmented'])
    index+=1


ans = svm.classify(vectors=x)
print svm._output_fname
#print ans[0]

fp = open("/home/xorox90/test", "w+")
match=0
total=0
real=0
for i in range(0,len(ans)):
    if(ans[i]!=0 and (subs[ans[i]-1]==gold[i] or subs[ans[i]-1]=='commercial')):
        match+=1
        total+=1
    elif(ans[i]!=0):
        ret=""
        ret+= subs[ans[i]-1] + " " +gold[i] + "\n"
        ret+= y[i] +"\n"
        ret+= '############################' + "\n"

        fp.write(ret.encode("utf-8"))
        total+=1



    real+=1
print str(real) + " " + str(match) + " " + str(total)
print(match/(total/1.0))
exit(0)

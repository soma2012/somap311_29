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
import rpcutil
import sys
from jsonrpc.proxy import JSONRPCProxy
import psycopg2



#subs = ("adult","animation", "book", "car", "childcare", "commercial", "economy", "fashion", "food", "game", "health", "it", "love", "movie", "pet", "politics", "science", "sports", "travel", "world")
subs = ("animation", "baseball", "basketball", "book", "car", "childcare", "commercial", "economy", "entertainment",
       "fashion", "food", "game", "health", "infotech", "love", "movie", "pet", "science", "politics", "soccer","sports", "travel", "volleyball", "world")
#{      animation,baseball,basketball,book,car,childcare,commercial,economy,entertainment,
# fashion,food,game,health,infotech,love,movie,pet,politics,science,soccer,sports,travel,volleyball,world}

def read_dic(sub,filetype='train'):


    file = "/home/xorox90/topic/%s/%s/%s.txt"%(filetype,sub,sub)
    #os.path.exists(file)
    fp = codecs.open(file, "r", encoding="utf-8")

    ret = fp.read()
    #ret = re.sub(u"[^\sa-z가-힣]+", "", ret)
    ret = re.sub("(\s)+", r"\1", ret)
    return ret.split("\n")[:-1]


def make_dic(subs):

    dic = codecs.open("/home/xorox90/dic", "w+", encoding="utf-8")
    s = set()

    for sub in subs:
        for words in read_dic(sub):
            for word in words.split(" "):
                s.add(word)

    for word in s:
        dic.write(word + " ")




def load_dic():
    dic = {}
    fp = codecs.open("/home/xorox90/dic","r", encoding="utf-8")

    index=1
    for word in fp.read().split():
        dic[word]=index
        dic[index]=word
        index+=1


    return dic

def apply_dic(dic, str):
    #server = xmlrpclib.ServerProxy("http://61.43.139.70:9002")
    #str = server.BuzzniTagger.segmentRpc(str)
    l = {}
    index=1
    for word in str.split(" "):
        if(dic.has_key(word)):
            l[dic[word]]=1
        index+=1

    return l;

def classify_init():
    make_dic(subs)
    dic = load_dic()

    x = []
    y = []
    cid = 1
    for sub in subs:
        lines = read_dic(sub)
        for line in lines:
            x.append(apply_dic(dic, line))
            y.append(cid)
            #print "W"
        cid+=1


    svm = SVMLight("/home/xorox90/svm", labels=y, vectors=x)
    print "END!"




def classify(str):
    global dic
    global subs
    svm = SVMLight("/home/xorox90/svm", model="model", cleanup=True)
    x = []
    x.append(apply_dic(dic,str))

    return subs[svm.classify(vectors=x)[0]-1]



dic = load_dic()
svm = SVMLight("/home/xorox90/svm", model="model", cleanup=True)
ans = []
gold = []
x = []
index =1
for sub in subs:
    lines = read_dic(sub, 'test')

    for line in lines:
        x.append(apply_dic(dic, line))
        gold.append(index)

    index+=1


ans = svm.classify(vectors=x)

match=0
total=0
for i in range(0,len(ans)):
    if(ans[i]==gold[i]):
        match+=1
    total+=1

print(match/(total/1.0))
exit(0)



server = SimpleXMLRPCServer(("localhost", 8080))
server.register_function(classify, "classify")
server.serve_forever()

exit(0)
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




subs = ("adult","animation", "book", "car", "childcare", "commercial", "economy", "fashion", "food", "game", "health", "it", "love", "movie", "pet", "politics", "science", "sports", "travel", "world")


server = xmlrpclib.ServerProxy("http://61.43.139.70:9001")
def segment(str):
    #server = xmlrpclib.ServerProxy("http://61.43.139.70:9001")
    global server
    str = server.BuzzniTagger.segmentRpc(str)
    return str

def read_dic(sub,filetype='train'):


    file = "/home/xorox90/topic/%s/%s/%s.txt"%(filetype,sub,sub)
    #os.path.exists(file)
    fp = codecs.open(file, "r", encoding="utf-8")

    ret = fp.read()
    ret = re.sub(u"[^[\s가-힣]+", "", ret)
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
        #dic[index]=word
        index+=1


    return dic


def apply_dic(dic, str):

    l = {}
    index=1
    for word in str.split(" "):
        if(dic.has_key(word)):
            l[dic[word]]=1
        index+=1

    return l;



#make_dic(subs)

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
print svm._output_fname
exit(0)



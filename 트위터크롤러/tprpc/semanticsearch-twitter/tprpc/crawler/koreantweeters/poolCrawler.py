#!/usr/bin/python
# coding=utf-8

import httplib,urllib2
import sgmllib,string
import MySQLdb
import re,time

version = "v0.02"
error_cnt = 0 # 에러 카운트가 10 이상이면 종료 하는것으로..
workername = open('env').readline().replace("\n","")
print workername + "  crawler start!"
out = open('tweeters','w')
visited = {}
tweeters = {}

def crawlTweet(id = "/dir/list/0"):
    global visited,tweeters
    if visited.has_key(id) :
        return
    visited[id] = 1
    print id+'...',
    try:
        data = urllib2.urlopen("http://koreantweeters.com%s" % id).read()
    except urllib2.HTTPError, e:
        print "HTTP error: %d" % e.code
    except urllib2.URLError, e:
        print "Network error: %s" % e.reason.args[1]
    nextUrls = set(re.findall("/dir/list/[0-9/]+\"",data))
    #print nextUrl

    tweeter = set(re.findall("@\w+",data))
    #print tweeter
    sz = 0
    for twitid in tweeter:
        if not tweeters.has_key(twitid):
            tweeters[twitid] = 1
            out.write(twitid+"\n")
            sz += 1
    print sz
    for nextUrl in nextUrls:
        #print nextUrl
        crawlTweet(nextUrl.replace('"',''))

crawlTweet()

out.close()

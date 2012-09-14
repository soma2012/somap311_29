#!/usr/bin/python
# coding=utf-8

import httplib,urllib2
import sgmllib,string
import MySQLdb
import re,time

version = "v0.02"
error_cnt = 0 # 에러 카운트가 10 이상이면 종료 하는것으로..
workername = open('env').readline().replace("\n","") + version
print workername + "  crawler start!"
out = open('tweeters','w')
visited = {}

def crawlTweet(id):
    global visited
    print '%d...'%id,
    try:
        data = urllib2.urlopen("http://twtkr.olleh.com/fpl.php?d=r&s=&p=%d&n=100" % id).read()
    except urllib2.HTTPError, e:
        print "HTTP error: %d" % e.code
    except urllib2.URLError, e:
        print "Network error: %s" % e.reason.args[1]

    tweeter = set(re.findall("@\w+",data))
    #print tweeter
    sz = 0
    for twitid in tweeter:
        if not visited.has_key(twitid) :
            visited[twitid] = 1
            out.write(twitid+"\n")
            sz += 1
    print sz
    if sz == 0:
        return

for a in xrange(1,1000,1):
    crawlTweet(a)
out.close()

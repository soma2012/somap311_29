#!/usr/bin/python26
# coding=utf-8

import httplib,urllib2
import sgmllib,string
import MySQLdb
import re,time,sys
import json

#
# AllTweetCrawler 한사용자의 트윗을 가능한 모두 크롤링하는 크롤러 스크립트
#

version = "v0.02"
workername = 'emilejong'
print workername + " get timestamp modifier start!"

db = MySQLdb.connect(host = 'twit.tprpc.com', user='twit', passwd='1rmdwjd', db='twit_manager', charset='utf8')
cursor = db.cursor(MySQLdb.cursors.DictCursor)

while 1:
    # DB에서 데이터 읽어오기

    query = "SELECT * FROM `tweet_timedata` WHERE `tweet_time` IS NULL LIMIT 1"
    cursor.execute(query)
    timedata = cursor.fetchone()
    
    #데이터가 없을 경우~
    if not timedata:
        time.sleep(60) # 1분 쉰다 
        continue
    

    timestamp = timedata['timestamp']

    # 시간 읽기 위해 api 요청 하는 부분 
    try:
        url = "http://api.twitter.com/1/statuses/show/%s.json"%timestamp
        print url
        data = urllib2.urlopen(url).read()
        print data
        tweet = json.loads(data)

    except urllib2.HTTPError, e:
        print "HTTP error: %d" % e.code
        #putLog('%s:crawlTweet'%id,'error',"HTTP error: %d" % e.code)
        time.sleep(60)
        continue
    except urllib2.URLError, e:
        print "Network error: %s" % e.reason.args[1]
        continue
    except KeyboardInterrupt, SystemExit:
        print '사용자 종료'
        sys.exit()
    except:
        continue

    # 시간 처리
    ts = time.strftime('%Y-%m-%d %H:%M:%S',time.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
    print ts
    
    query = "UPDATE `tweet_timedata` SET `tweet_time` = '%s' WHERE `no` = '%s'"%(ts,timedata['no'])
    #print query
    cursor.execute(query)
    db.commit()
    print "query ok"
#    time.sleep(5)

cursor.close()
db.close()


#!/usr/bin/python
# coding=utf-8

import sgmllib,string
import MySQLdb
import re,time

# 멘션한 트위터 사용자 추가

version = "v0.01"
print "mention crawler start!"

db = MySQLdb.connect(host = 'twit.tprpc.com', user='twit', passwd='1rmdwjd', db='twit_manager', charset='utf8')
db2 = MySQLdb.connect(host = 'twit.tprpc.com', user='twit', passwd='1rmdwjd', db='twit_manager', charset='utf8')

cursor = db.cursor(MySQLdb.cursors.DictCursor)
cursor2 = db2.cursor(MySQLdb.cursors.DictCursor)

cnt = 0
term = 1000
offset = 0
until = 10000000
twitters = {}

while until > offset:
    print "%d] %d"%(offset,cnt)

    query = "SELECT * FROM `tweet_data` WHERE `no` > %d ORDER BY `no` ASC LIMIT %d"%(offset,term)
    cursor.execute(query)
    numrows = int(cursor.rowcount)

    for i in range(numrows):

        row = cursor.fetchone()
        data = row['tweet']

        tweeter = set(re.findall("@[a-z0-9_-]+ ",data))
        
        for twitid in tweeter:
            twitid = twitid[1:]
            twitid = twitid[:-1]
            
            if len(twitid) < 2:
                continue

            if not twitters.has_key(twitid):
                twitters[twitid] = 1
                
                print twitid
            
                try:
                    query = "INSERT INTO `tweeter_pool` (`twit_id`) VALUES ('%s')"%(twitid)
                    print query
                    cursor2.execute(query)
                    db2.commit()
                    arow = cursor2.rowcount
                except:
                    arow = 0
                cnt += arow

    offset += term

cursor.close()
cursor2.close()
db.close()
db2.close()


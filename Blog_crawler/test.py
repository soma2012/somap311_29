# coding=utf-8
import MySQLdb
import psycopg2
from psycopg2 import extras
import MySQLdb.cursors
from jsonrpc.proxy import JSONRPCProxy
import xmlrpclib
import re
from jsonrpc.proxy import JSONRPCProxy
server = JSONRPCProxy("http://office2.buzzni.com:10100")

test = {}
test['polarity']="sdf"
print test
exit(0)
def polar_test():
    con = MySQLdb.connect(db='twit_manager', host="61.43.139.70",user='twit', passwd='1rmdwjd', charset="UTF8")
    cur = con.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    cur.execute("select * from tweet_data order by no desc limit 1000")

    qq2 = xmlrpclib.ServerProxy("http://61.43.139.70:11001")
    for tt in cur.fetchall():
        #print tt['tweet']
        ret = qq2.TopicClassify.classifyTopic(tt['tweet'])
        if(ret[0]!=None):
            ret=ret[0]

            score=float(ret['score'])
            if(ret['topic']=='neg'):
                score = -score

            score = round(3.5+ score/90, 1)
            #print 3.0 + score/50

            if(score>=3 and ret['topic']=='pos'):
                print server.opn_classify(tt['tweet'])
                print str(score) + " " + ret['score'] + " " + ret['topic']
                print tt['tweet']
                print "##################"

def test():
    my = xmlrpclib.ServerProxy("http://61.43.139.70:11002")
    con = psycopg2.connect(dbname='postgres', host="61.43.139.70",port=5432, user='postgres', password='postgres')
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("select segmented,subject,score from blog order by id asc limit 100")
    for sub in cur.fetchall():
        sub['segmented'] = re.sub(u"[^\s\u3040-\u309F\u30A0-\u30FF\u31F0-\u31FF0-9A-Za-z가-힣]", " ", sub['segmented'].decode("utf-8"))
        sub['segmented'] = re.sub("(\s)+", r" ", sub['segmented'])

        ret = my.TopicClassify.classifyTopic(sub['segmented'])[0]
        print ret
        print sub['segmented']


my = xmlrpclib.ServerProxy("http://61.43.139.70:11002")
con = psycopg2.connect(dbname='postgres', host="61.43.139.70",port=5432, user='postgres', password='postgres')
cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)


#polar_test()
#print '########################################################'
#문제점2 토픽 분류에 adult가 들어가있는데 .svmlight에 넣지 않은 토픽임
#test()

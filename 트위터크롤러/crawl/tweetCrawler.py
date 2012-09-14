#!/usr/bin/python
# coding=utf-8

import httplib,urllib2
import sgmllib,string
import MySQLdb
import re,time,sys

version = "v0.03"
error_cnt = 0 # 에러 카운트가 10 이상이면 종료 하는것으로..
workername = open('env').readline().replace("\n","") + version
print workername + "  crawler start!"

db = MySQLdb.connect(host = 'twit.tprpc.com', user='twit', passwd='1rmdwjd', db='twit_manager', charset='utf8')
cursor = db.cursor(MySQLdb.cursors.DictCursor)

# 태그 정리하는 유틸리티
class Stripper(sgmllib.SGMLParser):
    def __init__(self):
        self.data = []
        sgmllib.SGMLParser.__init__(self)
    def unknown_starttag(self, tag, attrib):
        self.data.append(" ")
    def unknown_endtag(self, tag):
        self.data.append(" ")
    def handle_data(self, data):
        self.data.append(data)
    def gettext(self):
        text = string.join(self.data, "")
        return string.join(string.split(text)) # normalize whitespace

def stripTag(text):
    s = Stripper()
    s.feed(text)
    s.close()
    return s.gettext()

#headers = {"Accept":"text/html", "User-Agent":"Mozilla/5.0 (Linux; U; Android 2.3.5; ko-kr; HTC_DesireHD_A9191 Build/GRJ90) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"}

# 로그 저장 
def putLog(action, resultcode, raw):
    global cursor,db,workername
    global error_cnt

    try:
        action = action.replace("'","\\'")
        resultcode = resultcode.replace("'","\\'")
        raw = raw.decode('UTF-8').replace("\\","\\\\").replace("'","\\'")
        #raw = raw.replace("'","\\'") #.encode('UTF-8')
        #print raw
        query = "INSERT INTO `log` (`id`,`worker`,`action`,`result_code`,`time`,`raw`) VALUES (NULL, '%s', '%s', '%s', CURRENT_TIMESTAMP, '%s')"%(workername, action, resultcode, raw)
        cursor.execute(query)
        db.commit()
    except:
        error_cnt += 1

# 트위터 아이디 가져오기 
def getTweeter():
    global cursor,db,workername
    
    # 이미 작업중인지 확인하기 위함
    query = "SELECT * FROM `tweeter_pool` WHERE `using` = '1' AND `latest_worker` = '%s' "%workername
    cursor.execute(query)
    data = cursor.fetchone()
    if data :
        return data

    # locking pool
    query = "UPDATE `tweeter_pool` SET `using` = '1', `latest_worker` = '%s', `crawl_time` = NOW() WHERE `using` = '0' ORDER BY `crawl_time` ASC LIMIT 1 "%workername
    cursor.execute(query)
    db.commit()

    query = "SELECT * FROM `tweeter_pool` WHERE `using` = '1' AND `latest_worker` = '%s' "%workername
    cursor.execute(query)
    data = cursor.fetchone()

#print data['twit_id']
    return data


def poolUnlock(code=0):
    global workername
    
    try:
        query = "UPDATE `tweeter_pool` SET `using` = '%d' WHERE `latest_worker` = '%s' AND `using` = '1'"%(code,workername)
        cursor.execute(query)
        db.commit()
    except:
        print "asdf"


def putTweet(id,data):
    global cursor,db,workername

    getrow = 0
    affectrow = 0
    maxtimestamp = 0
    for tweet in data:
        maxtimestamp = max(maxtimestamp, tweet['timestamp'])
        
        try:
            tweet['tweet'] = tweet['tweet'].decode('UTF-8').replace("\\","\\\\").replace("'","\\'")
            #tweet['tweet'] = tweet['tweet'].replace("'","\\'")
            query = "INSERT INTO `tweet_data` (`twitid`, `username` ,`timestamp` ,`tweet` ,`worker` ,`update_time`) SELECT '%s', '%s',  '%s',  '%s',  '%s', CURRENT_TIMESTAMP FROM DUAL WHERE NOT EXISTS (SELECT * FROM `tweet_data` WHERE `twitid`='%s' AND `username`='%s' AND `timestamp` = '%s')"%(id, tweet['username'],tweet['timestamp'],tweet['tweet'],workername,id,tweet['username'],tweet['timestamp'])
            cursor.execute(query)
        except:
            print tweet['tweet']
            putLog('%s:putTweet'%id,'tweetErr',tweet['tweet'])
        
        getrow += 1
        affectrow += cursor.rowcount
        
    print "%d...pushed!"%affectrow

    # unlocking pool
    #print maxtimestamp

    poolUnlock()
    #putLog('%s:putTweet'%id,'crawlok',"%d - %d...pushed!"%(getrow, affectrow))

# 해당 아이디 크롤 진입점
# http://mobile.twitter.com/{$id}
#conn = httplib.HTTPConnection("mobile.twitter.com")
def crawlTweet(id = "xguru", option=''):
    ret = {}
    ret['status'] = 'ok'
    print id+'...',
    try:
        #기존코드에 버그가 있는거 같아서 사용안함
        #conn.request("GET", "/%s"%id, "", headers)
        #response = conn.getresponse()
        #data = response.read()
        url = "http://mobile.twitter.com/%s%s" % (id,option)
        print url
        data = urllib2.urlopen(url).read()
    except urllib2.HTTPError, e:
        print "HTTP error: %d" % e.code
        putLog('%s:crawlTweet'%id,'error',"HTTP error: %d" % e.code)
        if e.code == 403 :
            ret['status'] = '403'
			#time.sleep(60)
        elif e.code == 404:
            ret['status'] = '404'
        else :
            ret['status'] = 'HTML error'
        return ret
    except urllib2.URLError, e:
        print "Network error: %s" % e.reason.args[1]
        putLog('%s:crawlTweet'%id,'error',"Network error: %s" % e.reason.args[1])
        ret['status'] = 'Net error'
        return ret
    
    # 다 읽어오지 못하는 경우 
    if data.find('</html>') == -1:
        ret['status'] = 'HTML error'
        return ret
    #conn.close)
    #print data # 데이터를 잘 받아왔는지 확인
    tweetCnt = 0
    crawlTweets = []
    originaldata = data
    while 1:
        tweetStartStr = '<table class="tweet">'
        tweetEndStr = '</table>'

        tweetStartPos = data.find(tweetStartStr)
        #print data

        if tweetStartPos != -1:
            #print "%d %d"%(tweetCnt,tweetStartPos)
            data = data[data.find(tweetStartStr)+len(tweetStartStr):] # 불필요한 데이터 끊기

            tweetCnt = tweetCnt + 1
            tweetData =  data[:data.find(tweetEndStr)] #이번에 필요한 데이터만
            #print tweetData

            token = '</span>'
            tweetData = tweetData[tweetData.find(token)+len(token):]
            username = tweetData[:tweetData.find('\n')]
            #print username

            token = 'name="tweet_'
            tweetData = tweetData[tweetData.find(token)+len(token):]
            timestamp = tweetData[:tweetData.find('"')]
            #print timestamp

            token = 'class="tweet-text">'
            tweetData = tweetData[tweetData.find(token)+len(token):]
            rawTweet = tweetData[:tweetData.find('</div>')]
            #print rawTweet
            tweet = stripTag(rawTweet)
            #print tweet

            crawlTweets.append({'username' : username , 'timestamp' : timestamp, 'tweet' : tweet})

        else:
            print "%d..read!"%tweetCnt,
            break

    #트윗이 없다
    if tweetCnt == 0:
        putLog('%s:crawlTweet'%id,'tweetCnt=0',originaldata)
        print "...tweetCnt = 0"
        ret['status'] = 'zero'

    #이전 트윗 보기
    data = data[data.find('?max_id='):] 
    maxId = data[:data.find('"')]

    #print crawlTweets
    ret['userId'] = id
    ret['crawlTweets'] = crawlTweets
    ret['crawlTweetCnt'] = tweetCnt
    ret['nextId'] = maxId
    return ret

#도입부

#한 사용자에 대해 크롤링하는 부분
latest = ''

option = '?max_id=95114544107626496'

done = False
while not done:
    data = crawlTweet('xguru',option)
    #상황에 따른 처리
    if data['status'] == '403':
        print '403',
        continue
    elif data['status'] == 'HTML error':
        print 'htmlerror'
        continue
    elif data['status'] == 'zero':
        break

    for tweet in data['crawlTweets']:
        print tweet['timestamp']
        if tweet['timestamp'] <= latest:
            done = True
            break

    if not data['nextId']:
        done = True
    
    if not done:
        option = "%s"%data['nextId']
        print option

    putTweet('xguru',data['crawlTweets'])

sys.exit()
#
num = 1
while 1:
    print "%d"%num,
    nowTweeter = getTweeter()
    data = crawlTweet(nowTweeter['twit_id'])
    if data :
        putTweet(nowTweeter['twit_id'],data)
    num += 1
    #time.sleep(2)

#break

#crawlTweet("tprpc")

#putTweet(getTweeter())

cursor.close()
db.close()


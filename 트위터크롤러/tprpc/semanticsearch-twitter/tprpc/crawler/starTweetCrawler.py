#!/usr/bin/python
#-*- encoding: utf-8 -*-

import httplib,urllib2
import sgmllib,string
import MySQLdb
import re,time,sys
import socket

#
# AllTweetCrawler 한사용자의 트윗을 가능한 모두 크롤링하는 크롤러 스크립트
#

version = "v0.08star"
error_cnt = 0 # 에러 카운트가 10 이상이면 종료 하는것으로..
workername = open('env').readline().replace("\n","") + version
print workername + "  crawler start!"


# 타임아웃 설정
timeout = 5
socket.setdefaulttimeout(timeout)


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
        raw = raw.replace("\\","\\\\").replace("'","\\'")
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
    try:
        query = "SELECT * FROM `tweeter_pool_star` WHERE `using` = '1' AND `latest_worker` = '%s' "%workername
        cursor.execute(query)
        data = cursor.fetchone()
        if data :
            return data
    
        # locking pool
        # 기존 lock 은 round robin 방식 
        query = "UPDATE `tweeter_pool_star` SET `using` = '1', `latest_worker` = '%s', `crawl_time` = NOW() WHERE `using` = '0' ORDER BY `crawl_time` ASC LIMIT 1 "%workername
        
        cursor.execute(query)
        db.commit()
    
        query = "SELECT * FROM `tweeter_pool_star` WHERE `using` = '1' AND `latest_worker` = '%s' "%workername
        cursor.execute(query)
        data = cursor.fetchone()

#print data['twit_id']
        return data
    except:
        return data


def poolUnlock(code=0):
    global workername,cursor,db 
    
    try:
        query = "UPDATE `tweeter_pool_star` SET `using` = '%d' WHERE `latest_worker` = '%s' AND `using` = '1'"%(code,workername)
        cursor.execute(query)
        db.commit()
    except:
        print "asdf"


# 사용자 상태 저장 
def putTwitterStatus(id,data,cnt):
    global cursor,db,workername
    #print data
    try:
        query = "INSERT INTO `twitter_user_status` (`twitid`, `fullname` ,`location` ,`bio` ,`url` ,`twitcnt`, `cnt`, `following`, `followers`) VALUES ('%s', '%s',  '%s',  '%s',  '%s', '%s', '%d', '%s', '%s')"%(id,data['fullname'], data['location'], data['bio'], data['url'], data['twitcnt'], cnt, data['following'], data['followers'])
        cursor.execute(query)
        db.commit()
    except:
        print "put Error"


def putTweet(id,data):
    global cursor,db,workername

    getrow = 0
    affectrow = 0
    
    for tweet in data:
        
        #print tweet['tweet']
        try:
            tweet['tweet'] = tweet['tweet'].replace("\\","\\\\").replace("'","\\'")

        #tweet['tweet'] = tweet['tweet'].replace("'","\\'")
            query = "INSERT INTO `tweet_data` (`twitid`, `username` ,`timestamp` ,`tweet` ,`worker` ,`update_time`) SELECT '%s', '%s',  '%s',  '%s',  '%s', CURRENT_TIMESTAMP FROM DUAL WHERE NOT EXISTS (SELECT * FROM `tweet_data` WHERE `twitid`='%s' AND `username`='%s' AND `timestamp` = '%s')"%(id, tweet['username'],tweet['timestamp'],tweet['tweet'],workername,id,tweet['username'],tweet['timestamp'])
            cursor.execute(query)
            db.commit()
            arow = cursor.rowcount
        except:
            arow = 0
        
        getrow += 1
        affectrow += arow
        
    print "%d...pushed!"%affectrow
    return affectrow

    # unlocking pool
    #print maxtimestamp
 
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
        #putLog('%s:crawlTweet'%id,'error',"HTTP error: %d" % e.code)
        if e.code == 403 :
            ret['status'] = '403'
            data = e.read()
            # print data
            # 계정에 문제가 있으면 삭제 대상(404)으로 반환한다.
            if data.find('Hold up!') != -1:
                ret['status'] = '404'

            #time.sleep(1) # 1초 쉰다!
        elif e.code == 404:
            ret['status'] = '404'
        elif e.code == 500:
            ret['status'] = '500' # 내부 서버 에러
        else :
            ret['status'] = 'HTML error'
        return ret
    except urllib2.URLError, e:
        print "Network error: %s" % e.reason
        putLog('%s:crawlTweet'%id,'error',"Network error: %s" % e.reason)
        ret['status'] = 'fatal error'
        return ret
    except KeyboardInterrupt, SystemExit:
        print '사용자 종료'
        sys.exit()    
    except:
        ret['status'] = 'fatal error'
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
    twitterStatus = {}

    #트위터 기본정보
    token = 'class="fullname">'
    data = data[data.find(token)+len(token):]
    twitterStatus['fullname'] = data[:data.find('\n')]
   
    token = 'class="location">'
    data = data[data.find(token)+len(token):]
    twitterStatus['location'] = data[:data.find('</div>')]
    
    token = 'class="bio">'
    data = data[data.find(token)+len(token):]
    twitterStatus['bio'] = data[:data.find('</div>')]
    
    token = 'class="url">'
    data = data[data.find(token)+len(token):]
    twitterStatus['url'] = data[:data.find('</div>')]

    # 트윗수 
    token = 'class="statnum">'
    data = data[data.find(token)+len(token):]
    twitterStatus['twitcnt'] = data[:data.find('</div>')].replace(",","")

    # 팔로잉수
    token = 'class="statnum">'
    data = data[data.find(token)+len(token):]
    twitterStatus['following'] = data[:data.find('</div>')].replace(",","")

    # 팔로워수
    token = 'class="statnum">'
    data = data[data.find(token)+len(token):]
    twitterStatus['followers'] = data[:data.find('</div>')].replace(",","")

    #트위터 본문 긁기
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
    ret['userinfo'] = twitterStatus
    ret['crawlTweets'] = crawlTweets
    ret['crawlTweetCnt'] = tweetCnt
    ret['nextId'] = maxId
    return ret

#도입부

num = 1
while 1:
    print "%d"%num,
    nowTweeter = getTweeter()

    twitId = nowTweeter['twit_id']
    if not twitId:
        continue

    #한 사용자에 대해 크롤링하는 부분
    latest = nowTweeter['latest_time'] # 얼만큼 까지 받는것인지 정한다.
    option = ''
    done = False
    first = True
    unlockCode = 0
    maxTimestamp = 0
    cntUpdate = 0

    while not done:
        data = crawlTweet(twitId,option)

        #상황에 따른 처리
        if data['status'] == '403':
            print '403',
#time.sleep(10)
            continue
        elif data['status'] == 'HTML error':
            print 'htmlerror'
            continue
        elif data['status'] == 'zero':
            break
        elif data['status'] == '500':
            break
        elif data['status'] == '404':
            unlockCode = 4
            break
        elif data['status'] == 'fatal error':
            print 'fatal error'
            continue

        if first:
            nowTweeter['userinfo'] = data['userinfo']
            first = False


        # 시간 체크
        for tweet in data['crawlTweets']:
            maxTimestamp = max(long(maxTimestamp), long(tweet['timestamp']))
            maxTemp = max(long(latest),long(tweet['timestamp']))
            # print maxTimestamp, tweet['timestamp'], latest, maxTemp
            if latest == maxTemp:
                print "check!!!"
                done = True
                break
    
        if not data['nextId']:
            done = True
        
        if not done:
            option = "%s"%data['nextId']
            print option
    
        cnt = putTweet(twitId,data['crawlTweets'])
        cntUpdate += cnt
        

        # 처음이 아닌데 중복이 전부면 
        #if cnt == 0 and latest != 0:
        #    done = True 

    num+=1

    # 사용자 정보 저장
    if not first :
        putTwitterStatus(twitId,nowTweeter['userinfo'],cntUpdate)

    # 다음 크롤 시각 정하기
    
    try:
        nextWeight = nowTweeter['weight'] * 0.5 + cntUpdate
        print nextWeight
        if nextWeight == 0:
            nextTime = 50
        else:
            nextTime = (int)(50 / nextWeight) + 1

        query = "UPDATE `tweeter_pool_star` SET `latest_time` = '%d', `weight` = '%f', `nCrawl_time` = DATE_ADD(now(), INTERVAL +%d hour) WHERE `twit_id` = '%s'"%(maxTimestamp, nextWeight, nextTime ,twitId)
        print query
        cursor.execute(query)
        db.commit()
    except:
        print 'update error'

   
    poolUnlock(unlockCode)

#
#num = 1
#while 1:
#    print "%d"%num,
#    nowTweeter = getTweeter()
#    data = crawlTweet(nowTweeter['twit_id'])
#    if data :
#        putTweet(nowTweeter['twit_id'],data)
#    num += 1
#    #time.sleep(2)

#break

#crawlTweet("tprpc")

#putTweet(getTweeter())

cursor.close()
db.close()


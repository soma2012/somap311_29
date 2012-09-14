#!/usr/bin/python
# coding=utf-8
import httplib,urllib2
import sgmllib,string
import MySQLdb
import re,time

error_cnt = 0 # 에러 카운트가 10 이상이면 종료 하는것으로..
workername = 'test'
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

    action = action.replace("'","\\'")
    resultcode = resultcode.replace("'","\\'")
    #raw = re.escape(raw.decode('UTF-8'))
    raw = raw.replace("'","\\'") #.encode('UTF-8')
    #print raw
    cursor.execute("INSERT INTO `log` (`id`,`worker`,`action`,`result_code`,`time`,`raw`) VALUES (NULL, '%s', '%s', '%s', CURRENT_TIMESTAMP, '%s')"%(workername, action, resultcode, raw))
    db.commit()

# 트위터 아이디 가져오기 
def getTweeter():
    global cursor,db,workername
    
    cursor.execute("SELECT * FROM `tweeter_pool` WHERE `using` = '1' AND `latest_worker` = '%s' "%workername)
    data = cursor.fetchone()
    if data :
        return data['twit_id']

    # locking pool
    cursor.execute("UPDATE `tweeter_pool` SET `using` = '1', `latest_worker` = '%s', `crawl_time` = NOW() WHERE `using` = '0' ORDER BY `crawl_time` ASC LIMIT 1 "%workername)
    db.commit()

    cursor.execute("SELECT * FROM `tweeter_pool` WHERE `using` = '1' AND `latest_worker` = '%s' "%workername)
    data = cursor.fetchone()

#print data['twit_id']
    return data['twit_id']



def putTweet(id,data):
    global cursor,db,workername

    getrow = 0
    affectrow = 0
    maxtimestamp = 0
    for tweet in data:
        maxtimestamp = max(maxtimestamp, tweet['timestamp'])
        tweet['tweet'] = re.escape(tweet['tweet'])
        
        #tweet['tweet'] = tweet['tweet'].replace("'","\\'")
        try:
            cursor.execute("INSERT INTO  `tweet_data` (`username` ,`timestamp` ,`tweet` ,`worker` ,`update_time`) SELECT '%s',  '%s',  '%s',  '%s', CURRENT_TIMESTAMP FROM DUAL WHERE NOT EXISTS (SELECT * FROM `tweet_data` WHERE `username`='%s' AND `timestamp` = '%s')"%(tweet['username'],tweet['timestamp'],tweet['tweet'],workername,tweet['username'],tweet['timestamp']) )
        except:
            print tweet['tweet']
            putLog('putTweet','tweetErr',tweet['tweet'])
        getrow += 1
        affectrow += cursor.rowcount
        
    print "%d...pushed!"%affectrow

    # unlocking pool
    #print maxtimestamp
    cursor.execute("UPDATE `tweeter_pool` SET `using` = '0', `latest_time` = '%s'  WHERE `latest_worker` = '%s' AND `using` = '1'"%(maxtimestamp,workername))
    db.commit()

    putLog('%s:putTweet'%id,'crawlok',"%d - %d...pushed!"%(getrow, affectrow))

def errorUnlock(code=2):
    global workername
    cursor.execute("UPDATE `tweeter_pool` SET `using` = '%d' WHERE `latest_worker` = '%s' AND `using` = '1'"%(code,workername))
    db.commit()



# 해당 아이디 크롤 진입점
# http://mobile.twitter.com/{$id}
#conn = httplib.HTTPConnection("mobile.twitter.com")
def crawlTweet(id = "xguru"):
    print id+'...',
    try:
        #기존코드에 버그가 있는거 같아서 사용안함
        #conn.request("GET", "/%s"%id, "", headers)
        #response = conn.getresponse()
        #data = response.read()
        data = urllib2.urlopen("http://mobile.twitter.com/%s" % id).read()
    except urllib2.HTTPError, e:
        print "HTTP error: %d" % e.code
        putLog('%s:crawlTweet'%id,'error',"HTTP error: %d" % e.code)
        if e.code == 403 :
            errorUnlock(0)
            time.sleep(60)
        elif e.code == 404:
            errorUnlock(4)
        else :
            errorUnlock()
        return

    except urllib2.URLError, e:
        print "Network error: %s" % e.reason.args[1]
        putLog('%s:crawlTweet'%id,'error',"Network error: %s" % e.reason.args[1])
        errorUnlock()
        return

    #conn.close()
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
            timestamp = tweetData[:tweetData.find('"'):]
            #print timestamp

            token = 'class="tweet-text">'
            tweetData = tweetData[tweetData.find(token)+len(token):]
            rawTweet = tweetData[:tweetData.find('</div>'):]
            #print rawTweet
            tweet = stripTag(rawTweet)
            #print tweet

            crawlTweets.append({'username' : username , 'timestamp' : timestamp, 'tweet' : tweet})


        else:
            print "%d..read!"%tweetCnt,
            break

    if tweetCnt == 0:
        putLog('%s:crawlTweet'%id,'tweetCnt=0',originaldata)
        errorUnlock()

    #print crawlTweets
    return crawlTweets

#도입부

num = 1
while 1:
    print "%d"%num,
    nowid = getTweeter()
    data = crawlTweet(nowid)
    if data :
        putTweet(nowid,data)
    num += 1
    time.sleep(2)

#break

#crawlTweet("tprpc")

#putTweet(getTweeter())

cursor.close()
db.close()


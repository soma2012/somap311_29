# coding=utf-8
import re
import xmlrpclib
import codecs
from svmlight import SVMLight
import rpcutil
from jsonrpc.proxy import JSONRPCProxy
import MySQLdb

server = xmlrpclib.ServerProxy("http://61.43.139.70:9003")

cls = ("animation", "baseball", "basketball", "book", "car", "childcare", "commercial", "economy", "entertainment",
       "fashion", "food", "game", "health", "infotech", "love", "movie", "pet", "politics", "science", "soccer","sports", "travel", "volleyball", "world")

subs = ("p","c")

def read_dic(sub):

    arr=[]
    for c in cls:
        file = "/home/xorox90/tp/polar/%s_%s"%(sub,c)
        #os.path.exists(file)
        fp = codecs.open(file, "r", encoding="utf-8")

        ret = fp.read()
        ret = re.sub(u"[^\s\u3040-\u309F\u30A0-\u30FF\u31F0-\u31FF0-9A-Za-z가-힣.]", " ", ret)
        ret = re.sub("(\s)+", r"\1", ret)
        for x in ret.split("\n"):
            arr.append(x)

    return arr


def make_dic(subs):
    global server
    dic = codecs.open("/home/xorox90/polar_dic", "w+", encoding="utf-8")
    s = set()

    for sub in subs:
        for line in read_dic(sub):
            line = line[line.find(' ')+1:]
            line = server.BuzzniTagger.segmentRpc(line)
            line = line.strip()
            for word in re.split("\s", line):
                s.add(word)

    for word in s:
        dic.write(word + " ")



def load_dic():
    dic = {}
    fp = codecs.open("/home/xorox90/polar_dic","r", encoding="utf-8")

    index=1
    for word in fp.read().split():
        dic[word]=index
        dic[index]=word
        index+=1


    return dic

def apply_dic(dic, str):
    #server = xmlrpclib.ServerProxy("http://61.43.139.70:9002")
    global server
    str = server.BuzzniTagger.segmentRpc(str)
    l = {}
    index=1
    for word in re.split("\s", str):
        if(dic.has_key(word)):
            l[dic[word]]=1
        index+=1

    return l;

def classify_init():
    make_dic(subs)
    dic = load_dic()
    print "end dic"
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

    print "svm start"
    svm = SVMLight("/home/xorox90/svm", labels=y, vectors=x)
    print "END!"


def classify(str):
    global dic
    global subs
    svm = SVMLight("/home/xorox90/svm", model="polar", cleanup=True)
    x = []
    x.append(apply_dic(dic,str))

    return subs[svm.classify(vectors=x)[0]-1]

def test():
    con = MySQLdb.connect(db='twit_manager', host="61.43.139.70",user='twit', passwd='1rmdwjd', charset="UTF8")
    cur = con.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    cur.execute("select * from tweet_data order by no desc limit 10000")

    qq2 = JSONRPCProxy("http://61.43.139.70:11001")
    for tt in cur.fetchall():
        print qq2.opn_classify(tt['tweet'])
        print tt['tweet']


#classify_init()
test()
exit(0)

svm = SVMLight("/home/xorox90/svm", model="polar_model", cleanup=True)
ans = []
gold = []
x = []
index =1

qq = JSONRPCProxy("http://61.43.139.70:8000")
qq2 = JSONRPCProxy("http://office2.buzzni.com:10100")

con = MySQLdb.connect(db='twit_manager', host="61.43.139.70",user='twit', passwd='1rmdwjd', charset="UTF8")
cur = con.cursor(cursorclass=MySQLdb.cursors.DictCursor)
cur.execute("select * from tweet_data order by no desc limit 10000")

arr = []
for tt in cur.fetchall():
    arr.append(tt['tweet'])

print len(arr)

dic = load_dic()
for line in arr:
    x.append(apply_dic(dic, line))
    polarity = qq2.opn_classify(line)
    if polarity==None or (polarity>2 and polarity <4):
        gold.append(0)
    elif(polarity<=2):
        gold.append(2)
    else:
        gold.append(1)

    index+=1


ans = svm.classify(vectors=x)

match=0
total=0
for i in range(0,len(ans)):

    if(ans[i]==gold[i]):
        match+=1
        total+=1
    elif(gold[i]!=0):
        total+=1
    else:
        print str(ans[i]) + " " + str(gold[i])

print "###############################"
print str(match) + " " + str(total)
print(match/(total/1.0))
exit(0)


exit(0)
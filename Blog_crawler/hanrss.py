# coding=utf-8
import requests
import feedparser
import difflib
import re
from datetime import timedelta
from datetime import date
from bs4 import BeautifulSoup, Comment
import psycopg2

##date parser => dateparser.parse
#print re.search("(.*?)/NNG[ +]", "나/NP+는/JX 학교/NNG+에/JKB 갈/VV+서/EC 맛있/VA+는/ETM 밥/NNG+을/JKO 맛있/VA+게/EC 먹/VV+었/EP+다/EF ./SF").group(1)

#for  a in re.finditer("(.*?)/NNG[ +]", "나/NP+는/JX 학교/NNG+에/JKB 갈/VV+서/EC 맛있/VA+는/ETM 밥/NNG+을/JKO 맛있/VA+게/EC 먹/VV+었/EP+다/EF ./SF"):
#    print a.group(1)

exit(0)

def get_url(url):
    return requests.get(url).text.encode("utf-8")

def flatten(dom):
    #comment erase
    comments = dom.find_all(text=lambda text:isinstance(text, Comment))
    [comment.extract() for comment in comments]

    #script decompose
    [s.decompose() for s in dom('script')]

    for s in dom('img'):
        if(s.get('src') and (s['src'].startswith("http") or  s['src'].startswith("/"))):
            s.replace_with(" " + s['src'] + " ")

    for s in article('a'):
        if(s.get('href') and (s['href'].startswith("http") or  s['href'].startswith("/"))):
            s.replace_with(" " + s['href'] + " ")

    for s in article('br'):
        s.replace_with("\n")

    return dom


def get_tistory_rss_list():
    s= set('')
    start_date = date.today() - timedelta(1)


    fp = open('ts',"w+")
    for i in (start_date - timedelta(n) for n in range(500)):

        req=requests.get('http://www.tistory.com/best/'+ i.strftime("%Y%m%d") + '?_best_tistory').text.encode("utf-8")
        for url in re.findall(r"<a.*?href=\"(http://[^\"]*?)/[^\"]*?\?_best_tistory=(trackback|reply)_bestpost\".*?>", req, re.I | re.M | re.S):
            s.add(url[0])



        print i.strftime("%Y%m%d")
        print s.__len__()

    for url in s:
        fp.write(url + "\n")


###general_parser not implemented yet..
def general_parser():

    f = open("url", "r")

    urls = f.readlines()


    url = urls[2]
    res = requests.get(url)
    feed = feedparser.parse(res.text.encode("utf-8"))


    #for entry in feed.entries:
    #    print entry.link

    doc=feed.entries[0].link
    doc2=feed.entries[1].link

    #print doc
    #print doc2


    #preprocess(requests.get(doc).text.encode("utf-8"))
    #exit(0)
    doc = BeautifulSoup(get_url(doc))
    doc2 = BeautifulSoup(get_url(doc2))


    diff = ''
    for line in difflib.context_diff(doc,doc2):
        print line
        print "#################################"

    exit(0)
    print diff

    for chunk in re.findall(r"\*\*\* \d+,\d+ \*\*\*\*(.*?)--- \d+,\d+ ----(.*?)\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*", diff, re.I|re.M|re.S):
        if re.search("<div.*?class=.*?(content|article|post).*?>", chunk[0], re.I|re.M|re.S):
            print stripIt(chunk[0])
            print "#################################"
            print stripIt(chunk[1])
            print "#################################"
        #else:
        #    print chunk[0]
        #    print "#################################"
        #    print chunk[1]

        #if re.search(r"<div.*?>", line,re.M|re.I|re.S) :



def update_tistory_rss():
    con = psycopg2.connect(dbname='postgres', host="61.43.139.70",port=5432, user='postgres', password='postgres')
    cur = con.cursor()

    fp = open('ts', "r+")
    for r in fp.readlines():
        #print r[:-1]
        cur.execute("""insert into rss (rss_url, post_date, crawl_date, crawl_id, type) values ('%s',0,0,0,1);""" % (r[:-1] + '/rss'))

    con.commit()
    con.close()

#get_tistory_rss_list()
#update_tistory_rss()
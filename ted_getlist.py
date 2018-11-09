#!/usr/bin/python
# -*- coding: utf-8 -*-


import json
import re
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

import pandas

from retry import retry

filename = "data.csv"


@retry(urllib.error.URLError, tries=6, delay=2, backoff=1.5, logger=None)
def urlopen_with_retry(link):
    return urllib.request.urlopen(link)


class TEDTalkHTMLParser(HTMLParser):
    
    def __init__(self, df):
        HTMLParser.__init__(self)
        self.df = df
    
    def process(self):
        try:
            self.df.ix[len(self.df)-1,'video'] = "https://hls.ted.com/talks/" + self.id + ".m3u8"
            
            # get transcript
            link_tx = "https://www.ted.com/talks/" + self.id + "/transcript.json?language=en"
            sock = urlopen_with_retry(link_tx)
            encoding = sock.headers.get_content_charset()
            page = sock.read().decode(encoding)
            self.df.ix[len(self.df)-1,'someNewHeader'] = "A string of some sort"
            # flatten paragraph into list of dicts
            # someNames = list
            # aSomeName = dict
            lst = []
            data = json.loads(page)
            paragraphs = data.get("paragraphs") 
            for aParagraph in paragraphs:
                cues = aParagraph.get("cues")
                for aCue in cues:
                    lst.append(aCue)
            self.df.ix[len(self.df)-1,'transcript'] = json.dumps(lst) 
            # self.df.ix[len(self.df)-1,'transcript'] = page
            sock.close()
        except:
            print("Caught Exception in Retry Function, probably from 404 Error, skipping...")
    
    def handle_starttag(self, tag, attrs):
        if tag == 'meta' and ('property', 'al:ios:url') in attrs:
            urltmp = re.split('/', attrs[1][1])[3]
            self.id = re.split('\?', urltmp)[0]
            self.process()


class TEDListHTMLParser(HTMLParser):
    def __init__(self, df):
        HTMLParser.__init__(self)
        self.state = 0
        self.df = df
    
    def process(self):
        link_talk = "http://www.ted.com" + self.name
        self.df.loc[len(self.df)] = None
        self.df.ix[len(self.df)-1, 'name'] = self.name.split("/")[2]
        self.df.ix[len(self.df)-1, 'speaker'] = self.speaker
        self.df.ix[len(self.df)-1, 'title'] = self.title
        self.df.ix[len(self.df)-1, 'year'] = self.year
        self.df.ix[len(self.df)-1, 'link'] = link_talk
        # parse talk
        print(link_talk)
        try:
            sock = urlopen_with_retry(link_talk)
            encoding = sock.headers.get_content_charset()
            page = sock.read().decode(encoding)
            sock.close()
            parser = TEDTalkHTMLParser(self.df)
            parser.feed(page)
        except:
            print("Caught Exception in Retry Function, probably from 404 Error, skipping...")

    def handle_starttag(self, tag, attrs):
        if self.state == 0 and tag == 'div' and ('class', 'media__message') in attrs:
            self.state = 1
        elif self.state == 1 and tag == 'h4' and attrs[0][1] == "h12 talk-link__speaker":
            self.state = 2
        elif self.state == 3 and tag == 'a':
            self.name = attrs[-1][1].rstrip()
            self.state = 4
        elif self.state == 5 and tag == 'span' and attrs[0][1] == "meta__val":
            self.state = 6

    def handle_endtag(self, tag):
        pass
    
    def handle_data(self, data):
        if self.state == 2 and data.rstrip():
            self.speaker = data.rstrip()
            self.state = 3
        elif self.state == 4 and data.rstrip():
            if len(data.rstrip().split("\n"))>1:
                self.title = data.rstrip().split("\n")[1]
            else:
                self.title = data.rstrip()
            self.state = 5
        elif self.state == 6 and data.rstrip():
            self.year = data.rstrip().split("\n")[1]
            self.state = 0
            self.process()


df = pandas.read_csv(filename)

for i in range(1, 81, 1): # Go through all pages
    print("--- page %g ---" % i) 
    link = "http://www.ted.com/talks?page=" + str(i)
    try:
        sock = urlopen_with_retry(link)
        encoding = sock.headers.get_content_charset()
        page = sock.read().decode(encoding)
        sock.close()
        parser = TEDListHTMLParser(df)
        parser.feed(page)
    except:
        print("Caught Exception in Retry Function, probably from 404 Error, skipping...")

    df.to_csv(filename, index=False, encoding='utf-8')

#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from subprocess import call
import numpy
import pandas
import os.path
import urllib2
import requests
import re
import time
from retry import retry
from HTMLParser import HTMLParser

filename = "data.csv"

@retry(urllib2.URLError, tries=100, delay=3, backoff=2)
def urlopen_with_retry(link):
    return urllib2.urlopen(link)

class TEDTalkHTMLParser(HTMLParser):
    
    def __init__(self, df):
        HTMLParser.__init__(self)
        self.df = df
    
    def process(self):
        self.df.ix[len(self.df)-1,'video'] = "https://hls.ted.com/talks/" + self.id + ".m3u8"
        
        # get transcript
        link_tx = "https://www.ted.com/talks/" + self.id + "/transcript.json?language=en"
        sock = urlopen_with_retry(link_tx)
        encoding = sock.headers.getparam('charset')
        page = sock.read().decode(encoding)
        
        self.df.ix[len(self.df)-1,'transcript'] = page
        sock.close()
    
    def handle_starttag(self, tag, attrs):
        if tag == 'meta' and (u'property', u'al:ios:url') in attrs:
            urltmp = re.split('/', attrs[1][1])[3]
            self.id = re.split('\?', urltmp)[0]
            self.process()


class TEDListHTMLParser(HTMLParser):
    def __init__(self,df):
        HTMLParser.__init__(self)
        self.state = 0
        self.df = df
    
    def process(self):
        link_talk = "http://www.ted.com" + self.name
        self.df.loc[len(self.df)] = None
        self.df.ix[len(self.df)-1,'name'] = self.name.split("/")[2]
        self.df.ix[len(self.df)-1,'speaker'] = self.speaker
        self.df.ix[len(self.df)-1,'title'] = self.title
        self.df.ix[len(self.df)-1,'year'] = self.year
        self.df.ix[len(self.df)-1,'link'] = link_talk
        # parse talk
        print(link_talk)
        sock = urlopen_with_retry(link_talk)
        encoding = sock.headers.getparam('charset')
        page = sock.read().decode(encoding)
        sock.close()
        parser = TEDTalkHTMLParser(self.df)
        parser.feed(page)

    def handle_starttag(self, tag, attrs):
        if self.state==0 and tag == 'div' and ('class','media__message') in attrs:
            self.state=1;
        elif self.state==1 and tag == 'h4' and attrs[0][1]=="h12 talk-link__speaker":
            self.state = 2;
        elif self.state==3 and tag == 'a':
            self.name = attrs[-1][1].rstrip()
            self.state = 4;
        elif self.state == 5 and tag == 'span' and attrs[0][1]=="meta__val":
            self.state = 6;

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

for i in range(1,75,1): # Go through all pages
    print ("--- page %g ---" % i) 
    link = "http://www.ted.com/talks?page=" + str(i)
    sock = urlopen_with_retry(link)
    encoding = sock.headers.getparam('charset')
    page = sock.read().decode(encoding)
    sock.close()
    parser = TEDListHTMLParser(df)
    parser.feed(page)

    df.to_csv(filename, index=False, encoding='utf-8')

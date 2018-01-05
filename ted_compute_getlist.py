#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from subprocess import call
import numpy
import pandas
import os.path
import urllib
import requests
import re
import time
from HTMLParser import HTMLParser

filename = "ted_data.csv"

class TEDTranscriptHTMLParser(HTMLParser):
    
    def __init__(self, df):
        HTMLParser.__init__(self)
        self.state = 0
        self.xtext = []
        self.df = df
    
    def process(self):
        self.df.ix[len(self.df)-1,'transcript'] = self.xtext.replace("\"", "")
        
    def handle_starttag(self, tag, attrs):
        print (attrs)
        # TODO: The site software has been recently updated to include interactive transcript.
        # This requires parser modification to get the full text of the talk.
        if self.state==0 and tag == 'span' and ('class','talk-transcript__fragment') in attrs:
            self.state=1

    def handle_endtag(self, tag):
        if tag == "html":
            self.xtext = " ".join(self.xtext)
            self.process();

    def handle_data(self, data):
        if self.state == 1:
            self.xtext.append(data.strip().rstrip().replace("\n", " "))
            self.state = 0
    

class TEDTalkHTMLParser(HTMLParser):
    
    def __init__(self, df):
        HTMLParser.__init__(self)
        self.state = 0
        self.topics = []
        self.topic_urls = []
        self.df = df
    
    def process(self):
        self.df.ix[len(self.df)-1,'video'] = self.video
        self.df.ix[len(self.df)-1,'topics'] = ";".join(self.topics)
        self.df.ix[len(self.df)-1,'topic_urls'] = ";".join(self.topic_urls)
        self.topics = []
        self.topic_urls = []
    
    def handle_starttag(self, tag, attrs):
        if self.state==0 and tag == 'ul' and ('class','talk-topics__list') in attrs:
            self.state = 1
        elif self.state==1 and tag == 'a' and ('class','l3 talk-topics__link ga-link') in attrs:
            sl = [v for (k,v) in attrs if k == 'href']
            self.topic_urls.append(sl[0])
            self.state=2
        if self.state==3 and tag == 'script':
            self.state=4

    def handle_endtag(self, tag):
        if self.state == 1 and tag == "ul":
            self.state = 3

    def handle_data(self, data):
        if self.state == 2:
            self.topics.append(data.rstrip().split("\n")[1])
            self.state=1
        elif self.state == 4:
            code = data.rstrip()
            result = re.search(r'"low":"(\S+)\?(\S+)","medium',code)
            if result:
                self.video = result.group(1)
                self.process();
                self.state = 5

class TEDListHTMLParser(HTMLParser):
    
    def __init__(self,df):
        HTMLParser.__init__(self)
        self.state = 0
        self.df = df
    
    def process(self):
        link_talk = "http://www.ted.com" + self.name
        self.df.loc[len(self.df)] = None
        print ("Talk title: %s" % link_talk)
        self.df.ix[len(self.df)-1,'name'] = self.name.split("/")[2]
        self.df.ix[len(self.df)-1,'speaker'] = self.speaker
        self.df.ix[len(self.df)-1,'title'] = self.title
        self.df.ix[len(self.df)-1,'views'] = self.views
        self.df.ix[len(self.df)-1,'year'] = self.year
        self.df.ix[len(self.df)-1,'link'] = link_talk
        # parse talk
        sock = urllib.urlopen(link_talk)
        encoding = sock.headers.getparam('charset')
        page = sock.read().decode(encoding)
        sock.close()
        parser = TEDTalkHTMLParser(self.df)
        parser.feed(page)
        # parse transcript
        link_tx = "http://www.ted.com" + self.name + "/transcript?language=en"
        sock = urllib.urlopen(link_tx)
        encoding = sock.headers.getparam('charset')
        page = sock.read().decode(encoding)
        sock.close()
        parser = TEDTranscriptHTMLParser(self.df)
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
        elif self.state == 7 and tag == 'span' and attrs[0][1]=="meta__val":
            self.state = 8;

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
            self.views = data.rstrip().split("\n")[1]
            self.state = 7
        elif self.state == 8 and data.rstrip():
            self.year = data.rstrip().split("\n")[1]
            self.state = 0          
            self.process()


df = pandas.read_csv(filename)

for i in range(1,74,1): # Go through all pages
    print ("--- page %g ---" % i) 
    link = "http://www.ted.com/talks?page=" + str(i)
    sock = urllib.urlopen(link)
    encoding = sock.headers.getparam('charset')
    page = sock.read().decode(encoding)
    sock.close()
    parser = TEDListHTMLParser(df)
    parser.feed(page)

    df.to_csv(filename, index=False, encoding='utf-8')
    time.sleep(2)

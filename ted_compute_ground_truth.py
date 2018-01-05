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
from HTMLParser import HTMLParser

filename = "ted_data.csv"

class WCIParser(HTMLParser):
    def __init__(self, df, i):
        HTMLParser.__init__(self)
        self.state = 0
        self.df = df
        self.i = i
    def handle_starttag(self, tag, attrs):
        if self.state == 0 and tag=="div" and ('class','quote2') in attrs:
            self.state = 1
    def handle_endtag(self, tag):
        pass
    def handle_data(self, data):
        if self.state == 1:
            self.syllables = data.rstrip().replace(",","")
            self.state = 2
        elif self.state == 2 and data.rstrip() == "Sentences":
            self.state = 3
        elif self.state == 3:
            self.sentences = data.rstrip()
            self.state = 4
        elif self.state == 4 and data.rstrip() == "Total Words":
            self.state = 5
        elif self.state == 5:
            self.words = data.rstrip()
            self.state = 6
    def get_counters(self):
        return [self.syllables, self.words, self.sentences]
            

class WCCParser(HTMLParser):
    def __init__(self, df, i):
        HTMLParser.__init__(self)
        self.state = 0
        self.df = df
        self.i = i
    def handle_starttag(self, tag, attrs):
        if self.state == 1 and tag=="td":
            self.state = 2
        elif self.state == 4 and tag=="td":
            self.state = 5
        elif self.state == 7 and tag=="td":
            self.state = 8
    def handle_endtag(self, tag):
        if tag == "html":
            if not hasattr(self, 'sentences'):
                self.sentences = self.words = self.syllables = "0";
            self.df.ix[self.i,'wcc_sentence_count'] = self.sentences.replace(',',"")
            self.df.ix[self.i,'wcc_word_count'] = self.words.replace(',',"")
            self.df.ix[self.i,'wcc_syllable_count'] = self.syllables.replace(',',"")            
    def handle_data(self, data):
        if self.state == 0 and data=="Sentence Count":
            self.state = 1
        elif self.state == 2:
            self.sentences = data.rstrip()
            self.state = 3
        elif self.state == 3 and data=="Word Count":
            self.state = 4
        elif self.state == 5:
            self.words = data.rstrip()
            self.state = 6
        elif self.state == 6 and data=="Syllable Count":
            self.state = 7
        elif self.state == 8:
            self.syllables = data.rstrip()
            self.state = 9
    
class SCNParser(HTMLParser):
    def __init__(self, df, i):
        HTMLParser.__init__(self)
        self.state = 0
        self.df = df
        self.i = i
    def handle_starttag(self, tag, attrs):
        if self.state == 0 and tag=="span" and ('class','muted') in attrs:
            self.state = 1
        elif self.state == 1 and tag=="span":
            self.state = 2
    def handle_endtag(self, tag):
        pass
    def handle_data(self, data):
        if self.state == 2:
            self.df.ix[self.i,'scn_syllable_count'] = data.rstrip()            
            self.state = 3
            



df = pandas.read_csv(filename)

#===============================================================================
# counts for music, video, laughter, applause
#===============================================================================
#df = df.dropna()
for i,e in df.iterrows():
    print (e['transcript'])
    text = e['transcript'].decode('utf_8')
    df.ix[i,'applause_count'] = text.count("(Applause)")
    df.ix[i,'music_count'] = text.count("(Music)")  +  text.count("(Video)") + text.count(u"♫") + text.count(u"♪")
    df.ix[i,'laughter_count'] = text.count("(Laughter)")
    df.ix[i,'transcript'] = text.replace("(Applause)","").replace("(Laughter)","")
  
df.to_csv(filename, index=False, encoding='utf-8')

#===============================================================================
# www.wordcalc.com -- WCC
#===============================================================================
for i,e in df.iterrows():
#     if not numpy.isnan(e['wcc_syllable_count']):
#         continue
    
    url = "http://www.wordcalc.com/index.php"
    options = {
            "text": e['transcript'],
            "optionWordCount": True,
            "optionSyllableCount": True,
            "optionAnalyzeParagraphs": True,
            "optionAnalyzeSentences": True,
            }
    r = requests.post(url, data=options)
    print (r)
    parser = WCCParser(df, i)
    parser.feed(r.text)
     
df.to_csv(filename, index=False, encoding='utf-8')

#===========================================================================
# http://syllablecounter.net -- SCN
#===========================================================================
for i,e in df.iterrows():
#     if not numpy.isnan(e['scn_syllable_count']):
#         continue
  
    url = "http://syllablecounter.net/count"
    options = {
           "words": e['transcript'],
           }
    r = requests.post(url, data=options)
    print (r)
    parser = SCNParser(df, i)
    parser.feed(r.text)
   
df.to_csv(filename, index=False, encoding='utf-8')

#===========================================================================
# http://countwordsworth.com/syllablespersentence -- CWW
#===========================================================================
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import re
import time
     
# starting headless browser (browser automation)
os.environ["SELENIUM_SERVER_JAR"] = "selenium-server-standalone-2.41.0.jar"
driver = webdriver.Safari()
driver.implicitly_wait(60)
driver.get("http://countwordsworth.com/syllablespersentence")
elem = driver.find_element_by_id("page")
     
for i,e in df.iterrows():
#     if not numpy.isnan(e['cww_syllable_count']):
#         continue
    
    driver.execute_script("document.getElementById('page').value =\"" + \
                           e['transcript'].decode('utf-8').replace("\"","") + \
                           "\"; $('page').keyup();");
    elem.send_keys(Keys.UP)
    time.sleep(5)
         
    syllable_count = driver.find_element_by_class_name("syllables-count")
    word_count = driver.find_element_by_class_name("word-count")
    sentence_count = driver.find_element_by_class_name("sentence-count")
    preposition_count = driver.find_element_by_class_name("preposition-count")
    article_count = driver.find_element_by_class_name("article-count")
    pause_count = driver.find_element_by_class_name("pause-count")
         
    ee = driver.find_element_by_id("readability-container")
    print(ee.text)
    a = re.split("\n",ee.text)[1:6]
    scores = [re.split(" ",aa)[-1] for aa in a]
         
    df.ix[i,'cww_syllable_count'] = syllable_count.text
    df.ix[i,'cww_word_count'] = word_count.text
    df.ix[i,'cww_sentence_count'] = sentence_count.text
    df.ix[i,'cww_preposition_count'] = preposition_count.text
    df.ix[i,'cww_article_count'] = article_count.text
    df.ix[i,'cww_pause_count'] = pause_count.text
             
    df.ix[i,'cww_flesch_reading_ease'] = scores[0]
    df.ix[i,'cww_flesch_kincaid_grade_level'] = scores[1]
    df.ix[i,'cww_dale_chall_formula'] = scores[2]
    df.ix[i,'cww_gunning_fog_index'] = scores[3]
    df.ix[i,'cww_forecast_grade_level'] = scores[4]
     
df.to_csv(filename, index=False, encoding='utf-8')
     
driver.close()


#===============================================================================
# http://www.wordscount.info/hw/syllable.jsp -- WCI
#===============================================================================
for i,e in df.iterrows():
#     if not numpy.isnan(e['wci_syllable_count']):
#         continue
           
    url = "http://wordscount.info/hw/service/syllable/analyze.jsp"
       
    l=e['transcript'].decode('utf-8').split(" ")
    p = []
    parts = []
    for j in range (len(l)):
        p.append(l[j])
        if j>0 and j % 1000 == 0:
            parts.append(" ".join(p))
            p = []
    parts.append(" ".join(p))
       
    syllables = 0; words = 0; sentences = 0;
    for p in parts:
        options = {
                "user_text": p,
                }
        r = requests.post(url, data=options)
        print (r)
        parser = WCIParser(df, i)
        parser.feed(r.text)
        [sy, w, se] = parser.get_counters()
        syllables += float(sy); words += float(w); sentences += float(se);
           
    df.ix[i,'wci_sentence_count'] = sentences
    df.ix[i,'wci_word_count'] = words
    df.ix[i,'wci_syllable_count'] = syllables
   
    df.to_csv(filename, index=False, encoding='utf-8')

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
import os
import time

filename = "data.csv"

df = pandas.read_csv(filename, encoding='utf-8')
df = df.dropna()

#===============================================================================
# filter out music, video, laughter, applause, etc.
#===============================================================================
for i,e in df.iterrows():
    text = e['transcript'].decode('utf_8')
    df.ix[i,'applause_count'] = text.count("(Applause)")                        
    df.ix[i,'music_count'] = text.count("Music)")  +  \
        text.count("Video)") + text.count(u"♫") + text.count(u"♪") + \
        text.count("oise)") + text.count("oises)") + text.count("music)") + text.count("violin)") + \
        text.count(" CA:") + text.count("ang)") + text.count("aughs)") + text.count("Whoosh)") + \
        text.count("(In Dutch)") + text.count("CC: A-rhythm") + text.count("Tone") + \
        text.count("(Cheers)") + text.count("(Dinosaur roaring)") + text.count("(Musical chords)") + \
        text.count(" MB:") + text.count(" MR:") + text.count("(Audience:") + text.count(" MTT:")
    df.ix[i,'laughter_count'] = text.count("(Laughter)")
    df.ix[i,'transcript'] = (text.replace("(Applause)","").replace("(Laughter)",""))
   
df = df[df.music_count == 0]
df = df[df.laughter_count <= 15]
df = df[df.applause_count <= 5]
# df = df[not numpy.isnan(df.transcript)]

df.to_csv(filename, index=False, encoding='utf-8')

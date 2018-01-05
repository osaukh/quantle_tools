#!/usr/bin/python

from subprocess import call
import numpy
import pandas
import os.path

import wave


filename = "data.csv"

df = pandas.read_csv(filename)

for i,e in df.iterrows():
    print "--- %g - %s ---" % (i, e['name'])
    
    # get video file and convert if necessary
    if not os.path.exists("ted/"+e['name']+".wav"):
        dlink = ["curl", "-L", e['video'], "-o", "ted/"+e['name']+".mp4"]
        print (dlink)
        call(dlink)
        call(["./ffmpeg", "-i", "ted/"+e['name']+".mp4", "-ar", 
              "44100", "-ac", "1", "-ab", "64k", "ted/"+e['name']+".wav"])
        call(["rm", "-f", "ted/"+e['name']+".mp4"])
        
        # read wave and cut TED intoduction and applause at the end
        wf =  wave.open("ted/"+e['name']+".wav", 'r')
        nchannels, sampwidth, rate, nframes, comptype, compname =  wf.getparams()
        data = wf.readframes(nframes*nchannels)
                
        # write single channel (why always the second one?)
        start_frame = 26*rate;
        end_frame = (nframes - 12*rate) * sampwidth
        frames = data[(start_frame*nchannels):(end_frame*nchannels)]
#         new_frames = ''        
#         for (s1, s2) in zip(frames[0::2],frames[1::2]):
#             new_frames += (hex(ord(s2)))[2:].zfill(4).decode('hex')
                
        ww = wave.open("ted/"+e['name']+".wav",'wb')
        ww.setparams((nchannels,sampwidth,rate,end_frame-start_frame+1,comptype,compname))    
        ww.writeframes(frames)
 
    # compute length if not yet known
    if not numpy.isnan(e['length']):
        continue
    wf =  wave.open("ted/"+e['name']+".wav", 'r')
    rate = wf.getframerate()
    data = wf.readframes(wf.getnframes())
    signal = numpy.array(wave.struct.unpack(b"%dh"%(len(data)/wf.getsampwidth()),data))
    df.ix[i,'length'] = len(signal[:])/float(rate)/60
    df.to_csv(filename, index=False)

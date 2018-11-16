#!/usr/bin/python
import json
import os.path
import re
import subprocess
import urllib

import pandas

filename = "data.csv"

df = pandas.read_csv(filename)

for i, e in df.iterrows():
    print("--- %g - %s ---" % (i, e['name']))
    
    # get video file and convert if necessary
    if not os.path.exists("ted/"+e['name']+".aac"):
        t1 = "tmp1.m3u"
        t2 = "tmp2.m3u"
        t3 = "ted/" + e['name'] + ".aac"
        urllib.request.urlretrieve(e['video'], t1)

        with open(t1, "r") as tmp1file:
            data1 = tmp1file.read()
            try:
                f1 = re.search('NAME="Audio"(.+?)BANDWIDTH', data1).group(0)
                found = re.search('/(.+?)"', f1).group(0)
                found = found[:-1]
                url = "https://hls.ted.com" + found
                urllib.request.urlretrieve(url, t2)
                with open(t2, "r") as tmp2file:
                    data2 = tmp2file.read()
                    f2 = re.findall('https.*aac', data2)
                    audioFile = f2[2]
            except AttributeError:
                # TODO clean error handling
                # not found in text
                audioFile = ''

        urllib.request.urlretrieve(audioFile, t3)

        # convert to wav
        # this sometimes repairs errors in aac data
        if not os.path.exists("ted\\"+e['name']):
            os.makedirs("ted\\"+e['name'])
        t4 = "ted\\" + e['name'] + "\\" + "tmp3.wav"
        print("Converting " + e['name'] + ".aac to .wav")
        subprocess.call(['ffmpeg', '-i', t3, t4], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # remove temp files
        try:
            os.remove(t1)
            os.remove(t2)
            os.remove(t3)
        except OSError:
            pass

        timeStamps = json.loads(e['transcript'])
        for j in range(len(timeStamps)):
            print("\tSplitting part " + str(j+1) + "/" + str(len(timeStamps)))
            if j == len(timeStamps)-1:
                # last element
                startTime = timeStamps[j].get('time') / 1000
                subFile = "ted\\" + e['name'] + "\\" + str(j) + ".wav"
                ret = subprocess.call(
                    ['ffmpeg', '-ss', str(startTime), '-i', t4, subFile]
                    , stdout=subprocess.DEVNULL
                    , stderr=subprocess.DEVNULL
                )
            else:
                # all other elements
                startTime = timeStamps[j].get('time') / 1000
                duration = (timeStamps[j + 1].get('time') / 1000) - startTime
                if (duration <= 10):
                    subFile = "ted\\" + e['name'] + "\\" + str(j) + ".wav"
                    ret = subprocess.call(
                        ['ffmpeg', '-ss', str(startTime), '-i', t4, '-t', str(duration), subFile]
                        , stdout=subprocess.DEVNULL
                        , stderr=subprocess.DEVNULL
                    )
                    # ret = 0 -> success
                    # ret = 1 -> fail
                    if ret:
                        print("Error when splitting file for " + str(j) + ".wav")
                else:
                    print("Subfile " +str(j) + " >10 seconds. Ignoring....")
        # cleanup
        try:
            os.remove(t4)
        except OSError:
            pass

#         # old code
#         call(["./ffmpeg", "-i", "ted/"+e['name']+".mp4", "-ar",
#               "44100", "-ac", "1", "-ab", "64k", "ted/"+e['name']+".wav"])
#         call(["rm", "-f", "ted/"+e['name']+".mp4"])
#
#         # read wave and cut TED intoduction and applause at the end
#         wf = wave.open("ted/"+e['name']+".wav", 'r')
#         nchannels, sampwidth, rate, nframes, comptype, compname = wf.getparams()
#         data = wf.readframes(nframes*nchannels)
#
#         # write single channel (why always the second one?)
#         start_frame = 26*rate
#         end_frame = (nframes - 12*rate) * sampwidth
#         frames = data[(start_frame*nchannels):(end_frame*nchannels)]
# #         new_frames = ''
# #         for (s1, s2) in zip(frames[0::2],frames[1::2]):
# #             new_frames += (hex(ord(s2)))[2:].zfill(4).decode('hex')
#
#         ww = wave.open("ted/"+e['name']+".wav",'wb')
#         ww.setparams((nchannels, sampwidth, rate, end_frame-start_frame+1, comptype, compname))
#         ww.writeframes(frames)
#
#     # compute length if not yet known
#     if not numpy.isnan(e['length']):
#         continue
#     wf = wave.open("ted/"+e['name']+".wav", 'r')
#     rate = wf.getframerate()
#     data = wf.readframes(wf.getnframes())
#     signal = numpy.array(wave.struct.unpack(b"%dh"%(len(data)/wf.getsampwidth()), data))
#     df.ix[i, 'length'] = len(signal[:])/float(rate)/60
#     df.to_csv(filename, index=False)



import json
import csv
import codecs
import re
from pprint import pprint


filename = "data - Copy.csv"
outputFolder = "Transcripts"
with open(filename) as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    #Skip the header
    next(readCSV, None)
    i = 0
    for row in csvfile:
        line = next(readCSV, None)
        oFileName = "transcript_" + line[2]
        oFileName = re.sub('[<>:"/\|?*.]', '', oFileName)
        oFileName += ".txt"
        transcript = line[8]
        bar = json.loads(transcript)
        lineStr = ""
        lineStr.encode('utf-8')

        numParagraphs = len(bar["paragraphs"])
        for paragraph in range(numParagraphs):
            numCues = len(bar["paragraphs"][paragraph]["cues"])
            for cue in range(numCues):
                foo = bar["paragraphs"][paragraph]["cues"][cue]["text"]
                foo.encode('utf-8')
                lineStr += foo
                lineStr += " "
        
        text_file = codecs.open(outputFolder + "\\" + oFileName, "w", "utf-8")
        text_file.write(lineStr)
        text_file.close()

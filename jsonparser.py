import json
import csv
from pprint import pprint

with open('data.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    next(readCSV, None)
    foo = next(readCSV, None)
    s = foo[8]
    bar = json.loads(s)
    pprint(bar)

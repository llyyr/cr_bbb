#!/usr/bin/env python3
from urllib.request import urlopen
import json
import string
import csv
import os


names = set()
for i in range(10000):
    if i % 100 == 0: print(i)
    try:
        r = urlopen('https://apiv2.cricket.com.au/web/views/scorecard?FixtureId=' + str(i) + '&jsconfig=eccn:true&format=json').read()
    except:
        continue
    r = json.loads(r)
    if 'fixture' in r:
        name = r['fixture']['competition']['name']
        if not ' v ' in name and not r['fixture']['competition']['isWomensCompetition']:
            names.add(name)
    print(names)


# https://github.com/bfemiano/big-data-code-examples/blob/master/Ch3/src/main/python/clean_acled_nigeria.py
# !/usr/bin/python
import sys

day = ''
month = ''
year = ''
for line in sys.stdin:
    (loc, event_date, year, event_type, actor, lat, lon, src, fatalities) = line.strip().split(
        '\t')
    if loc != 'LOCATION':  # remove header row
        (day, month, year) = event_date.split('/')
        if fatalities == 'ZERO_FLAG':
            fatalities = 'FLAG'
        if len(day) == 1:
            day = '0' + day
        if len(month) == 1:
            month = '0' + month
        if len(year) == 2:
            if int(year) > 30 and int(year) <= 99:
                year = '19' + year
            else:
                year = '20' + year
        if int(month) >= 13:
            temp = month
            month = day
            day = temp
        event_date = year + '-' + month + '-' + day
        print('\t'.join(
            [loc, event_date, event_type, actor, lat, lon, src, fatalities]))  # strip out year

#!/usr/bin/env python
"""
This is an example script to dump the fitbit data for the previous day.
This can be set up in a cronjob to dump data daily.

Create a config file at ~/.fitbit.conf with the following:

[fitbit]
user_id: 12XXX 
sid: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
uid: 123456
uis: XXX%3D
dump_dir: ~/Dropbox/fitbit
"""
import time
import os
import ConfigParser

import fitbit

CONFIG = ConfigParser.ConfigParser()
CONFIG.read(["fitbit.conf", os.path.expanduser("~/.fitbit.conf")])

DUMP_DIR=os.path.expanduser(CONFIG.get('fitbit', 'dump_dir'))

def client():
    return fitbit.Client(CONFIG.get('fitbit', 'user_id'), CONFIG.get('fitbit', 'sid'), CONFIG.get('fitbit', 'uid'), CONFIG.get('fitbit', 'uis'))

def dump_to_str(data):
    return "\n".join(["%s,%s" % (str(ts), v) for ts, v in data])

def dump_to_file(data_type, date, data):
    directory = "%s/%s" % (DUMP_DIR, data_type)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    with open("%s/%s.csv" % (directory, str(date)), "w") as f:
        f.write(dump_to_str(data))

def dump_day(date):
    c = client()

    dump_to_file("steps", date, c.intraday_steps(date))
    time.sleep(5)    
    dump_to_file("calories", date, c.intraday_calories_burned(date))
    time.sleep(5)
    dump_to_file("active_score", date, c.intraday_active_score(date))
    time.sleep(5)
    dump_to_file("sleep", date, c.intraday_sleep(date))
    time.sleep(5)

if __name__ == '__main__':
    #import logging
    #logging.basicConfig(level=logging.DEBUG)
    import datetime
    dump_day((datetime.datetime.now().date() - datetime.timedelta(days=1)))

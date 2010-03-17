#!/usr/bin/env python
"""
This is an example script to dump the fitbit data for the previous day into a sqlite database.
This can be set up in a cronjob to dump data daily.

Create a config file at ~/.fitbit.conf with the following:

[fitbit]
user_id: 12XXX
sid: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
uid: 123456
uis: XXX%3D
dump_dir: ~/Dropbox/fitbit
db_file: ~/data/nameofdbfile.sqlite

The database has a table for each of steps, calories, active_score, and sleep. There is also a table with extension _daily for each that contains accumulated data per day.

The timestamp in the table is a unix timestamp. Tables are set up so that the script can be run repeatedly for the same day. Newer data replaces older data for the same timestamp. This is so data can be caught up if the fitbit does not sync every day.
"""

from time import mktime, sleep
from datetime import datetime, timedelta
from os import path
import ConfigParser
import sqlite3

import fitbit

CONFIG = ConfigParser.ConfigParser()
CONFIG.read(["fitbit.conf", path.expanduser("~/.fitbit.conf")])

DB_FILE = path.expanduser(CONFIG.get('fitbit', 'db_file'))

def client():
	return fitbit.Client(CONFIG.get('fitbit', 'user_id'), CONFIG.get('fitbit', 'sid'), CONFIG.get('fitbit', 'uid'), CONFIG.get('fitbit', 'uis'))

def create_table(table, db):
	db.execute("create table %s (datetime integer PRIMARY KEY ON CONFLICT REPLACE, %s integer)" % (table, table))
	db.execute("create table %s_daily (date integer PRIMARY KEY ON CONFLICT REPLACE, %s integer)" % (table, table))

""" Connects to the DB, creates it if it doesn't exist. Returns the connection.
"""
def connect_db(filename):
	if path.isfile(filename):
		return sqlite3.connect(filename)
	else:
		db = sqlite3.connect(filename)
		create_table("steps", db)
		create_table("calories", db)
		create_table("active_score", db)
		create_table("sleep", db)
		return db

def dump_to_db(db, data_type, date, data):
	insertString = "insert into %s values (?, ?)" % data_type
	sum = 0
	for row in data:
		db.execute(insertString, (mktime(row[0].timetuple()), row[1]))
		sum += row[1]
	db.execute("insert into %s_daily values (?, ?)" % data_type, (mktime(date.timetuple()), sum))
	db.commit()

def dump_day(db, date):
	c = client()

	dump_to_db(db, "steps", date, c.intraday_steps(date))
	sleep(1)
	dump_to_db(db, "calories", date, c.intraday_calories_burned(date))
	sleep(1)
	dump_to_db(db, "active_score", date, c.intraday_active_score(date))
	sleep(1)
	dump_to_db(db, "sleep", date, c.intraday_sleep(date))
	sleep(1)

if __name__ == '__main__':
	db = connect_db(DB_FILE)

	#oneday = timedelta(days=1)
	#day = datetime(2009, 10, 18).date()
	#while day < datetime.now().date():
	#	print day
	#	dump_day(db, day)
	#	day += oneday

	dump_day(db, (datetime.now().date() - timedelta(days=1)))

	db.close()

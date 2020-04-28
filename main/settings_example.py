#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pymongo

secret_key = "abcdefghijklmnopqrstuvwxyz"

client = pymongo.MongoClient('localhost', 27017)
db = client.artlogic
appdir = '/home/colm/git/Jason-Scraper/static/'

# Logfile location
logFilename = os.path.join(appdir, 'logs/flask.log')
# Amount of logs kept
logBackupCount = 25
# Max log file size
logMaxBytes = 1024 * 1024 # For now 1MB
thumbsize = (240, 160)

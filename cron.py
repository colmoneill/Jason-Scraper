#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Performs fetch.py on these time settings
"""

from crontab import CronTab
#init cron
cron   = CronTab()

#add new cron job
job  = cron.new(command='fetch.py')

#job settings
job.hour.every(4)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

secret_key = "g\xd4\xb0\x10\xa5.\x91\r\xf374\xbc3\x87#\x07\x0bEtM\x1a\x86R\x1c-}\xdc\x86N7\xf7\xcf"

import pymongo

client = pymongo.MongoClient('localhost', 27017)
db = client.artlogic

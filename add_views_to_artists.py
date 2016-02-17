#!/usr/bin/env python
# -*- coding: utf-8 -*-

from main.settings import db

# Remove duplicates in artist.images
for artist in db.artist.find():
    if 'views' not in artist or \
    type(artist['views']) is not list:
        db.artist.update({"_id": artist['_id']}, {'$set': {'views': [] } } )
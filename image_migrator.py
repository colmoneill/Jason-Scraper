#!/usr/bin/env python
# -*- coding: utf-8 -*-

from main.settings import db
from bson import ObjectId

for image in db.image.find():
    if 'artist' in image and '_id' in image['artist']:
        artist = db.artist.find_one({ '_id' : ObjectId(image['artist']['_id']) })
        
        if artist:
            del image['artist']
            
            db.image.update({'_id' : ObjectId(image['_id']) }, image)
            
            del image['_id']
            
            if 'images' not in artist or type(artist['images']) is not list:
                artist['images'] = []
            
            artist['images'].append(image)
            
            db.artist.update({'_id' : ObjectId(artist['_id']) }, artist)
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from main.settings import db
from bson import ObjectId

# First ensure an images array on all the artist
for artist in db.artist.find():
    if 'images' not in artist or type(artist['images']) is not list:
        artist['images'] = []
        db.artist.update({'_id' : ObjectId(artist['_id']) }, artist)
        ## Update this artist on exhibitions as well
        db.exhibitions.update({"artist._id": ObjectId(artist['_id'])}, {"$set": { "artist": artist }}, multi=True)
        ## Should update this artist on group exhibitions as well
        db.exhibitions.update({"artists._id": ObjectId(artist['_id'])}, {"$set": {"artists.$": artist}}, multi=True)
        
# Walk through all the images, move the image to the artist, remove
# reference to the artist from the image.
for image in db.image.find():
    if 'artist' in image and '_id' in image['artist']:
        artist = db.artist.find_one({ '_id' : ObjectId(image['artist']['_id']) })
        
        if artist:
            del image['artist']
            
            db.image.update({'_id' : ObjectId(image['_id']) }, image)
            
            del image['_id']
            
            image['published'] = True
            
            artist['images'].append(image)
            ## Update this artist on exhibitions as well
            db.exhibitions.update({"artworks.path": image['path']}, {"$set": { "artworks.$": image }}, multi=True)
            
            db.artist.update({'_id' : ObjectId(artist['_id']) }, artist)
            ## Update this artist on exhibitions as well
            db.exhibitions.update({"artist._id": ObjectId(artist['_id'])}, {"$set": { "artist": artist }}, multi=True)
            ## Should update this artist on group exhibitions as well
            db.exhibitions.update({"artists._id": ObjectId(artist['_id'])}, {"$set": {"artists.$": artist}}, multi=True)
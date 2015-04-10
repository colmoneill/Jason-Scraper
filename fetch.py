#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Synch the local MongoDB database with the remote ArtLogic Feed
"""

import json
import sys
import urllib2
from datetime import datetime

import pymongo
import pytz

from utils import slugify
# from utils import logger

client = pymongo.MongoClient()
db = client.artlogic

def fetch_artworks():
    # logger.debug("downloading artwork data from Artlogic")
    
    artworks = []
    artists = []
    url = "http://feeds.artlogic.net/artworks/artlogiconline/json/"
    
    while True:
        f = urllib2.urlopen(url)
        data = json.load(f)
        
        artworks += data['rows']
        
        # logger.debug("retrieved page %s of %s of artwork data" % (data['feed_data']['page'], data['feed_data']['no_of_pages']))
        
        # Stop we are at the last page
        if data['feed_data']['page'] == data['feed_data']['no_of_pages']:
            break
        
        url = data['feed_data']['next_page_link']
    
    # Now we have a list called ‘artworks’ in which all the descriptions are stored
    # We are going to put them into the mongoDB database,
    # Making sure that if the artwork is already encoded (an object with the same id
    # already is in the database) we update the existing description instead of
    # inserting a new one (‘upsert’).
    
    # logger.debug("updating local mongodb database with %s entries" % len(artworks))
    
    for artwork in artworks:
        # Mongo does not like keys that have a dot in their name,
        # this property does not seem to be used anyway so let us
        # delete it:
        if 'artworks.description2' in artwork:
            del artwork['artworks.description2']
        # upsert int the database:
        db.artworks.update({"id": artwork['id']}, artwork, upsert=True)
        
        
        # artwork['artist_id'] is not functioning properly
        db.artists.update({"artist": artwork['artist']},
                          {"artist_sort": artwork['artist_sort'],
                           "artist":  artwork['artist'],
                           "slug": slugify(artwork['artist'])},
                          upsert=True)
    
    # db.meta.update({"subject": "artworks"}, {"updated": datetime.now(pytz.utc), "subject": "artworks"}, upsert=True)
    return artworks

if __name__ == "__main__":
    fetch_artworks()

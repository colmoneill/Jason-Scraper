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
import os

import time

from main.utils import slugify
# from utils import logger

client = pymongo.MongoClient()
db = client.artlogic

artwork_image_folder = 'static/uploads/artworks'

def fetchfile(url, dst):
    fi = urllib2.urlopen(url)
    fo = open(dst, 'wb')
    while True:
        chunk = fi.read(4096)
        if not chunk:
            fo.close()
            break
        fo.write(chunk)

def getsafepath (path, count = 1):
    root, ext = os.path.splitext(path)
    safepath = root + '-' + str(count) + ext

    if os.path.exists(safepath):
        return getsafepath(path, (count+1))
    else:
        return safepath

def fetch_artworks():
    # logger.debug("downloading artwork data from Artlogic")

    AL_artworks = []
    AL_artists = []
    url = "http://feeds.artlogic.net/websites/2.0/rodolphejanssen/artworks/json"

    while True:
        f = urllib2.urlopen(url)
        data = json.load(f)

        AL_artworks += data['rows']

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

    for artwork in AL_artworks:
        # Mongo does not like keys that have a dot in their name,
        # this property does not seem to be used anyway so let us
        # delete it:
        if 'artworks.description2' in artwork:
            del artwork['artworks.description2']
        # upsert int the database:
        db.AL_artworks.update({"id": artwork['id']}, artwork, upsert=True)

        slug = slugify(artwork['artist'])
        exisiting_artist = db.artist.find_one({ "slug": slug })

        if not exisiting_artist:
        # artwork['artist_id'] is not functioning properly
            db.artist.update({"name": artwork['artist']},
                              {"$set": {"name":  artwork['artist'],
                               "slug": slug,
                               "artist_sort": artwork['artist_sort']
                               }},
                              upsert=True)
        else:
            print "Artist already exists"


        # download image
        if artwork['img_url'] is None \
            or artwork['img_url'] == '' \
            or artwork['img_url'] == 'null':
            print "img_url is null, skipping"

        else:
            existing_image = db.image.find_one({ 'id_AL': artwork['id'] })
            if not existing_image:
                extension = os.path.splitext(artwork['img_url'])[1]
                dest = getsafepath(os.path.join(artwork_image_folder, slugify(artwork['artist']) + extension))
                fetchfile(artwork['img_url'], dest)

                db.image.insert({
                    'artist': db.artist.find_one({"slug": slugify(artwork['artist'])}),
                    'path': dest,
                    'title': artwork['title'],
                    'year': artwork['year'],
                    'medium': artwork['medium'],
                    'dimensions': artwork['dimensions'],
                    'stock_number': artwork['stock_number'],
                    'stock_number_sort': artwork['stock_number_sort'],
                    'id_AL': artwork['id'],
                    },
                    upsert=True
                )

                print "image downloaded"
            else:
                print "Skipped image; already in the database."
        #time.sleep(1)

    # db.meta.update({"subject": "artworks"}, {"updated": datetime.now(pytz.utc), "subject": "artworks"}, upsert=True)
    return AL_artworks

if __name__ == "__main__":
    fetch_artworks()

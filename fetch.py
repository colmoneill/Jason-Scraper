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

from bson import ObjectId
from main.utils import slugify, find_where
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
        #if 'artworks.description2' in artwork:
            #del artwork['artworks.description2']

        ## upsert int the database:
        #db.AL_artworks.update({"id": artwork['id']}, artwork, upsert=True)

        slug = slugify(artwork['artist'])
        artist = db.artist.find_one({ "slug": slug })

        if not artist:
            print 'created artist'
            artist = {
                'name': artwork['artist'],
                'slug': slug,
                'artist_sort': artwork['artist_sort'],
                'images': [],
                'selected_images': []
            }

            db.artist.insert(artist)
            artist = db.artist.find_one({ "slug": slug })

        if artwork['img_url'] is not None \
        and artwork['img_url'] <> '' \
        and artwork['img_url'] <> 'null' :

            if 'images' not in artist or type(artist['images']) is not list:
                artist['images'] = []

            if 'selected_images' not in artist or type(artist['selected_images']) is not list:
                artist['selected_images'] = []

            image = find_where('id_AL', artwork['id'], artist['images'])

            if not image:
                print 'created image'
                extension = os.path.splitext(artwork['img_url'])[1]
                dest = getsafepath(os.path.join(artwork_image_folder, slugify(artwork['artist']) + extension))
                fetchfile(artwork['img_url'], dest)

                image = {
                    '_id': ObjectId(),
                    'id_AL': artwork['id'],
                    'path': dest,
                    'title': artwork['title'],
                    'year': artwork['year'],
                    'medium': artwork['medium'],
                    'dimensions': artwork['dimensions'],
                    'stock_number': artwork['stock_number'],
                    'stock_number_sort': artwork['stock_number_sort']
                }

                artist['images'].append(image)
                artist['selected_images'].append(image)

                db.artist.update({'_id': artist['_id']}, {'$set': { 'images': artist['images'], 'selected_images': artist['selected_images'] } })

            else:
                print 'updated image'
                image['title'] = artwork['title']
                image['year'] = artwork['year']
                image['medium'] = artwork['medium']
                image['dimensions'] = artwork['dimensions']
                image['stock_number'] = artwork['stock_number']

                db.artist.update({'images._id': image['_id']}, {'$set': { 'images.$': image }})
                db.artist.update({'selected_images._id': image['_id']}, {'$set': { 'selected_images.$': image }})
                db.exhibitions.update({'artworks._id': image['_id']}, {'$set': { 'artworks.$': image }}, multi=True)

            artist = db.artist.find_one({"_id": artist['_id']})
            db.exhibitions.update({"artist._id": artist['_id']}, {"$set": { "artist": artist }}, multi=True)
            ## Should update this artist on group exhibitions as well
            db.exhibitions.update({"artists._id": artist['_id']}, {"$set": {"artists.$": artist}}, multi=True)

    return AL_artworks

if __name__ == "__main__":
    fetch_artworks()

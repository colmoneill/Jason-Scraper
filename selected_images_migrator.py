#!/usr/bin/env python
# -*- coding: utf-8 -*-

from main.settings import db

# Update arists
for artist in db.artist.find():
    artist['selected_images'] = []

    if 'images' in artist:
        for image in artist['images']:
            if 'published' in image \
            and image['published']:
                artist['selected_images'].append(image)

        db.artist.update({'_id' : artist['_id'] }, artist)
        ## Update this artist on exhibitions as well
        db.exhibitions.update({"artist._id": artist['_id']}, {"$set": { "artist": artist }}, multi=True)
        ## Should update this artist on group exhibitions as well
        db.exhibitions.update({"artists._id": artist['_id']}, {"$set": {"artists.$": artist}}, multi=True)
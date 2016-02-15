#!/usr/bin/env python
# -*- coding: utf-8 -*-

from main.settings import db
from main.utils import find_where

# Remove duplicates in artist.images
for artist in db.artist.find():
    # start new list of image
    new_images = []

    for image in artist['images']:
        # Check whether the image isn't in the list yet
        if not find_where('path', image['path'], new_images):
            new_images.append(image)

    artist['images'] = new_images

    db.artist.update({"_id": artist['_id']}, artist)

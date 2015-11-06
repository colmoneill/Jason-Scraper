#!/usr/bin/env python
# -*- coding: utf-8 -*-

from main.settings import db
from bson import ObjectId

for exhibition in db.exhibitions.find():
    images = []

    if 'images' in exhibition and type(exhibition['images']) is list:
        for image in exhibition['images']:
            if type(image) is dict:
                image['_id'] = ObjectId()
                images.append(image)
            print 'added id to exhibition view'
    exhibition['images'] = images

    db.exhibitions.update({ '_id': exhibition['_id'] }, exhibition)

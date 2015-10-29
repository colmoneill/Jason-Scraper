#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, abort
from bson.json_util import dumps as bson_dumps
from .. import utils
import pymongo
import os
from bson import ObjectId
from ..settings import db

blueprint = Blueprint('admin_json_api', __name__)



"""
    Returns JSON-array with images for given artist. Or 404
"""
@blueprint.route('/artist/<artist_id>/image', methods=['GET'])
def imagesPerArtist(artist_id):
    artist = db.artist.find_one({'_id': ObjectId(artist_id)})
    
    if 'images' in artist:
        return bson_dumps([{'path': image['path'], 'published': image['published']} for image in artist['images']])
    else:
        return  bson_dumps([])
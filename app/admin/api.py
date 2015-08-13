#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, abort
from bson.json_util import dumps as bson_dumps
import utils
import pymongo

blueprint = Blueprint('admin_json_api', __name__)

client = pymongo.MongoClient()
db = client.artlogic


"""
    Returns JSON-array with images for given artist. Or 404
"""
@blueprint.route('/artist/<artist_id>/image', methods=['GET'])
def imagesPerArtist(artist_id):
    images = db.image.find({'artist._id': ObjectId(artist_id)})
    
    if len(images) > 0:
        return bson_dumps(images)
    else:
        abort(404)
        
"""
    Direct upload function. Stores given image in the artist images
    store location. Returns JSON DB-entry
"""
@blueprint.route("/artist/<artist_id>/image/create", methods=['POST'])
def uploadArtistImage(artist_id):
    artist = db.artist.find_one({'_id': ObjectId(artist_id)})

    if artist:
        image = {
            'artist': artist,
            'path': utils.handle_uploaded_file(
                request.files['image'],
                app.config['UPLOAD']['ARTWORK_IMAGE']
            )
        }

        db.image.insert(image)
        return bson_dumps(image)
    else:
       abort(404)

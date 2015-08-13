#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python Standard Library
import os
from datetime import datetime

# Dependencies: Flask + PIL or Pillowexhibition/create/
from functools import wraps
from flask import   Flask, flash, send_from_directory, \
                    redirect as redirect_flask, \
                    render_template, url_for, request, \
                    abort, Response, session
from flask_pagedown import PageDown

import pymongo

import utils
from bson import ObjectId
from bson.json_util import dumps
import forms

import json

from utils import login_required

client = pymongo.MongoClient()
db = client.artlogic

from flask import Blueprint, render_template, abort
    
blueprint = Blueprint('admin_artist', __name__)

@blueprint.route('/', methods=['GET'])
@login_required
def index():
    artists = db.artist.find()
    return render_template('admin/artist/index.html', artists=artists)

@blueprint.route('/create/', methods=['GET','POST'])
@login_required
def create():
    form = forms.ArtistForm()
    exhibitions = db.exhibitions.find()

    if form.validate_on_submit():
        formdata = form.data
        artist = utils.handle_form_data({}, formdata, ['press_release_file'])
        artist['slug'] = utils.slugify(artist['name'])

        if request.files['press_release_file']:
            artist['press_release'] = utils.handle_uploaded_file(
                request.files['press_release_file'],
                app.config['UPLOAD']['PRESS_RELEASE'],
                '{0}.pdf'.format(artist['slug'])
            )

        filename = secure_filename(form.fileName.file.filename)
        form.fileName.file.save(file_path)

        db.artist.insert(artist)
        flash('You successfully created an artist page')
        return redirect_flask(url_for('.index'))

    return render_template('admin/artist/create.html', form=form, exhibitions=exhibitions)


@blueprint.route('/update/<artist_id>', methods=['GET', 'POST'])
@login_required
def update(artist_id):
    artist = db.artist.find_one({"_id": ObjectId(artist_id)})
    images = db.image.find({"artist": artist})
    exhibitions = db.exhibitions.find()

    if request.method == 'POST':
        form = forms.ArtistForm()

        if form.validate_on_submit():
            formdata = form.data
            artist =  utils.handle_form_data(artist, formdata, ['press_release_file'])
            db.artist.update({"_id": ObjectId(artist_id)}, artist)
            
            ## Update this artist on images as well
            db.image.update({"artist._id": ObjectId(artist_id)}, {"$set": { "artist": artist }}, multi=True)
            ## Update this artist on exhibitions as well
            db.image.update({"exhibition._id": ObjectId(artist_id)}, {"$set": { "artist": artist }}, multi=True)

            if request.files['press_release_file']:
                artist['press_release'] = utils.handle_uploaded_file(
                    request.file['press_release_file'],
                    app.config['UPLOAD']['PRESS_RELEASE'],
                    '{0}.pdf'.format(artists['slug'])
                )
                
            flash('You\'ve updated the artist page successfully')
            return redirect_flask(url_for('.index'))

    else:
        form = forms.ArtistForm(data=artist)

    return render_template('admin/artist/edit.html', form=form, images=images, exhibitions=exhibitions)

@blueprint.route('/delete/<artist_id>', methods=['GET', 'POST'])
@login_required
def deleteArtist(artist_id):
    if request.method == 'POST':
        print artist_id
        db.artist.remove({"_id": ObjectId(artist_id)})
        flash('You deleted the artist page')
        return redirect_flask(url_for('.index'))

    return render_template('admin/artist/delete.html')

"""
    Publish method, sets an artist to be published or not.
    Returns JSON version of the published artist
"""
@blueprint.route("/publish/<artist_id>", methods=['POST'])
@login_required
def publishArtist (artist_id):
    is_published = ('true' == request.form['is_published'])
    db.artist.update(
        {'_id': ObjectId(artist_id)},
        {'$set': {'is_published': is_published}}
    )
    return dumps(db.artist.find_one({'_id': ObjectId(artist_id)}))

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

from .. import utils, settings
from bson import ObjectId
from bson.json_util import dumps as bson_dumps
import forms

from . import config

import json

from ..settings import db

from flask import Blueprint, render_template, abort

from ..utils import login_required

blueprint = Blueprint('admin_exhibition', __name__)

### single artist exhibition ###
@blueprint.route("/")
@login_required
def index():
    exhibitions = db.exhibitions.find().sort([
            ("end", -1 ),
            ("start", -1 )
            ])
    return render_template('admin/exhibition/index.html', exhibitions=exhibitions)

"""
    Sets an exhibition to be publically visible
    or not. Returns JSON object
"""
@blueprint.route("/publish/<exhibition_id>", methods=['POST'])
@login_required
def publish(exhibition_id):
    is_published = ('true' == request.form['is_published'])
    db.exhibitions.update(
        {'_id': ObjectId(exhibition_id)},
        {'$set': {'is_published': is_published}}
    )
    return bson_dumps(db.exhibitions.find_one({'_id': ObjectId(exhibition_id)}))


@blueprint.route("/create/", methods=['GET', 'POST'])
@login_required
def create():
    form = forms.ExhibitionForm()
    form.artist.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find().sort("artist_sort")]

    selectedArtworks = []

    if form.is_submitted():
        if form.validate():

            formdata = form.data
            artist = db.artist.find_one({'_id': ObjectId(formdata['artist'])})
            exhibition = utils.handle_form_data({}, formdata, ['press_release', 'artist'])
            exhibition['artist'] = artist
            exhibition['slug'] = utils.slugify(exhibition['exhibition_name'])
            exhibition_md = form.wysiwig_exhibition_description.data
            exhibition['artworks'] = [db.image.find_one({'_id': ObjectId(image_id)}) for image_id in request.form.getlist('artwork')]

            filenamebase = artist['slug'] + '-' + exhibition['start'].strftime('%d-%m-%Y')

            artist_md = form.wysiwig_artist_bio.data

            if request.files['press_release']:
                exhibition['press_release'] = utils.handle_uploaded_file(
                    request.files['press_release'],
                    config.upload['PRESS_RELEASE'],
                    utils.setfilenameroot(request.files['press_release'].filename, filenamebase)
                )

                exhibition['press_release_size'] = utils.getfilesize(exhibition['press_release'])

            exhibition['artworks'] = []
            uploaded_artworks = []

            # New artworks
            if 'artworks' in request.files:
                for uploaded_artwork_image in request.files.getlist('artworks'):
                    image_path = utils.handle_uploaded_file(
                            uploaded_artwork_image,
                            config.upload['ARTWORK_IMAGE'],
                            utils.setfilenameroot(uploaded_artwork_image.filename, artist['slug'])
                        )

                    uploaded_artworks.append(image_path)
                    artist['images'].append({ '_id': ObjectId(), 'path': image_path, 'published': False })

                db.artist.update({'_id': artist['_id']}, artist)
                ## Update this artist on exhibitions as well
                db.exhibitions.update({"artist._id": ObjectId(artist['_id'])}, {"$set": { "artist": artist }}, multi=True)
                ## Should update this artist on group exhibitions as well
                db.exhibitions.update({"artists._id": ObjectId(artist['_id'])}, {"$set": {"artists.$": artist}}, multi=True)

            if 'artworks' in request.form:
                for artwork_image_path in request.form.getlist('artworks'):
                    if artwork_image_path:
                        if artwork_image_path[0:9] == 'uploaded:':
                            artwork_index = int(artwork_image_path[9:])
                            artwork_image_path = uploaded_artworks[artwork_index]

                        image = utils.find_where('path', artwork_image_path, artist['images'])
                        exhibition['artworks'].append(image)

            if 'coverimage' in request.files:
                uploaded_image = request.files.getlist('coverimage')[0]
                exhibition['coverimage'] = {
                    'path': utils.handle_uploaded_file(
                        uploaded_image,
                        config.upload['EXHIBITION_COVER_IMAGE'],
                        utils.setfilenameroot(uploaded_image.filename, filenamebase)
                    )
                }

            exhibition['images'] = []
            uploaded_images = []

            if 'image' in request.files:
                for uploaded_image in request.files.getlist('image'):
                    uploaded_images.append(
                        utils.handle_uploaded_file(
                            uploaded_image,
                            config.upload['EXHIBITION_VIEW'],
                            utils.setfilenameroot(uploaded_image.filename, filenamebase)
                        )
                    )

            if 'image' in request.form:
                for image in request.form.getlist('image'):
                    if image:
                        if image[0:9] == 'uploaded:':
                            image_index = int(image[9:])
                            exhibition['images'].append({
                            '_id': ObjectId(),
                            'path': uploaded_images[image_index]
                            })

            db.exhibitions.insert(exhibition)
            flash('You successfully created an exhibition', 'success')

            if request.is_xhr:
                return bson_dumps(exhibition), 201
            else:
                return redirect_flask(url_for('.index'))

        elif request.is_xhr:
            return json.dumps(form.errors), 400

        selectedArtworks = request.form.getlist('artworks')

    return render_template('admin/exhibition/create.html', form=form, selectedArtworks=json.dumps(selectedArtworks))


@blueprint.route("/update/<exhibition_id>", methods=['GET', 'POST'])
@login_required
def update(exhibition_id):
    form = forms.ExhibitionForm()
    exhibition = db.exhibitions.find_one({"_id": ObjectId(exhibition_id)})

    if form.is_submitted():
        form.artist.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find().sort("artist_sort")]

        if form.validate():
            formdata = form.data
            artist = db.artist.find_one({"_id": ObjectId(formdata['artist'])})
            exhibition = utils.handle_form_data(exhibition, formdata, ['press_release'])
            exhibition['artist'] = artist

            filenamebase = artist['slug'] + '-' + exhibition['start'].strftime('%d-%m-%Y')

            exhibition['artworks'] = []
            uploaded_artworks = []

            # New artworks
            if 'artworks' in request.files:
                for uploaded_artwork_image in request.files.getlist('artworks'):
                    image_path = utils.handle_uploaded_file(
                            uploaded_artwork_image,
                            config.upload['ARTWORK_IMAGE'],
                            utils.setfilenameroot(uploaded_artwork_image.filename, artist['slug'])
                        )

                    uploaded_artworks.append(image_path)
                    artist['images'].append({ '_id': ObjectId(), 'path': image_path, 'published': False })

                db.artist.update({'_id': artist['_id']}, artist)
                ## Update this artist on exhibitions as well
                db.exhibitions.update({"artist._id": ObjectId(artist['_id'])}, {"$set": { "artist": artist }}, multi=True)
                ## Should update this artist on group exhibitions as well
                db.exhibitions.update({"artists._id": ObjectId(artist['_id'])}, {"$set": {"artists.$": artist}}, multi=True)

            if 'artworks' in request.form:
                for artwork_image_path in request.form.getlist('artworks'):
                    if artwork_image_path:
                        if artwork_image_path[0:9] == 'uploaded:':
                            artwork_index = int(artwork_image_path[9:])
                            artwork_image_path = uploaded_artworks[artwork_index]

                        image = utils.find_where('path', artwork_image_path, artist['images'])
                        exhibition['artworks'].append(image)

            if request.files['press_release']:
                exhibition['press_release'] = utils.handle_uploaded_file(
                        request.files['press_release'],
                        config.upload['PRESS_RELEASE'],
                        utils.setfilenameroot(request.files['press_release'].filename, filenamebase)
                    )

                exhibition['press_release_size'] = utils.getfilesize(exhibition['press_release'])
            elif 'press_release' not in request.form \
                and 'press_release' in exhibition:
                    del exhibition['press_release']

            if 'coverimage' in request.files:
                uploaded_image = request.files.getlist('coverimage')[0]
                exhibition['coverimage'] = {
                    'path': utils.handle_uploaded_file(
                        uploaded_image,
                        config.upload['EXHIBITION_COVER_IMAGE'],
                        utils.setfilenameroot(uploaded_image.filename, filenamebase)
                    )
                }

            elif 'coverimage' not in request.form:
                if 'coverimage' in exhibition:
                    del exhibition['coverimage']

            old_images = exhibition['images']
            exhibition['images'] = []
            uploaded_images = []

            if 'image' in request.files:
                for uploaded_image in request.files.getlist('image'):
                    uploaded_images.append(
                        utils.handle_uploaded_file(
                            uploaded_image,
                            config.upload['EXHIBITION_VIEW'],
                            utils.setfilenameroot(uploaded_image.filename, filenamebase)
                        )
                    )

            for path in request.form.getlist('image'):
                if path:
                    if path[0:9] == 'uploaded:':
                        image_index = int(path[9:])
                        path = uploaded_images[image_index]
                        exhibition['images'].append({'_id': ObjectId(), 'path': path})
                    else:
                        image = utils.find_where('path', path, old_images)
                            
                        if image:
                            exhibition['images'].append(image)
                        
            db.exhibitions.update({"_id": ObjectId(exhibition_id)}, exhibition)
            flash('You successfully updated the exhibition data', 'success')

            if request.is_xhr:
                return bson_dumps(exhibition), 201
            else:
                return redirect_flask(url_for('.index'))
        elif request.is_xhr:
            return json.dumps(form.errors), 400

    exhibition['artist'] = str(exhibition['artist']['_id'])
    form = forms.ExhibitionForm(data=exhibition)
    form.artist.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]

    return render_template('admin/exhibition/edit.html',
                                form=form,
                                selectedArtworks=utils.prepare_images(exhibition['artworks'] if 'artworks' in exhibition else []),
                                coverimage=[exhibition['coverimage']] if 'coverimage' in exhibition else [],
                                images=exhibition['images'] if 'images' in exhibition else [])


@blueprint.route("/delete/<exhibition_id>", methods=['GET', 'POST'])
@login_required
def delete(exhibition_id):
    if request.method == 'POST':
        print(exhibition_id)
        db.exhibitions.remove({"_id": ObjectId(exhibition_id)})
        flash('You deleted the exhibition', 'warning')
        return redirect_flask(url_for('.index'))

    return render_template('admin/exhibition/delete.html')

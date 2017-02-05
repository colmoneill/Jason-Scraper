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

from .. import utils
from bson import ObjectId
from bson.json_util import dumps as bson_dumps
import forms

import config

import json

from ..settings import db
from flask import Blueprint, render_template, abort

from ..utils import login_required

blueprint = Blueprint('admin_group-exhibition', __name__)

### group exhibition ###
@blueprint.route("/")
@login_required
def index():
    print 'exhibition index function'
    exhibitions = db.exhibitions.find()
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
    return dumps(db.exhibitions.find_one({'_id': ObjectId(exhibition_id)}))

@blueprint.route("/create/", methods=['GET', 'POST'])
@login_required
def createGroupExhibition():
    form = forms.GroupExhibitionForm()
    artist = db.artist.find()
    form.artists.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find().sort("artist_sort")]

    selectedArtworks = []

    if form.is_submitted():
        if form.validate():

            formdata = form.data

            exhibition = utils.handle_form_data({}, formdata, ['press_release', 'artists', 'extra_artists'])
            exhibition['artists'] = [db.artist.find_one({'_id': ObjectId(artist_id)}) for artist_id in request.form.getlist('artists')]
            exhibition['slug'] = utils.slugify(exhibition['exhibition_name'])
            exhibition_md = form.wysiwig_exhibition_description.data
            exhibition['is_group_expo'] = True
            extra_artists = zip(request.form.getlist('extra_artists_name'), request.form.getlist('extra_artists_sort'))
            exhibition['extra_artists'] = [{'name': name, 'artist_sort': sort} for name, sort in extra_artists]
            
            exhibition['artworks'] = []
            uploaded_artworks = []

            if 'artworks' in request.files:
                for uploaded_image in request.files.getlist('artworks'):
                    image_path = utils.handle_uploaded_file(
                        uploaded_image,
                        config.upload['ARTWORK_IMAGE'],
                        utils.setfilenameroot(uploaded_image.filename, exhibition['artists'][0]['slug'])
                    )
                    
        
                    exhibition['artists'][0]['images'].append({ '_id': ObjectId(), 'path': image_path, 'published': False })
                    uploaded_artworks.append(image_path)
                    
                db.artist.update({'_id': exhibition['artists'][0]['_id']}, exhibition['artists'][0])
                ## Update this artist on exhibitions as well
                db.exhibitions.update({"artist._id": ObjectId(artist_id)}, {"$set": { "artist": artist }}, multi=True)
                ## Should update this artist on group exhibitions as well
                db.exhibitions.update({"artists._id": ObjectId(artist_id)}, {"$set": {"artists.$": artist}}, multi=True)

            if 'artworks' in request.form:
                for artwork_image_path in request.form.getlist('artworks'):
                    if artwork_image_path:
                        if artwork_image_path[0:9] == 'uploaded:':
                            artwork_index = int(artwork_image_path[9:])
                            artwork_image_path = uploaded_artworks[artwork_index]
                        
                        for artist in exhibition['artists']:
                            image = utils.find_where('path', artwork_image_path, artist['images'])
                            
                            if image:
                                exhibition['artworks'].append(image)
                                break

            if request.files['press_release']:
                exhibition['press_release'] = utils.handle_uploaded_file(
                    request.files['press_release'],
                    config.upload['PRESS_RELEASE'],
                    utils.setfilenameroot(request.files['press_release'].filename, exhibition['slug'])
                )
                exhibition['press_release_size'] = utils.getfilesize(exhibition['press_release'])

            if 'coverimage' in request.files:
                uploaded_image = request.files.getlist('coverimage')[0]
                exhibition['coverimage'] = {
                    'path': utils.handle_uploaded_file(
                        uploaded_image,
                        config.upload['EXHIBITION_COVER_IMAGE'],
                        utils.setfilenameroot(uploaded_image.filename, exhibition['slug'])
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
                            utils.setfilenameroot(uploaded_image.filename, exhibition['slug'])
                        )
                    )
            
            if 'image' in request.form:
                for path in request.form.getlist('image'):
                    if path[0:9] == 'uploaded:':
                        image_index = int(path[9:])
                        path = uploaded_images[image_index]
                        
                        exhibition['images'].append({'path': path})

            inserted_id = db.exhibitions.insert(exhibition)
            
            flash(u'You successfully created the group exhibition, <a href="{1}">{0}</a>'.format(exhibition['exhibition_name'], url_for('.updateGroupExhibition', exhibition_id = inserted_id)), 'success')

            if request.is_xhr:
                return bson_dumps(exhibition), 201
            else:
                return redirect_flask(url_for('.index'))
        elif request.is_xhr:
            return json.dumps(form.errors), 400

        selectedArtworks = request.form.getlist('artworks')

    return render_template('admin/group-exhibition/exhibitionCreate.html', form=form, selectedArtworks=json.dumps(selectedArtworks))

@blueprint.route("/update/<exhibition_id>", methods=['GET', 'POST'])
@login_required
def updateGroupExhibition(exhibition_id):
    exhibition = db.exhibitions.find_one({"_id": ObjectId(exhibition_id)})

    form = forms.GroupExhibitionForm()
    form.artists.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find().sort("artist_sort")]

    if form.is_submitted():
        if form.validate():
            formdata = form.data
            exhibition = utils.handle_form_data(exhibition, formdata, ['press_release', 'artists', 'extra_artists'])
            exhibition['artists'] = [db.artist.find_one({'_id': ObjectId(artist_id)}) for artist_id in request.form.getlist('artists')]
            extra_artists = zip(request.form.getlist('extra_artists_name'), request.form.getlist('extra_artists_sort'))
            exhibition['extra_artists'] = [{'name': name, 'artist_sort': sort} for name, sort in extra_artists]
            exhibition['artworks'] = []
            uploaded_artworks = []
            
            if 'artworks' in request.files:
                for uploaded_image in request.files.getlist('artworks'):
                    image_path = utils.handle_uploaded_file(
                        uploaded_image,
                        config.upload['ARTWORK_IMAGE'],
                        utils.setfilenameroot(uploaded_image.filename, exhibition['artists'][0]['slug'])
                    )
        
                    exhibition['artists'][0]['images'].append({ '_id': ObjectId(), 'path': image_path, 'published': False })
                    uploaded_artworks.append(image_path)
                    
                db.artist.update({'_id': exhibition['artists'][0]['_id']}, exhibition['artists'][0])
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
                        
                        for artist in exhibition['artists']:
                            image = utils.find_where('path', artwork_image_path, artist['images'])
                            
                            if image:
                                exhibition['artworks'].append(image)
                                break


            if request.files['press_release']:
                exhibition['press_release'] = utils.handle_uploaded_file(
                        request.files['press_release'],
                        config.upload['PRESS_RELEASE'],
                        utils.setfilenameroot(request.files['press_release'].filename, exhibition['slug'])
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
                        utils.setfilenameroot(uploaded_image.filename, exhibition['slug'])
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
                            utils.setfilenameroot(uploaded_image.filename, exhibition['slug'])
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

            db.exhibitions.update({ "_id": ObjectId(exhibition_id) }, exhibition)
            flash(u'You successfully updated the exhibition data on <a href="{1}">{0}</a>'.format(exhibition['exhibition_name'], url_for('.updateGroupExhibition', exhibition_id = exhibition_id)), 'success')

            if request.is_xhr:
                return bson_dumps(exhibition), 201
            else:
                return redirect_flask(url_for('.index'))

        elif request.is_xhr:
            json.dumps(form.errors), 400
    else:
        exhibition['artists'] = [str(artist['_id']) for artist in exhibition['artists']]
        form = forms.GroupExhibitionForm(data=exhibition)
        form.artists.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]
        
    return render_template('admin/group-exhibition/exhibitionEdit.html',
                                form=form,
                                selectedArtworks=utils.prepare_images(exhibition['artworks']),
                                coverimage = [exhibition['coverimage']] if 'coverimage' in exhibition else [],
                                images=exhibition['images'] if 'images' in exhibition else [],
                                extra_artists=exhibition['extra_artists'] if 'extra_artists' in exhibition else [])


@blueprint.route("/delete/<exhibition_id>", methods=['GET', 'POST'])
@login_required
def deleteGroupExhibition(exhibition_id):
    if request.method == 'POST':
        print exhibition_id
        db.exhibitions.remove({"_id": ObjectId(exhibition_id)})
        flash(u'You deleted the exhibition', 'warning')
        return redirect_flask(url_for('.index'))

    return render_template('admin/group-exhibition/exhibitionDelete.html')

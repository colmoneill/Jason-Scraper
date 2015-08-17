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
from bson.json_util import dumps as bson_dumps
import forms

import config

import json

from ..settings import db

from flask import Blueprint, render_template, abort

from utils import login_required

blueprint = Blueprint('admin_exhibition', __name__)

### single artist exhibition ###
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
    return bson_dumps(db.exhibitions.find_one({'_id': ObjectId(exhibition_id)}))

@blueprint.route("/create/", methods=['GET', 'POST'])
@login_required
def create():
    form = forms.ExhibitionForm()
    form.artist.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]

    selectedArtworks = []

    if form.is_submitted():
        if form.validate():
            formdata = form.data

            exhibition = utils.handle_form_data({}, formdata, ['press_release_file', 'artist'])
            exhibition['artist'] = db.artist.find_one({'_id': ObjectId(formdata['artist'])})
            exhibition['slug'] = utils.slugify(exhibition['exhibition_name'])
            exhibition_md = form.wysiwig_exhibition_description.data
            exhibition['artworks'] = [db.image.find_one({'_id': ObjectId(image_id)}) for image_id in request.form.getlist('artwork')]
            artist_md = form.wysiwig_artist_bio.data

            if request.files['press_release_file']:
                exhibition['press_release'] = utils.handle_uploaded_file(
                    request.files['press_release_file'],
                    config.upload['PRESS_RELEASE'],
                    utils.setfilenameroot(request.files['press_release_file'], exhibition['slug'])
                )
                
            if 'coverimage' in request.files:
                uploaded_image = request.files.getlist('coverimage')[0]
                exhibition['coverimage'] = {
                    'path': utils.handle_uploaded_file(
                        uploaded_image,
                        config.upload['EXHIBITION_COVER_IMAGE'],
                        utils.setfilenameroot(uploaded_image.filename, exhibition['slug'])
                    )
                }
            
            if 'image' in request.files:
                exhibition['images'] = []
                for uploaded_image in request.files.getlist('image'):
                    exhibition['images'].append({
                        'path': utils.handle_uploaded_file(
                            uploaded_image,
                            config.upload['EXHIBITION_VIEW'],
                            utils.setfilenameroot(uploaded_image.filename, exhibition['slug'])
                        )
                    })

            db.exhibitions.insert(exhibition)
            flash(u'You successfully created an exhibition', 'success')
            
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
        form.artist.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]
        exhibition['artworks'] = [db.image.find_one({'_id': ObjectId(image_id)}) for image_id in request.form.getlist('artworks')]

        if form.validate():
            formdata = form.data
            exhibition = utils.handle_form_data(exhibition, formdata, ['press_release_file'])
            exhibition['artist'] = db.artist.find_one({"_id": ObjectId(formdata['artist'])})


            if request.files['press_release_file']:
                exhibition['press_release'] = utils.handle_uploaded_file(
                    request.files['press_release_file'],
                    config.upload['PRESS_RELEASE'],
                    '{0}.pdf'.format(exhibition['slug'])
            )


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
            
            images = []
            
            for image in exhibition['images']:
                if image['path'] in request.form.getlist('image'):
                    images.append(image)
            
            exhibition['images'] = images
            
            if 'image' in request.files:
                for uploaded_image in request.files.getlist('image'):
                    exhibition['images'].append({
                        'path': utils.handle_uploaded_file(
                            uploaded_image,
                            config.upload['EXHIBITION_VIEW'],
                            utils.setfilenameroot(uploaded_image.filename, exhibition['slug'])
                        )
                    })

            db.exhibitions.update({"_id": ObjectId(exhibition_id)}, exhibition)
            flash(u'You successfully updated the exhibition data', 'success')
            
            if request.is_xhr:
                return bson_dumps(exhibition), 201
            else:
                return redirect_flask(url_for('.index'))
        elif request.is_xhr:
            return json.dumps(form.errors), 400
        
    selectedArtworks = [str(image['_id']) for image in exhibition['artworks']]
    exhibition['artist'] = str(exhibition['artist']['_id'])
    form = forms.ExhibitionForm(data=exhibition)
    form.artist.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]

    return render_template('admin/exhibition/edit.html',
                                form=form,
                                selectedArtworks=json.dumps(selectedArtworks),
                                coverimage=[exhibition['coverimage']] if 'coverimage' in exhibition else [],
                                images=exhibition['images'] if 'images' in exhibition else [])

@blueprint.route("/delete/<exhibition_id>", methods=['GET', 'POST'])
@login_required
def delete(exhibition_id):
    if request.method == 'POST':
        print exhibition_id
        db.exhibitions.remove({"_id": ObjectId(exhibition_id)})
        flash(u'You deleted the exhibition', 'warning')
        return redirect_flask(url_for('.index'))

    return render_template('admin/exhibition/delete.html')

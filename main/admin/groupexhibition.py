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
    form.artists.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]

    selectedArtworks = []

    if form.is_submitted():
        if form.validate():
            
            formdata = form.data
            
            exhibition = utils.handle_form_data({}, formdata, ['press_release_file', 'artists'])
            exhibition['artists'] = [db.artist.find_one({'_id': ObjectId(artist_id)}) for artist_id in request.form.getlist('artists')]
            exhibition['slug'] = utils.slugify(exhibition['exhibition_name'])
            exhibition_md = form.wysiwig_exhibition_description.data
            exhibition['is_group_expo'] = True

            exhibition['artworks'] = []
            
            if 'artworks' in request.files:
                for uploaded_image in request.files.getlist('artworks'):
                    image_id = db.image.insert({
                        'artist': exhibition['artists'][0],
                        'path': utils.handle_uploaded_file(
                                uploaded_image,
                                config.upload['ARTWORK_IMAGE'],
                                utils.setfilenameroot(uploaded_image.filename, artist['slug'])
                            )
                    })
                        
                    exhibition['artworks'].append(db.image.find_one({'_id': image_id}))

            if 'artworks' in request.form:
                for artwork_id in request.form.getlist('artworks'):
                    exhibition['artworks'].append(db.image.find_one({'_id': ObjectId(artwork_id)}))

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
            flash(u'You successfully created a group exhibition', 'success')
            
            if request.is_xhr:
                return bson_dumps(exhibition), 201
            else:
                return redirect_flask(url_for('.index'))
        elif request.is_xhr:
            return json.dumps(form.errors), 400

        selectedArtworks = request.form.getlist('artworks')

    return render_template('admin/group-exhibition/exhibitionCreate.html', form=form, selectedArtworks=selectedArtworks)

@blueprint.route("/update/<exhibition_id>", methods=['GET', 'POST'])
@login_required
def updateGroupExhibition(exhibition_id):
    exhibition = db.exhibitions.find_one({"_id": ObjectId(exhibition_id)})

    form = forms.GroupExhibitionForm()
    form.artists.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]
    
    if form.is_submitted():
        if form.validate():
            formdata = form.data
            artists = db.artist.find()
            exhibition = utils.handle_form_data(exhibition, formdata, ['press_release_file', 'artists'])
            exhibition['artists'] = [db.artist.find_one({'_id': ObjectId(artist_id)}) for artist_id in request.form.getlist('artists')]

            exhibition['artworks'] = []
            
            if 'artworks' in request.files:
                for uploaded_image in request.files.getlist('artworks'):
                    image_id = db.image.insert({
                        'artist': exhibition['artists'][0],
                        'path': utils.handle_uploaded_file(
                                uploaded_image,
                                config.upload['ARTWORK_IMAGE'],
                                utils.setfilenameroot(uploaded_image.filename, artist['slug'])
                            )
                    })
                        
                    exhibition['artworks'].append(db.image.find_one({'_id': image_id}))

            if 'artworks' in request.form:
                for artwork_id in request.form.getlist('artworks'):
                    exhibition['artworks'].append(db.image.find_one({'_id': ObjectId(artwork_id)}))


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
            
            exhibition['images'] = []
            
            for path in request.form.getlist('image'):
                exhibition['images'].append({'path': path})
            
            if 'image' in request.files:
                for uploaded_image in request.files.getlist('image'):
                    exhibition['images'].append({
                        'path': utils.handle_uploaded_file(
                            uploaded_image,
                            config.upload['EXHIBITION_VIEW'],
                            utils.setfilenameroot(uploaded_image.filename, exhibition['slug'])
                        )
                    })
           
            db.exhibitions.update({ "_id": ObjectId(exhibition_id) }, exhibition)
            flash(u'You successfully updated the exhibition data', 'success')
            
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

    selectedArtworks = [str(image['_id']) for image in exhibition['artworks']] if 'artworks' in exhibition else []

    return render_template('admin/group-exhibition/exhibitionEdit.html',
                                form=form,
                                selectedArtworks=json.dumps(selectedArtworks),
                                coverimage = [exhibition['coverimage']] if 'coverimage' in exhibition else [],
                                images=exhibition['images'] if 'images' in exhibition else [])


@blueprint.route("/delete/<exhibition_id>", methods=['GET', 'POST'])
@login_required
def deleteGroupExhibition(exhibition_id):
    if request.method == 'POST':
        print exhibition_id
        db.exhibitions.remove({"_id": ObjectId(exhibition_id)})
        flash(u'You deleted the exhibition', 'warning')
        return redirect_flask(url_for('.index'))

    return render_template('admin/group-exhibition/exhibitionDelete.html')

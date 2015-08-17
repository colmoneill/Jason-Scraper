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

import config

import json

client = pymongo.MongoClient()
db = client.artlogic

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
    return dumps(db.exhibitions.find_one({'_id': ObjectId(exhibition_id)}))

@blueprint.route("/create/", methods=['GET', 'POST'])
@login_required
def create():
    form = forms.ExhibitionForm()
    form.artist.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]

    selectedImages = []

    if form.is_submitted():
        if form.validate_on_submit():
            formdata = form.data

            exhibition = utils.handle_form_data({}, formdata, ['press_release_file', 'artist'])
            exhibition['artist'] = db.artist.find_one({'_id': ObjectId(formdata['artist'])})
            exhibition['slug'] = utils.slugify(exhibition['exhibition_name'])
            exhibition_md = form.wysiwig_exhibition_description.data
            exhibition['images'] = [db.image.find_one({'_id': ObjectId(image_id)}) for image_id in request.form.getlist('image')]
            artist_md = form.wysiwig_artist_bio.data

            if request.files['press_release_file']:
                exhibition['press_release'] = utils.handle_uploaded_file(
                    request.files['press_release_file'],
                    config.upload['PRESS_RELEASE'],
                    '{0}.pdf'.format(exhibition['slug'])
                )

            db.exhibitions.insert(exhibition)
            flash(u'You successfully created an exhibition', 'success')
            return redirect_flask(url_for('.index'))

        selectedImages = request.form.getlist('image')

    return render_template('admin/exhibition/create.html', form=form, selectedImages=json.dumps(selectedImages))

@blueprint.route("/update/<exhibition_id>", methods=['GET', 'POST'])
@login_required
def update(exhibition_id):
    form = forms.ExhibitionForm()
    exhibition = db.exhibitions.find_one({"_id": ObjectId(exhibition_id)})

    if form.is_submitted():
        form.artist.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]
        exhibition['images'] = [db.image.find_one({'_id': ObjectId(image_id)}) for image_id in request.form.getlist('image')]

        if form.validate_on_submit():
            formdata = form.data
            exhibition = utils.handle_form_data(exhibition, formdata, ['press_release_file'])
            exhibition['artist'] = db.artist.find_one({"_id": ObjectId(formdata['artist'])})

            db.exhibitions.update({"_id": ObjectId(exhibition_id)}, exhibition)

            if request.files['press_release_file']:
                exhibition['press_release'] = utils.handle_uploaded_file(
                    request.files['press_release_file'],
                    config.upload['PRESS_RELEASE'],
                    '{0}.pdf'.format(exhibition['slug'])
            )

            flash(u'You successfully updated the exhibition data', 'success')
            return redirect_flask(url_for('.index'))

    selectedImages = [str(image['_id']) for image in exhibition['images']]
    exhibition['artist'] = str(exhibition['artist']['_id'])
    form = forms.ExhibitionForm(data=exhibition)
    form.artist.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]


    return render_template('admin/exhibition/edit.html', form=form, selectedImages=json.dumps(selectedImages))

@blueprint.route("/delete/<exhibition_id>", methods=['GET', 'POST'])
@login_required
def delete(exhibition_id):
    if request.method == 'POST':
        print exhibition_id
        db.exhibitions.remove({"_id": ObjectId(exhibition_id)})
        flash(u'You deleted the exhibition', 'warning')
        return redirect_flask(url_for('.index'))

    return render_template('admin/exhibition/delete.html')

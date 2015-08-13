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

    if form.validate_on_submit():
        print 'Hello group exhibition?'
        formdata = form.data
        print formdata['artists']
        exhibition = utils.handle_form_data({}, formdata, ['press_release_file', 'artists'])
        exhibition['artists'] = [db.artist.find_one({'_id': ObjectId(artist_id)}) for artist_id in request.form.getlist('artists')]
        exhibition['slug'] = utils.slugify(exhibition['exhibition_name'])
        exhibition_md = form.wysiwig_exhibition_description.data
        exhibition['is_group_expo'] = True

        if request.files['press_release_file']:
            exhibition['press_release'] = utils.handle_uploaded_file(
                request.files['press_release_file'],
                config.upload['PRESS_RELEASE'],
                '{0}.pdf'.format(exhibition['slug'])
            )

        db.exhibitions.insert(exhibition)
        flash(u'You successfully created a group exhibition', 'success')
        return redirect_flask(url_for('.index'))

    return render_template('admin/group-exhibition/exhibitionCreate.html', form=form)

@blueprint.route("/update/<exhibition_id>", methods=['GET', 'POST'])
@login_required
def updateGroupExhibition(exhibition_id):
    exhibition = db.exhibitions.find_one({"_id": ObjectId(exhibition_id)})

    if request.method == 'POST':
        form = forms.GroupExhibitionForm()
        form.artists.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]

        if form.validate_on_submit():
            formdata = form.data
            artists = db.artist.find()
            exhibition = utils.handle_form_data(exhibition, formdata, ['press_release_file', 'artists'])
            exhibition['artists'] = [db.artist.find_one({'_id': ObjectId(artist_id)}) for artist_id in request.form.getlist('artists')]
            db.exhibitions.update({ "_id": ObjectId(exhibition_id) }, exhibition)

            if request.files['press_release_file']:
                exhibition['press_release'] = utils.handle_uploaded_file(
                    request.files['press_release_file'],
                    config.upload['PRESS_RELEASE'],
                    '{0}.pdf'.format(exhibition['slug'])
            )
        flash(u'You successfully updated the exhibition data', 'success')
        return redirect_flask(url_for('.index'))

    else:
#        exhibition['artists'] = [str(artist['_id']) for artist in exhibition['artists']]
        form = forms.GroupExhibitionForm(data=exhibition)
        form.artists.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]

    return render_template('admin/group-exhibition/exhibitionEdit.html', form=form)

@blueprint.route("/delete/<exhibition_id>", methods=['GET', 'POST'])
@login_required
def deleteGroupExhibition(exhibition_id):
    if request.method == 'POST':
        print exhibition_id
        db.exhibitions.remove({"_id": ObjectId(exhibition_id)})
        flash(u'You deleted the exhibition', 'warning')
        return redirect_flask(url_for('.index'))

    return render_template('admin/group-exhibition/exhibitionDelete.html')

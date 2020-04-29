#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python Standard Library
from flask import   Flask, flash, redirect as redirect_flask, \
                    render_template, url_for, request, \
                    abort, Response, session
from flask_pagedown import PageDown

import pymongo

from .. import utils
from bson import ObjectId
from bson.json_util import dumps as bson_dumps
import forms
from . import config
import re
import json

from ..utils import login_required

from ..settings import db

from flask import Blueprint, render_template, abort

blueprint = Blueprint('admin_artist', __name__)

@blueprint.route('/', methods=['GET'])
@login_required
def index():
    artists = db.artist.find().sort("artist_sort", 1)
    return render_template('admin/artist/index.html', artists=artists)

"""    
    Create artist method
    
"""
@blueprint.route('/create/', methods=['GET','POST'])
@login_required
def create():
    form = forms.ArtistForm()
    exhibitions = db.exhibitions.find()

    if request.method == 'POST':
        if form.validate():
            formdata = form.data
            artist = utils.handle_form_data({}, formdata, ['press_release', 'biography_file'])
            artist['slug'] = utils.slugify(artist['name'])

            if 'press_release' in request.files \
            and request.files['press_release']:
                uploaded_file = request.files['press_release']
                basepath = utils.setfilenameroot(uploaded_file.filename, artist['slug'])
                artist['press_release'] = utils.handle_uploaded_file(uploaded_file, config.upload['PRESS_RELEASE'], basepath)
                artist['press_release_size'] = utils.getfilesize(artist['press_release'])

            if 'biography_file' in request.files \
            and request.files['biography_file']:
                uploaded_file = request.files['biography_file']
                basepath = utils.setfilenameroot(uploaded_file.filename, artist['slug'])
                artist['biography_file'] = utils.handle_uploaded_file(uploaded_file, config.upload['BIOGRAPHY'], basepath)
                artist['biography_size'] = utils.getfilesize(artist['biography_file'])

            if 'coverimage' in request.files:
                uploaded_image = request.files.getlist('coverimage')[0]
                basepath = utils.setfilenameroot(uploaded_image.filename, artist['slug'])
                artist['coverimage'] = { 'path': utils.handle_uploaded_file(uploaded_image, config.upload['COVER_IMAGE'], basepath) }

            artist['images'] = []
            artist['views'] = []
            artist['selected_images'] = []
            
            uploaded_views = request.files.getlist('views')
            uploaded_images = request.files.getlist('images')            
            
            # Go through added images. Should only be uploaded images
            if 'images' in request.form:
                for image_name in request.form.getlist('images'):
                    if image_name and image_name.find('uploaded:') > -1:
                        index = int(re.search(':(\d+)$', image_name).group(1))
                        
                        if image_name.find(':artwork:') > -1:
                            # image is an artwork
                            image_path = utils.handle_uploaded_file(
                                uploaded_images[index],
                                config.upload['ARTWORK_IMAGE'],
                                utils.setfilenameroot(uploaded_images[index].filename, artist['slug'])
                            )
                            
                            image = { '_id': ObjectId(), 'path': image_path }
                            artist['images'].append(image)
                        
                        else:
                            # image is a view
                            image_path = utils.handle_uploaded_file(
                                uploaded_views[index],
                                config.upload['EXTERNAL_EXHIBITION_VIEW'],
                                utils.setfilenameroot(uploaded_views[index].filename, artist['slug'])
                            )
                            
                            image = { '_id': ObjectId(), 'path': image_path }
                            artist['views'].append(image)
                        
                        artist['selected_images'].append(image)
            
            db.artist.insert(artist)
            flash('You successfully created an artist page', 'success')

            if (request.is_xhr):
                return bson_dumps(artist), 201

            else:
                return redirect_flask(url_for('.index'))

        elif (request.is_xhr):
            # Invalid and xhr, return the errors, rather than full HTML
            return json.dumps(form.errors), 400

    return render_template('admin/artist/create.html',
                                form=form,
                                exhibitions=exhibitions,
                                selected_images=[],
                                images=[]
                          )

"""    
    Update artist method
    
"""
@blueprint.route('/update/<artist_id>', methods=['GET', 'POST'])
@login_required
def update(artist_id):
    artist = db.artist.find_one({"_id": ObjectId(artist_id)})
    
    # All the images 
    available_images = [image for image in artist['images']]
    
    for image in artist['views']:
        if image and not utils.find_where('_id', image['_id'], available_images):
                available_images.append(image)

    # Find all exhibitions this artist participates in
    exhibitions = db.exhibitions.find({
        "$or": [
            {'artist._id': artist['_id']},
            {'artists._id': artist['_id']}
        ]
    })

    for exhibition in exhibitions:
        for image in exhibition['images']:
            if image and not utils.find_where('_id', image['_id'], available_images):
                available_images.append(image)

    if request.method == 'POST':
        form = forms.ArtistForm()

        if form.validate_on_submit():
            formdata = form.data
            artist =  utils.handle_form_data(artist, formdata, ['press_release', 'biography_file'])

            if 'press_release' in request.files \
            and request.files['press_release']:
                uploaded_file = request.files['press_release']
                basepath = utils.setfilenameroot(uploaded_file.filename, artist['slug'])
                artist['press_release'] = utils.handle_uploaded_file(uploaded_file, config.upload['PRESS_RELEASE'], basepath)
                artist['press_release_size'] = utils.getfilesize(artist['press_release'])
            elif 'press_release' not in request.form \
            and 'press_release' in artist:
                del artist['press_release']

            if 'biography_file' in request.files \
            and request.files['biography_file']:
                uploaded_file = request.files['biography_file']
                basepath = utils.setfilenameroot(uploaded_file.filename, artist['slug'])
                artist['biography_file'] = utils.handle_uploaded_file(uploaded_file, config.upload['BIOGRAPHY'], basepath)
                artist['biography_size'] = utils.getfilesize(artist['biography_file'])
            elif 'biography_file' not in request.form \
                and 'biography_file' in artist:
                    del artist['biography_file']

            if 'coverimage' in request.files:
                uploaded_image = request.files.getlist('coverimage')[0]
                basepath = utils.setfilenameroot(uploaded_image.filename, artist['slug'])
                artist['coverimage'] = { 'path': utils.handle_uploaded_file(uploaded_image, config.upload['COVER_IMAGE'], basepath) }
            elif 'coverimage' not in request.form:
                if 'coverimage' in artist:
                    del artist['coverimage']

            # Construct an array to fill with uploaded images
            uploaded_images = []
            uploaded_views = []
           
            if 'images' in request.files:
                for uploaded_image in request.files.getlist('images'):
                    image_path = utils.handle_uploaded_file(
                        uploaded_image,
                        config.upload['ARTWORK_IMAGE'],
                        utils.setfilenameroot(uploaded_image.filename, artist['slug'])
                    )
                    
                    image = { '_id': ObjectId(), 'path': image_path }
                    artist['images'].append(image)
                    uploaded_images.append(image)

            if 'views' in request.files:
                for uploaded_image in request.files.getlist('views'):
                    image_path = utils.handle_uploaded_file(
                        uploaded_image,
                        config.upload['EXTERNAL_EXHIBITION_VIEW'],
                        utils.setfilenameroot(uploaded_image.filename, artist['slug'])
                    )
                    
                    image = { '_id': ObjectId(), 'path': image_path }
                    artist['views'].append(image)
                    uploaded_views.append(image)

            artist['selected_images'] = []
            
            if 'images' in request.form:
                # Find all the selected images
                for path in request.form.getlist('images'):
                    if path.find('uploaded:') > -1:
                        index = int(re.search(':(\d+)$', path).group(1))
                        # uploaded image
                        if path.find(':artwork:') > -1:
                            # artwork
                            artist['selected_images'].append(uploaded_images[index])
                        else:
                            # external view
                            artist['selected_images'].append(uploaded_views[index])
                    else:
                        image = utils.find_where('path', path, available_images)
                                                 
                        if image:
                            artist['selected_images'].append(image)

            db.artist.update({"_id": ObjectId(artist_id)}, artist)
            # Update this artist on exhibitions as well
            db.exhibitions.update({"artist._id": ObjectId(artist_id)}, {"$set": { "artist": artist }}, multi=True)
            # Should update this artist on group exhibitions as well
            db.exhibitions.update({"artists._id": ObjectId(artist_id)}, {"$set": {"artists.$": artist}}, multi=True)

            flash('You\'ve updated the artist page successfully', 'success')

            if request.is_xhr:
                return bson_dumps(artist), 201
            else:
                return redirect_flask(url_for('.index'))
        else:
            # Invalid
            if request.is_xhr:
                return json.dumps(form.errors), 400
            else:
                return render_template('admin/artist/edit.html',
                            form=form,
                            images=utils.prepare_images(available_images),
                            selected_images=utils.prepare_images(artist['selected_images'] if 'selected_images' in artist else []),
                            exhibitions=exhibitions,
                            coverimage=[artist['coverimage']] if 'coverimage' in artist else [])


    else:
        form = forms.ArtistForm(data=artist)

    return render_template('admin/artist/edit.html',
                                form=form,
                                images=utils.prepare_images(available_images),
                                selected_images=utils.prepare_images(artist['selected_images'] if 'selected_images' in artist else []),
                                exhibitions=exhibitions,
                                coverimage=[artist['coverimage']] if 'coverimage' in artist else [])


@blueprint.route('/delete/<artist_id>', methods=['GET', 'POST'])
@login_required
def deleteArtist(artist_id):
    if request.method == 'POST':
        db.artist.remove({"_id": ObjectId(artist_id)})
        flash('You deleted the artist page', 'warning')
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
    ## Update this artist on exhibitions as well
    db.exhibitions.update({"artist._id": ObjectId(artist_id)}, {"$set": { "artist.is_published": is_published }}, multi=True)
    ## Should update this artist on group exhibitions as well
    db.exhibitions.update({"artists._id": ObjectId(artist_id)}, {"$set": {"artists.$.is_published": is_published}}, multi=True);

    return bson_dumps(db.artist.find_one({'_id': ObjectId(artist_id)}))

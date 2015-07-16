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
                    abort, Response
from flask_pagedown import PageDown
from flask.ext.misaka import Misaka

import pymongo
#import admin

import utils
from bson import ObjectId
from bson.json_util import dumps
import forms

import json

# Local imports
# from settings import *

app = Flask(__name__)
pagedown = PageDown(app)
Misaka(app)
app.secret_key = "@My*C7KNeC@74#HC$F7FkpEEmECaZ@jH#ePwwz#Fo^#T3%(!bM^xSAG^&!#x*i#*"

client = pymongo.MongoClient()
db = client.artlogic

app.config['UPLOAD'] = {
    'PRESS_RELEASE': {
        'allowed_extensions': ['pdf'],
        'upload_folder': 'static/uploads/press/'
    },

    'ARTWORK_IMAGE': {
        'allowed_extensions': ['png', 'jpeg', 'jpg', 'gi'],
        'upload_folder': 'static/uploads/artworks/'
    }
}

# login decorator

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == 'secret'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Your login is required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


####################################################################################

### PUBLIC VIEWS ###

####################################################################################

@app.route("/test/")
@requires_auth
def test():
    return render_template("front/tests.html")

@app.route("/")
def home():
    artworks = db.artworks.find().sort("id", -1).limit(10)
    exhibition = db.exhibitions.find().limit(2)
    return render_template("front/current.html", exhibition=exhibition)

@app.route("/past/")
def pastExhibitions():
    exhibition = db.exhibitions.find()
    date = db.exhibitions.find()
    return render_template("front/past.html", exhibition=exhibition, date=date)

@app.route("/artists/")
def artists():
    artists = db.artist.find()
    return render_template("front/artists.html", artists=artists)

@app.route("/artist/<slug>/")
def artist(slug):
    artist = db.artist.find_one({ "slug": slug})
    #artworks = db.artworks.find({"artist": artist["artist"]}).sort("id", -1).limit(10)
    return render_template("front/artist.html", artist=artist)

@app.route("/current/")
def current():
    current_exhibition = db.exhibitions.find()#.limit(2)
    return render_template("front/current.html", current_exhibition=current_exhibition)

@app.route("/current/<slug>/")
def exhibition(slug):
    exhibition = db.exhibition.find_one({ "slug": slug})
    return render_template("front/exhibition.html")

@app.route("/exhibition/<slug>/")
def publicviewExhibition(slug):
    exhibition = db.exhibitions.find_one({'slug': slug})

    if exhibition <> None:
        return render_template('front/exhibition.html', exhibition=exhibition)
    else:
        abort(404)

@app.route("/gallery/")
def GalleryInfo():
    teammembers = db.teammember.find()
    openinghours = db.openinghours.find()

    return render_template('front/gallery.html', teammembers=teammembers, openinghours=openinghours)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

####################################################################################

### ADMIN FUNCTIONALITY ###

####################################################################################

@app.route("/admin/")
def viewAdmin():
    flash('we still need to make a login method')
    return render_template('admin.html')

### single artist exhibition ###
@app.route("/admin/exhibitions/")
def viewExhibition():
    exhibitions = db.exhibitions.find()
    return render_template('admin/exhibition/exhibitions.html', exhibitions=exhibitions)

@app.route("/admin/exhibition/publish/<exhibition_id>", methods=['POST'])
def publishExhibition (exhibition_id):
    from time import sleep
    sleep(.5)
    is_published = ('true' == request.form['is_published'])
    db.exhibitions.update(
        {'_id': ObjectId(exhibition_id)},
        {'$set': {'is_published': is_published}}
    )
    return dumps(db.exhibitions.find_one({'_id': ObjectId(exhibition_id)}))

@app.route("/admin/exhibition/create/", methods=['GET', 'POST'])
def createExhibition():
    form = forms.ExhibitionForm()
    form.artist.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]
    print form.artist.choices

    AL_artworks = db.AL_artworks.find().limit(10)

    if form.validate_on_submit():
        formdata = form.data
        exhibition = utils.handle_form_data({}, formdata, ['press_release_file'])
        exhibition['slug'] = utils.slugify(exhibition['exhibition_name'])
        exhibition_md = form.wysiwig_exhibition_description.data
        artist_md = form.wysiwig_artist_bio.data

        if request.files['press_release_file']:
            exhibition['press_release'] = utils.handle_uploaded_file(
                request.files['press_release_file'],
                app.config['UPLOAD']['PRESS_RELEASE'],
                '{0}.pdf'.format(exhibition['slug'])
            )

        db.exhibitions.insert(exhibition)
        flash('You successfully created an exhibition')
        return redirect_flask(url_for('viewExhibition'))

    return render_template('admin/exhibition/exhibitionCreate.html', form=form, AL_artworks=AL_artworks)

@app.route("/admin/exhibition/update/<exhibition_id>", methods=['GET', 'POST'])
def updateExhibition(exhibition_id):
    exhibition = db.exhibitions.find_one({"_id": ObjectId(exhibition_id)})

    if request.method == 'POST':
        form = forms.ExhibitionForm()
        form.artist.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]

        if form.validate_on_submit():
            formdata = form.data
            db.exhibitions.update(
            {
                "_id": ObjectId(exhibition_id)
            },
            utils.handle_form_data(exhibition, formdata, ['press_release_file']),
            upsert=True
            )

            if request.files['press_release_file']:
                exhibition['press_release'] = utils.handle_uploaded_file(
                    request.files['press_release_file'],
                    app.config['UPLOAD']['PRESS_RELEASE'],
                    '{0}.pdf'.format(exhibition['slug'])
            )
        flash('You successfully updated the exhibition data')
        return redirect_flask(url_for('viewExhibition'))

    else:
        form = forms.ExhibitionForm(data=exhibition)
        form.artist.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]

    return render_template('admin/exhibition/exhibitionEdit.html', form=form)

@app.route("/admin/exhibition/delete/<exhibition_id>", methods=['GET', 'POST'])
def deleteExhibition(exhibition_id):
    if request.method == 'POST':
        print exhibition_id
        db.exhibitions.remove({"_id": ObjectId(exhibition_id)})
        flash('You deleted the exhibition')
        return redirect_flask(url_for('viewExhibition'))

    return render_template('admin/exhibition/exhibitionDelete.html')

### group exhibition ###

@app.route("/admin/group-exhibition/create/", methods=['GET', 'POST'])
def createGroupExhibition():
    form = forms.GroupExhibitionForm()
    form.artists.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]
    print form.artists.choices

    AL_artworks = db.AL_artworks.find().limit(10)

    if form.validate_on_submit():
        formdata = form.data
        exhibition = utils.handle_form_data({}, formdata, ['press_release_file'])
        exhibition['slug'] = utils.slugify(exhibition['exhibition_name'])
        exhibition_md = form.wysiwig_exhibition_description.data
        exhibition['is_group_expo'] = True

        if request.files['press_release_file']:
            exhibition['press_release'] = utils.handle_uploaded_file(
                request.files['press_release_file'],
                app.config['UPLOAD']['PRESS_RELEASE'],
                '{0}.pdf'.format(exhibition['slug'])
            )

        db.exhibitions.insert(exhibition)
        flash('You successfully created a group exhibition')
        return redirect_flask(url_for('viewExhibition'))

    return render_template('admin/group-exhibition/exhibitionCreate.html', form=form, AL_artworks=AL_artworks)

@app.route("/admin/group-exhibition/update/<exhibition_id>", methods=['GET', 'POST'])
def updateGroupExhibition(exhibition_id):
    exhibition = db.exhibitions.find_one({"_id": ObjectId(exhibition_id)})

    if request.method == 'POST':
        form = forms.GroupExhibitionForm()
        form.artists.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]

        if form.validate_on_submit():
            formdata = form.data
            db.exhibitions.update(
            {
                "_id": ObjectId(exhibition_id)
            },
            utils.handle_form_data(exhibition, formdata, ['press_release_file']),
            upsert=True
            )

            if request.files['press_release_file']:
                exhibition['press_release'] = utils.handle_uploaded_file(
                    request.files['press_release_file'],
                    app.config['UPLOAD']['PRESS_RELEASE'],
                    '{0}.pdf'.format(exhibition['slug'])
            )
        flash('You successfully updated the exhibition data')
        return redirect_flask(url_for('viewExhibition'))

    else:
        form = forms.GroupExhibitionForm(data=exhibition)
        form.artists.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]

    return render_template('admin/group-exhibition/exhibitionEdit.html', form=form)

@app.route("/admin/group-exhibition/delete/<exhibition_id>", methods=['GET', 'POST'])
def deleteGroupExhibition(exhibition_id):
    if request.method == 'POST':
        print exhibition_id
        db.exhibitions.remove({"_id": ObjectId(exhibition_id)})
        flash('You deleted the exhibition')
        return redirect_flask(url_for('viewExhibition'))

    return render_template('admin/group-exhibition/exhibitionDelete.html')

### artists ###
@app.route("/admin/artist/")
def listArtists():
    artists = db.artist.find()
    return render_template('admin/artists/artists.html', artists=artists)

@app.route("/admin/artist/publish/<artist_id>", methods=['POST'])
def publishArtist (artist_id):
    is_published = ('true' == request.form['is_published'])
    db.artist.update(
        {'_id': ObjectId(artist_id)},
        {'$set': {'is_published': is_published}}
    )
    return dumps(db.artist.find_one({'_id': ObjectId(artist_id)}))

@app.route("/admin/artist/create/", methods=['GET', 'POST'])
def artistCreate():
    form = forms.ArtistForm()

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
        return redirect_flask(url_for('listArtists'))

    return render_template('admin/artists/artistCreate.html', form=form)

@app.route("/admin/artist/update/<artist_id>", methods=['GET', 'POST'])
def updateArtist(artist_id):
    artist = db.artist.find_one({"_id": ObjectId(artist_id)})
    images = db.image.find({"artist": artist})

    if request.method == 'POST':
        form = forms.ArtistForm()

        if form.validate_on_submit():
            formdata = form.data
            db.artist.update(
            {
                "_id": ObjectId(artist_id)
            },
            utils.handle_form_data(artist, formdata, ['press_release_file']),
            upsert=True
            )

            if request.files['press_release_file']:
                artist['press_release'] = utils.handle_uploaded_file(
                    request.file['press_release_file'],
                    app.config['UPLOAD']['PRESS_RELEASE'],
                    '{0}.pdf'.format(artists['slug'])
                )
            flash('You updated the artist page successfully')
            return redirect_flask(url_for('listArtists'))

    else:
        form = forms.ArtistForm(data=artist)

    return render_template('admin/artists/artistEdit.html', form=form, images=images)

@app.route("/admin/artist/delete/<artist_id>", methods=['GET', 'POST'])
def deleteArtist(artist_id):
    if request.method == 'POST':
        print artist_id
        db.artist.remove({"_id": ObjectId(artist_id)})
        flash('You deleted the artist page')
        return redirect_flask(url_for('listArtists'))

    return render_template('admin/artists/artistDelete.html')

### gallery general ###
@app.route("/admin/manage-gallery-info/", methods=['GET', 'POST'])
def adminGalleryInfo():
    return render_template('admin/gallery/gallery.html')

### team members ###
@app.route("/admin/manage-gallery-teammembers/")
def listTeamMembers():
    form = forms.GalleryEmployees()
    teammember = db.teammember.find()

    return render_template('admin/gallery/teammembers/galleryTeamMember.html', form=form, teammember=teammember)

@app.route("/admin/edit-gallery-teammembers/", methods=['GET', 'POST'])
def createTeamMember():
    form = forms.GalleryEmployees()

    if form.validate_on_submit():
        formdata = form.data
        teammember = utils.handle_form_data({}, formdata)
        teammember['slug'] = utils.slugify(teammember['name'])
        db.teammember.insert(teammember)
        flash('You successfully created a new team member')
        return redirect_flask(url_for('listTeamMembers'))

    return render_template('admin/gallery/teammembers/galleryTeamMemberCreate.html', form=form)

@app.route("/admin/edit-gallery-teammembers/<teammember_id>", methods=['GET', 'POST'])
def updateTeamMembers(teammember_id):
    teammember = db.teammember.find_one({"_id": ObjectId(teammember_id)})

    if request.method == 'POST':
        form = forms.GalleryEmployees()

        if form.validate_on_submit():
            formdata = form.data
            db.teammember.update(
            {
                "_id": ObjectId(teammember_id)
            },
            utils.handle_form_data(teammember, formdata),
            upsert=True
        )
        flash('You successfully updated the team member entry')
        return redirect_flask(url_for('listTeamMembers'))

    else:
        form = forms.GalleryEmployees(data=teammember)

    return render_template('admin/gallery/teammembers/galleryTeamMemberEdit.html', form=form, teamMemberId=teammember_id)

@app.route("/admin/delete-gallery-teammembers/<teammember_id>", methods=['GET', 'POST'])
def deleteTeamMembers(teammember_id):
    if request.method == 'POST':
        print teammember_id
        db.teammember.remove({"_id": ObjectId(teammember_id)})
        flash('You deleted the team member')
        return redirect_flask(url_for('listTeamMembers'))

    return render_template('admin/gallery/teammembers/galleryTeamMemberDelete.html')

### opening hours ###
@app.route("/admin/manage-opening-hours/")
def listOpeningHours():
    form = forms.GalleryHours()
    openinghours = db.openinghours.find()

    return render_template('admin/gallery/openinghours/galleryOpeningHours.html', openinghours=openinghours, form=form)

@app.route("/admin/edit-opening-hours/", methods=['GET', 'POST'])
def createOpeningHours():
    form = forms.GalleryHours()

    if form.validate_on_submit():
        formdata = form.data
        openinghour = utils.handle_form_data({}, formdata)
        db.openinghours.insert(openinghour)
        flash('You successfully created the opening hour entry')
        return redirect_flask(url_for('listOpeningHours'))

    return render_template('admin/gallery/openinghours/galleryOpeningHoursCreate.html', form=form)

@app.route("/admin/edit-opening-hours/<opening_hour_id>", methods=['GET', 'POST'])
def updateOpeningHours(opening_hour_id):
    opening_hour = db.openinghours.find_one({"_id": ObjectId(opening_hour_id)})

    if request.method == 'POST':
        form = forms.GalleryHours()

        if form.validate_on_submit():
            formdata = form.data
            db.openinghours.update(
                {
                    "_id": ObjectId(opening_hour_id)
                },
                utils.handle_form_data(opening_hour, formdata),
                upsert=True
            )
            flash('You successfully updated the opening hour entry')
            return redirect_flask(url_for('listOpeningHours'))
    else:
        form = forms.GalleryHours(data=opening_hour)

    return render_template('admin/gallery/openinghours/galleryOpeningHoursEdit.html', form=form, galleryHoursId=opening_hour_id)

@app.route("/admin/delete-opening-hours/<opening_hour_id>", methods=['GET', 'POST'])
def deleteOpeningHours(opening_hour_id):
    if request.method == 'POST':
        print opening_hour_id
        db.openinghours.remove({"_id": ObjectId(opening_hour_id)})
        flash('You successfully deleted the opening hour entry')
        return redirect_flask(url_for('listOpeningHours'))

    return render_template('admin/gallery/openinghours/galleryOpeningHoursDelete.html')

### Images ###
@app.route("/admin/manage-images/")
def listImages():
    form = forms.Image()
    form.artist.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]
    images = db.image.find()

    return render_template('admin/images/list.html', images=images, form=form)

@app.route("/admin/edit-image/", methods=['GET', 'POST'])
def createImage():
    form = forms.Image()
    form.artist.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]

    if form.validate_on_submit():
        formdata = form.data
        image = {
            'artist': db.artist.find_one({'_id': ObjectId(formdata['artist'])}),
            'path': utils.handle_uploaded_file(
                request.files['image_file'],
                app.config['UPLOAD']['ARTWORK_IMAGE']
            )
        }
        db.image.insert(image)

        return redirect_flask(url_for('listImages'))

    return render_template('admin/images/create.html', form=form)

#@app.route("/admin/edit-i/<opening_hour_id>", methods=['GET', 'POST'])
#def updateOpeningHours(opening_hour_id):
    #opening_hour = db.openinghours.find_one({"_id": ObjectId(opening_hour_id)})

    #if request.method == 'POST':
        #form = forms.GalleryHours()

        #if form.validate_on_submit():
            #formdata = form.data
            #db.openinghours.update(
                #{
                    #"_id": ObjectId(opening_hour_id)
                #},
                #utils.handle_form_data(opening_hour, formdata),
                #upsert=True
            #)
            #flash('You successfully updated the opening hour entry')
            #return redirect_flask(url_for('listOpeningHours'))
    #else:
        #form = forms.GalleryHours(data=opening_hour)

    #return render_template('admin/gallery/openinghours/galleryOpeningHoursEdit.html', form=form, galleryHoursId=opening_hour_id)

@app.route("/admin/delete-image/<image_id>", methods=['GET', 'POST'])
def deleteImage(image_id):
    if request.method == 'POST':
        image = db.image.find_one({"_id": ObjectId(image_id)})
        os.remove(image['path'])
        db.image.remove({"_id": ObjectId(image_id)})
        flash('You successfully deleted the image')
        return redirect_flask(url_for('listImages'))

    return render_template('admin/images/delete.html')


"""
    Returns JSON-array with images for given artist. Or 404
"""
@app.route("/admin/images/list/<artist_id>", methods=['GET'])
def listImagesForArtist(artist_id):
    artist = db.artist.find_one({"_id": ObjectId(artist_id)})
    if artist:
        images = db.image.find({'artist': artist})
        return dumps(images)
    else:
        abort(404)

"""
    Direct upload function. Stores given image in the artist images
    store location. Returns JSON DB-entry
"""
@app.route("/admin/uploadArtistImage/<artist_id>", methods=['POST'])
def uploadArtistImage(artist_id):
    formdata = form.data
    artist = db.artist.find_one({'_id': ObjectId(formdata['artist'])})

    if artist:
        image = {
            'artist': artist,
            'path': utils.handle_uploaded_file(
                request.files['image_file'],
                app.config['UPLOAD']['ARTWORK_IMAGE']
            )
        }

        db.image.insert(image)

        return json.dumps(image)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

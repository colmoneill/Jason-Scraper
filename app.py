#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python Standard Library
import os
from datetime import datetime

# Dependencies: Flask + PIL or Pillowexhibition/create/
from flask import   Flask, flash, send_from_directory, \
                    redirect as redirect_flask, \
                    render_template, url_for, request, \
                    abort
from flask_pagedown import PageDown

import pymongo
#import admin

import utils
from bson import ObjectId
import forms

# Local imports
# from settings import *

app = Flask(__name__)
pagedown = PageDown(app)
app.secret_key = "@My*C7KNeC@74#HC$F7FkpEEmECaZ@jH#ePwwz#Fo^#T3%(!bM^xSAG^&!#x*i#*"

client = pymongo.MongoClient()
db = client.artlogic

app.config['UPLOAD'] = {
    'PRESS_RELEASE': {
        'allowed_extensions': ['pdf'],
        'upload_folder': 'static/uploads/press/'
    }
}

####################################################################################

### PUBLIC VIEWS ###

####################################################################################

@app.route("/test/")
def test():
    return render_template("front/tests.html")

@app.route("/")
def home():
    artworks = db.artworks.find().sort("id", -1).limit(10)
    exhibition = db.exhibition.find()
    current_exhibition = db.exhibitions.find() #.limit(2)
    return render_template("front/current.html", current_exhibition=current_exhibition)

@app.route("/artists/")
def artists():
    artists = db.artists.find().sort("artist_sort", 1)
    return render_template("front/artists.html", artists=artists)

@app.route("/artists/<slug>/")
def artist(slug):
    artist = db.artists.find_one({ "slug": slug})
    artworks = db.artworks.find({"artist": artist["artist"]}).sort("id", -1).limit(10)
    return render_template("front/artist.html", artist=artist, artworks=artworks)

@app.route("/current/")
def current():
    current_exhibition = db.exhibitions.find()#.limit(2)
    return render_template("front/current.html", current_exhibition=current_exhibition)

@app.route("/current/<slug>/")
def exhibition(slug):
    exhibition = db.exhibition.find_one({ "slug": slug})
    return render_template("front/exhibition.html")

# Deprecated?
@app.route('/exhibition', methods=['GET', 'POST'])
def adminexhibition():
    artists = db.artists.find().sort("artist_sort", 1)
    all_exhibitions = db.exhibition.find()
    exhibition = None
    new = False
    if request.method == 'POST' and 'exhibition' in request.form:
        exhibition = request.form['exhibition']
        if db.exhibition.find_one({'exhibition': exhibition}) is None:
            # this is a new exhibition, add it to the database
            db.exhibition.insert({'exhibition': exhibition})
            new = True


    return render_template('front/exhibition.html', exhibition=exhibition, allexhibition=allexhibition, artists=artists, new=new)

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
####################################################################################

### ADMIN FUNCTIONALITY ###

####################################################################################

@app.route("/admin/")
def viewAdmin():
    flash('we still need to make a login method')
    return render_template('admin.html')

### exhibitions general ###
@app.route("/admin/exhibitions/")
def viewExhibition():
    form = forms.ExhibitionForm()
    exhibition = db.exhibitions.find()

    return render_template('admin/exhibition/exhibitions.html', exhibition=exhibition)

@app.route("/admin/exhibition/create/", methods=['GET', 'POST'])
def createExhibition():
    form = forms.ExhibitionForm()

    if form.validate_on_submit():
        formdata = form.data
        exhibition = utils.handle_form_data({}, formdata, ['press_release_file'])
        exhibition['slug'] = utils.slugify(exhibition['name'])

        if request.files['press_release_file']:
            exhibition['press_release'] = utils.handle_uploaded_file(
                request.files['press_release_file'],
                app.config['UPLOAD']['PRESS_RELEASE'],
                '{0}.pdf'.format(exhibition['slug'])
            )

        db.exhibitions.insert(exhibition)
        flash('You successfully created an exhibition')
        return redirect_flask(url_for('viewExhibition'))

    return render_template('admin/exhibition/exhibitionCreate.html', form=form)

@app.route("/admin/exhibition/update/<exhibition_id>", methods=['GET', 'POST'])
def updateExhibition(exhibition_id):
    exhibition = db.exhibitions.find_one({"_id": ObjectId(exhibition_id)})

    if request.method == 'POST':
        form = forms.ExhibitionForm()

        if form.validate_on_submit():
            formdata = form.data
            db.exhibitions.update(
            {
                "_id": ObjectId(exhibition_id)
            },
            utils.handle_form_data(exhibition, formdata, ['press_release_file']),
            upsert=True
        )
        flash('You successfully updated the exhibition data')
        return redirect_flask(url_for('viewExhibition'))

    else:
        form = forms.ExhibitionForm(data=exhibition)

    return render_template('admin/exhibition/exhibitionEdit.html', form=form, singleExhibitionId=exhibition_id)

@app.route("/admin/exhibition/delete/<exhibition_id>", methods=['GET', 'POST'])
def deleteExhibition(exhibition_id):
    if request.method == 'POST':
        print exhibition_id
        db.exhibitions.remove({"_id": ObjectId(exhibition_id)})
        flash('You deleted the exhibition')
        return redirect_flask(url_for('viewExhibition'))

    return render_template('admin/exhibition/exhibitionDelete.html')


@app.route("/admin/artist/")
def listArtists():
    artist = db.artist.find()
    return render_template('admin/artists/artists.html', artist=artist)

@app.route("/admin/artist-create/")
def artistCreate():
    form = forms.artistCreate()

    if form.validate_on_submit():
        artist = form.data
        artist['slug'] = utils.slugify(artist['name'])
        db.artist.insert(artist)
        return redirect_flask(url_for('listArtists'))
    return render_template('admin/artists/artists.html', form=form)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

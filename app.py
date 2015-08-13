#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python Standard Library
import os
from datetime import datetime, date

# Dependencies: Flask + PIL or Pillowexhibition/create/
from functools import wraps
from flask import   Flask, flash, send_from_directory, \
                    redirect as redirect_flask, \
                    render_template, url_for, request, \
                    abort, Response, session
from flask_pagedown import PageDown
from flask.ext.misaka import Misaka

import pymongo

import utils
from utils import login_required
from bson import ObjectId
from bson.json_util import dumps
import forms

import json

from app import admin as admin

# Local imports
# from settings import *

app = Flask(__name__)
pagedown = PageDown(app)
Misaka(app)
app.secret_key = "g\xd4\xb0\x10\xa5.\x91\r\xf374\xbc3\x87#\x07\x0bEtM\x1a\x86R\x1c-}\xdc\x86N7\xf7\xcf"

client = pymongo.MongoClient()
db = client.artlogic

app.config['UPLOAD'] = {
    'PRESS_RELEASE': {
        'allowed_extensions': ['pdf'],
        'upload_folder': 'static/uploads/press/'
    },

    'ARTWORK_IMAGE': {
        'allowed_extensions': ['png', 'jpeg', 'jpg', 'gif'],
        'upload_folder': 'static/uploads/artworks/'
    }
}



@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    flash(u'You are logged out', 'warning')
    return redirect_flask(url_for('login'))

def validate_credentials(username=False, password=False):
    from users import users

    if username in users and users[username] == password:
        return True

    return False

@app.route("/login", methods=['GET', 'POST'])
def login():
    error = None
    form = forms.Login()
    if form.is_submitted():
        if validate_credentials(username=form.username.data, password=form.password.data):
            session['logged_in'] = True
            flash(u'You are logged in! Welcome', 'success')

            return redirect_flask(url_for('viewAdmin'))
        else:
            flash(u'Invalid credentials; Please try again.', 'danger')
    return render_template('login.html', error=error, form=form)


####################################################################################

### PUBLIC VIEWS ###

####################################################################################

@app.route("/")
def home():
    artworks = db.artworks.find().sort("id", -1).limit(10)
    exhibition = db.exhibitions.find({
        "is_published": True,
        "end": { "$gte": datetime.combine(date.today(), datetime.min.time()) }
    })
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
    exhibition = db.exhibitions.find() #.limit(2)
    return render_template("front/current.html", exhibition=exhibition)

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
@login_required
def viewAdmin():
    flash(u'You are logged in!', 'success')
    return render_template('admin.html')

### group exhibition ###

@app.route("/admin/group-exhibition/create/", methods=['GET', 'POST'])
@login_required
def createGroupExhibition():
    form = forms.GroupExhibitionForm()
    form.artists.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]

    if form.validate_on_submit():
        formdata = form.data
        print formdata['artists']
        exhibition = utils.handle_form_data({}, formdata, ['press_release_file', 'artists'])
        exhibition['artists'] = [db.artist.find_one({'_id': ObjectId(artist_id)}) for artist_id in formdata['artists']]
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
        flash(u'You successfully created a group exhibition', 'success')
        return redirect_flask(url_for('viewExhibition'))

    return render_template('admin/group-exhibition/exhibitionCreate.html', form=form)

@app.route("/admin/group-exhibition/update/<exhibition_id>", methods=['GET', 'POST'])
def updateGroupExhibition(exhibition_id):
    exhibition = db.exhibitions.find_one({"_id": ObjectId(exhibition_id)})

    if request.method == 'POST':
        form = forms.GroupExhibitionForm()
        form.artists.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]

        if form.validate_on_submit():
            formdata = form.data
            exhibition = utils.handle_form_data(exhibition, formdata, ['press_release_file', 'artists'])
            exhibition['artists'] = [db.artist.find_one({'_id': ObjectId(artist_id)}) for artist_id in formdata['artists']]
            db.exhibitions.update({ "_id": ObjectId(exhibition_id) }, exhibition)

            if request.files['press_release_file']:
                exhibition['press_release'] = utils.handle_uploaded_file(
                    request.files['press_release_file'],
                    app.config['UPLOAD']['PRESS_RELEASE'],
                    '{0}.pdf'.format(exhibition['slug'])
            )
        flash(u'You successfully updated the exhibition data', 'success')
        return redirect_flask(url_for('viewExhibition'))

    else:
        exhibition['artists'] = [str(artist['_id']) for artist in exhibition['artists']]
        form = forms.GroupExhibitionForm(data=exhibition)
        form.artists.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]

    return render_template('admin/group-exhibition/exhibitionEdit.html', form=form)

@app.route("/admin/group-exhibition/delete/<exhibition_id>", methods=['GET', 'POST'])
@login_required
def deleteGroupExhibition(exhibition_id):
    if request.method == 'POST':
        print exhibition_id
        db.exhibitions.remove({"_id": ObjectId(exhibition_id)})
        flash(u'You deleted the exhibition', 'warning')
        return redirect_flask(url_for('viewExhibition'))

    return render_template('admin/group-exhibition/exhibitionDelete.html')

### gallery general ###
@app.route("/admin/manage-gallery-info/", methods=['GET', 'POST'])
@login_required
def adminGalleryInfo():
    return render_template('admin/gallery/gallery.html')

### team members ###
@app.route("/admin/manage-gallery-teammembers/")
@login_required
def listTeamMembers():
    form = forms.GalleryEmployees()
    teammember = db.teammember.find()

    return render_template('admin/gallery/teammembers/galleryTeamMember.html', form=form, teammember=teammember)

@app.route("/admin/edit-gallery-teammembers/", methods=['GET', 'POST'])
@login_required
def createTeamMember():
    form = forms.GalleryEmployees()

    if form.validate_on_submit():
        formdata = form.data
        teammember = utils.handle_form_data({}, formdata)
        teammember['slug'] = utils.slugify(teammember['name'])
        db.teammember.insert(teammember)
        flash(u'You successfully created a new team member', 'success')
        return redirect_flask(url_for('listTeamMembers'))

    return render_template('admin/gallery/teammembers/galleryTeamMemberCreate.html', form=form)

@app.route("/admin/edit-gallery-teammembers/<teammember_id>", methods=['GET', 'POST'])
@login_required
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
        flash(u'You successfully updated the team member entry', 'success')
        return redirect_flask(url_for('listTeamMembers'))

    else:
        form = forms.GalleryEmployees(data=teammember)

    return render_template('admin/gallery/teammembers/galleryTeamMemberEdit.html', form=form, teamMemberId=teammember_id)

@app.route("/admin/delete-gallery-teammembers/<teammember_id>", methods=['GET', 'POST'])
@login_required
def deleteTeamMembers(teammember_id):
    if request.method == 'POST':
        print teammember_id
        db.teammember.remove({"_id": ObjectId(teammember_id)})
        flash(u'You deleted the team member', 'warning')
        return redirect_flask(url_for('listTeamMembers'))

    return render_template('admin/gallery/teammembers/galleryTeamMemberDelete.html')

### opening hours ###
@app.route("/admin/manage-opening-hours/")
@login_required
def listOpeningHours():
    form = forms.GalleryHours()
    openinghours = db.openinghours.find()

    return render_template('admin/gallery/openinghours/galleryOpeningHours.html', openinghours=openinghours, form=form)

@app.route("/admin/edit-opening-hours/", methods=['GET', 'POST'])
@login_required
def createOpeningHours():
    form = forms.GalleryHours()

    if form.validate_on_submit():
        formdata = form.data
        openinghour = utils.handle_form_data({}, formdata)
        db.openinghours.insert(openinghour)
        flash(u'You successfully created the opening hour entry', 'success')
        return redirect_flask(url_for('listOpeningHours'))

    return render_template('admin/gallery/openinghours/galleryOpeningHoursCreate.html', form=form)

@app.route("/admin/edit-opening-hours/<opening_hour_id>", methods=['GET', 'POST'])
@login_required
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
            flash(u'You successfully updated the opening hour entry', 'success')
            return redirect_flask(url_for('listOpeningHours'))
    else:
        form = forms.GalleryHours(data=opening_hour)

    return render_template('admin/gallery/openinghours/galleryOpeningHoursEdit.html', form=form, galleryHoursId=opening_hour_id)

@app.route("/admin/delete-opening-hours/<opening_hour_id>", methods=['GET', 'POST'])
@login_required
def deleteOpeningHours(opening_hour_id):
    if request.method == 'POST':
        print opening_hour_id
        db.openinghours.remove({"_id": ObjectId(opening_hour_id)})
        flash(u'You successfully deleted the opening hour entry', 'warning')
        return redirect_flask(url_for('listOpeningHours'))

    return render_template('admin/gallery/openinghours/galleryOpeningHoursDelete.html')

app.register_blueprint(admin.artist, url_prefix='/admin/artist')
app.register_blueprint(admin.exhibition, url_prefix='/admin/exhibition')
app.register_blueprint(admin.image, url_prefix='/admin/image')
app.register_blueprint(admin.api, url_prefix='/admin/api')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

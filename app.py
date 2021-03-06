#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python Standard Library
import os
from datetime import datetime, date, timedelta

# Dependencies: Flask + PIL or Pillowexhibition/create/
from functools import wraps, cmp_to_key
from flask import   Flask, flash, send_from_directory, \
                    redirect as redirect_flask, \
                    render_template, url_for, request, \
                    abort, Response, session, redirect
from flask_pagedown import PageDown
from flask.ext.misaka import Misaka

import pymongo

from itertools import chain

from main import utils
from main.utils import login_required
from bson import ObjectId
from bson.json_util import dumps
import forms

import json

from main import admin, settings
from main.settings import db, secret_key
import re

app = Flask(__name__)

pagedown = PageDown(app)
Misaka(app)
app.secret_key = secret_key

if not app.debug:
    import logging.handlers, os.path

    file_handler=logging.handlers.RotatingFileHandler(
        filename=settings.logFilename,
        backupCount=settings.logBackupCount,
        maxBytes=settings.logMaxBytes
    )

    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)

JPEG_THUMB_QUALITY = 80 # 'keep' as an alternative

@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    flash('You are logged out', 'warning')
    return redirect_flask(url_for('login'))

def validate_credentials(username=False, password=False):
    from main.users import users

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
            flash('You are logged in! Welcome', 'success')

            return redirect_flask(url_for('viewAdmin'))
        else:
            flash('Invalid credentials; Please try again.', 'danger')
    return render_template('general-login.html', error=error, form=form)


####################################################################################

### PUBLIC VIEWS ###

####################################################################################


@app.route("/")
@app.route("/current/")
def home():
    if "homepage" not in db.collection_names():
        homepage_temp = {"_id" : "current_status", "status" : "opt1", "internal_link" : "", "choosen_ext_exhibition_id": ""}
        db.homepage.update({"_id":'current_status'},homepage_temp, upsert=True)
    homepage_info = db.homepage.find_one({"_id": 'current_status'})
    homepage_selected_exhibition = db.exhibitions.find_one({"_id": homepage_info['choosen_ext_exhibition_id']})
    artworks = db.artworks.find().sort("id", -1).limit(10)
    exhibition_32 = db.exhibitions.find({
        "is_published": True,
        "location": "32",
        "end": { "$gte": datetime.combine(date.today(), datetime.min.time()) }
        }).sort("end", 1).limit(1)

    exhibition_35 = db.exhibitions.find({
        "is_published": True,
        "location": "35",
        "end": { "$gte": datetime.combine(date.today(), datetime.min.time()) }
        }).sort("end", 1).limit(1)

    current_virtual_exhib = db.exhibitions.find({
        "is_published": True,
        "location": "virtual",
        "end": { "$gte": datetime.combine(date.today(), datetime.min.time()) }
        }).sort("end", 1).limit(1)

    return render_template("front/current.html", homepage_info=homepage_info, homepage_selected_exhibition=homepage_selected_exhibition, exhibition_32=exhibition_32, exhibition_35=exhibition_35, current_virtual_exhib=current_virtual_exhib)

@app.route("/past/")

def pastExhibitions():
    exhibitions = {}

    past_exhibitions = db.exhibitions.find({
        "is_published": True,
        "end": { "$lt": datetime.combine(date.today(), datetime.min.time()) }
    }).sort("start", -1)

    for exhibition in past_exhibitions:
      year = exhibition['start'].year

      if year not in exhibitions:
        exhibitions[year] = []

      exhibitions[year].append(exhibition)


    years = list(exhibitions.keys())
    years.sort(reverse=True)

    return render_template("front/past.html", past_exhibitions=exhibitions, years=years)

@app.route("/upcoming/")
def upcomingExhibitions():
    future_exhibition = db.exhibitions.find({
        "is_published": True,
        "start": { "$gt": datetime.combine(date.today(), datetime.min.time()) + timedelta(days=3) }
    }).sort("start", 1)

    return render_template("front/upcoming.html", future_exhibition=future_exhibition)


@app.route("/artists/")
def artists():
    normal_artists = []
    artist_projects = []
    artists = db.artist.find({
    "is_published": True,
    }).sort("artist_sort", 1)
    for artist in artists:
        if "artist_is_project" in artist:
            if artist['artist_is_project'] == False:
                normal_artists.append(artist)
            if artist['artist_is_project'] == True:
                artist_projects.append(artist)
        else:
            normal_artists.append(artist)
    return render_template("front/artists.html", normal_artists=normal_artists, artist_projects=artist_projects)

@app.route("/artist/<slug>/")
def artist(slug):
    artist = db.artist.find_one({"slug": slug})
    has_artworks = True if 'selected_images' in artist and len(artist['selected_images']) > 0 else False
    involved_in = [e for e in db.exhibitions.find({
        "is_published": True,
        "artist._id": artist['_id']
    }).sort("start", -1)]
    involved_in_group = [e for e in db.exhibitions.find({
        "is_published": True,
        "is_group_expo": True,
        "artists._id": artist['_id'],
    }).sort("start", -1)]

    involved_in_all = sorted(involved_in + involved_in_group, key=lambda vs: vs['start'], reverse=True)

    for image in artist['selected_images']:
        exhibition = db.exhibitions.find_one({'images._id': image['_id']})

        if exhibition:
            image['exhibition'] = exhibition

    has_involved_in = True if (len(involved_in_all) > 0) else False

    return render_template("front/artist.html", artist=artist, involved_in=involved_in_all, has_involved_in=has_involved_in, has_artworks=has_artworks)

@app.route("/current/<slug>/")
def exhibition(slug):
    exhibition = db.exhibition.find_one({ "slug": slug})
    return render_template("front/exhibition.html")

@app.route("/exhibition/<artist>/<start>")
@app.route("/exhibition/<artist>/<start>/")
def publicviewExhibition(start, artist):
    start = datetime.strptime(start, ('%d.%m.%Y'))
    exhibition = db.exhibitions.find_one({'start': start, 'artist.slug': artist})

    if exhibition != None:
        return render_template('front/exhibition.html', artist=artist, date=date, exhibition=exhibition)
    else:
        abort(404)
"""
    Sort function to alphabetically sort all the artitsts in the list
"""
def cmp(a, b):
    return (a > b) - (a < b)
    
def sort_all_artists (a, b):
    name_a = a['artist_sort'] if type(a) is dict else a
    name_b = b['artist_sort'] if type(b) is dict else b
    return cmp(name_a.lower(), name_b.lower())

@app.route("/group-exhibition/<slug>/")
def publicviewGroupExhibition(slug):
    exhibition = db.exhibitions.find_one({
    'slug': slug,
    'is_group_expo': True,
    })
    exhibition['all_artists'] = exhibition['artists'] + exhibition['extra_artists']
    exhibition['all_artists'].sort(key=cmp_to_key(sort_all_artists))

    for artwork in exhibition['artworks']:
        for artist in exhibition['artists']:
            if utils.find_where('_id', artwork['_id'], artist['images']):
                artwork['artist'] = artist
                break

    if exhibition != None:
        return render_template('front/exhibition.html', exhibition=exhibition)
    else:
        abort(404)

@app.route("/gallery/")
def GalleryInfo():
    teammembers = db.teammember.find()
    openinghours = db.openinghours.find()

    return render_template('front/gallery.html', teammembers=teammembers, openinghours=openinghours)

@app.route("/temp-home/")
def TempHome():

    return render_template('front/temp-home.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

####################################################################################

### ADMIN FUNCTIONALITY ###

####################################################################################

@app.route("/admin/")
@login_required
def viewAdmin():
    return render_template('admin.html')

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
        flash('You successfully created a new team member', 'success')
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
        flash('You successfully updated the team member entry', 'success')
        return redirect_flask(url_for('listTeamMembers'))

    else:
        form = forms.GalleryEmployees(data=teammember)

    return render_template('admin/gallery/teammembers/galleryTeamMemberEdit.html', form=form, teamMemberId=teammember_id)

@app.route("/admin/delete-gallery-teammembers/<teammember_id>", methods=['GET', 'POST'])
@login_required
def deleteTeamMembers(teammember_id):
    if request.method == 'POST':
        print(teammember_id)
        db.teammember.remove({"_id": ObjectId(teammember_id)})
        flash('You deleted the team member', 'warning')
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
        flash('You successfully created the opening hour entry', 'success')
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
            flash('You successfully updated the opening hour entry', 'success')
            return redirect_flask(url_for('listOpeningHours'))
    else:
        form = forms.GalleryHours(data=opening_hour)

    return render_template('admin/gallery/openinghours/galleryOpeningHoursEdit.html', form=form, galleryHoursId=opening_hour_id)

@app.route("/admin/delete-opening-hours/<opening_hour_id>", methods=['GET', 'POST'])
@login_required
def deleteOpeningHours(opening_hour_id):
    if request.method == 'POST':
        print(opening_hour_id)
        db.openinghours.remove({"_id": ObjectId(opening_hour_id)})
        flash('You successfully deleted the opening hour entry', 'warning')
        return redirect_flask(url_for('listOpeningHours'))

    return render_template('admin/gallery/openinghours/galleryOpeningHoursDelete.html')

@app.route("/static/thumbs/<path:path>")
def generateThumb(path):
    from PIL import Image
    import os.path

    inpath = os.path.join('static/uploads', path)

    folder, name = os.path.split(path)
    folder = os.path.normpath(folder)

    if os.path.exists(os.path.join(settings.appdir, 'static/uploads', folder)) and os.path.exists(os.path.join(settings.appdir, inpath)):
        im = Image.open(os.path.join(settings.appdir, inpath))
        im.thumbnail(settings.thumbsize, Image.ANTIALIAS)
        im.save(os.path.join(settings.appdir, 'static/thumbs', path), quality=JPEG_THUMB_QUALITY)
        return send_from_directory(os.path.join(settings.appdir, 'static/thumbs'), path)

    abort(404)

@app.route("/admin/regenerate-thumbs", methods=["GET", "POST"])
@login_required
def regenerateThumbs():
    import subprocess
    import shlex
    import time
    cmd	= "sh /home/janssen/webapps/new_rodolphejanssen_com/Jason-Scraper/regenerateThumbs.sh"
    parsed_cmd = shlex.split(cmd)
    print(parsed_cmd)
    subprocess.call(parsed_cmd)
    print("removed all thumbs")
    time.sleep(5)
    flash('Thumbnail cache has been deleted, new thumbnails generated.', 'success')
    return redirect_flask(url_for('viewAdmin'))
    return render_template('admin.html')

app.register_blueprint(admin.artist, url_prefix='/admin/artist')
app.register_blueprint(admin.exhibition, url_prefix='/admin/exhibition')
app.register_blueprint(admin.groupexhibition, url_prefix='/admin/group-exhibition')
app.register_blueprint(admin.image, url_prefix='/admin/image')
app.register_blueprint(admin.exhib_views, url_prefix='/admin/exhib-views')
app.register_blueprint(admin.artist_exhib_views, url_prefix='/admin/artist-exhib-views')
app.register_blueprint(admin.api, url_prefix='/admin/api')
app.register_blueprint(admin.homepage, url_prefix='/admin/homepage')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python Standard Library
import os
from datetime import datetime, date, timedelta

# Dependencies: Flask + PIL or Pillowexhibition/create/
from functools import wraps
from flask import   Flask, flash, send_from_directory, \
                    redirect as redirect_flask, \
                    render_template, url_for, request, \
                    abort, Response, session
from flask_pagedown import PageDown
from flask.ext.misaka import Misaka

import pymongo

from main import utils
from main.utils import login_required
from bson import ObjectId
from bson.json_util import dumps
import forms

import json

from main import admin, settings
from main.settings import db, secret_key

app = Flask(__name__)

pagedown = PageDown(app)
Misaka(app)
app.secret_key = secret_key

if not app.debug:
    import logging, os.path
    file_handler = logging.FileHandler(os.path.join(settings.appdir, 'logs/flask.log'))
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)

@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    flash(u'You are logged out', 'warning')
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
            flash(u'You are logged in! Welcome', 'success')

            return redirect_flask(url_for('viewAdmin'))
        else:
            flash(u'Invalid credentials; Please try again.', 'danger')
    return render_template('general-login.html', error=error, form=form)


####################################################################################

### PUBLIC VIEWS ###

####################################################################################

@app.route("/")
def tempHome():
    return render_template("front/temporaryhome.html")

#@app.route("/")
@app.route("/current/")
@login_required
def home():
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

    return render_template("front/current.html", exhibition_32=exhibition_32, exhibition_35=exhibition_35)

@app.route("/past/")
@login_required
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


    years = exhibitions.keys()
    years.sort(reverse=True)

    return render_template("front/past.html", past_exhibitions=exhibitions, years=years)

@app.route("/upcoming/")
@login_required
def upcomingExhibitions():
    future_exhibition = db.exhibitions.find({
        "is_published": True,
        "start": { "$gt": datetime.combine(date.today(), datetime.min.time()) + timedelta(days=3) }
    })

    return render_template("front/upcoming.html", future_exhibition=future_exhibition)


@app.route("/artists/")
@login_required
def artists():
    artists = db.artist.find({
    "is_published": True,
    }).sort("artist_sort", 1)
    return render_template("front/artists.html", artists=artists)

@app.route("/artist/<slug>/")
@login_required
def artist(slug):
     artist = db.artist.find_one({"slug": slug})
     artworks = db.image.find({"artist._id": artist['_id']})
     has_artworks = db.image.find_one({"artist._id": artist['_id']})
     involved_in = db.exhibitions.find({
        "is_published": True,
        "artist._id": artist['_id']
    })
     has_involved_in = db.exhibitions.find_one({
       "is_published": True,
       "artist._id": artist['_id']
    })


     return render_template("front/artist.html", artist=artist, artworks=artworks, involved_in=involved_in, has_involved_in=has_involved_in, has_artworks=has_artworks)

@app.route("/current/<slug>/")
@login_required
def exhibition(slug):
    exhibition = db.exhibition.find_one({ "slug": slug})
    return render_template("front/exhibition.html")

@app.route("/exhibition/<artist>/<start>")
@app.route("/exhibition/<artist>/<start>/")
@login_required
def publicviewExhibition(start, artist):
    start = datetime.strptime(start, ('%d.%m.%Y'))

    exhibition = db.exhibitions.find_one({'start': start, 'artist.slug': artist})

    if exhibition <> None:
        return render_template('front/exhibition.html', artist=artist, date=date, exhibition=exhibition)
    else:
        abort(404)

@app.route("/group-exhibition/<slug>/")
@login_required
def publicviewGroupExhibition(slug):
    exhibition = db.exhibitions.find_one({'slug': slug})
    all_artists = db.exhibition.find({
    })

    if exhibition <> None:
        return render_template('front/exhibition.html', exhibition=exhibition)
    else:
        abort(404)

@app.route("/gallery/")
@login_required
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
app.register_blueprint(admin.groupexhibition, url_prefix='/admin/group-exhibition')
app.register_blueprint(admin.image, url_prefix='/admin/image')
app.register_blueprint(admin.exhib_views, url_prefix='/admin/exhib-views')
app.register_blueprint(admin.api, url_prefix='/admin/api')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

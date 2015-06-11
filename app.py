#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python Standard Library
import os
from datetime import datetime

# Dependencies: Flask + PIL or Pillowexhibition/create/
from flask import Flask, send_from_directory, redirect as redirect_flask, render_template, url_for, request, abort
import pymongo
#import admin

from utils import slugify
from bson import ObjectId
import forms

# Local imports
# from settings import *

app = Flask(__name__)
app.secret_key = "@My*C7KNeC@74#HC$F7FkpEEmECaZ@jH#ePwwz#Fo^#T3%(!bM^xSAG^&!#x*i#*"

client = pymongo.MongoClient()
db = client.artlogic


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

@app.route('/exhibition', methods=['GET', 'POST'])
def adminexhibition():
    all_exhibitions = db.exhibition.find()
    artists = db.artists.find().sort("artist_sort", 1)
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
def viewExhibition(slug):
    exhibition = db.exhibitions.find_one({'slug': slug})

    if exhibition <> None:
        return render_template('front/exhibition.html', exhibition=exhibition)
    else:
        abort(404)

@app.route("/gallery/")
def GalleryInfo():

    teammembers = db.teammember.find()

    return render_template('front/gallery.html', teammembers=teammembers)

### ADMIN FUNCTIONALITY ###
@app.route("/admin/")
def viewAdmin():
    return render_template('admin.html')

@app.route("/admin/exhibitions/")
def exhibitionAdmin():
    all_exhibitions = db.exhibition.find()
    artists = db.artists.find().sort("artist_sort", 1)
    exhibition = None
    new = False
    return render_template('admin/exhibition/exhibitions.html', all_exhibitions=all_exhibitions, exhibition=exhibition, artists=artists, new=new)

@app.route("/admin/exhibition/create/", methods=['GET', 'POST'])
def createExhibition():

    form = forms.ExhibitionForm()

    if form.validate_on_submit():
        exhibition = form.data
        exhibition['slug'] = slugify(exhibition['name'])

        db.exhibitions.insert(exhibition)

        return redirect_flask(url_for('viewExhibition', slug=exhibition['slug']))

    artists = db.artists.find()

    return render_template('admin/exhibition/exhibitionForm.html', form=form, artists=artists)

@app.route('/admin/exhibition/update/<slug>/', methods=['GET', 'POST'])
def updateExhibition (slug):
    exhibition = db.exhibitions.find_one({'slug': slug})

    if request.method == 'POST':
        exhibition['name'] = request.form['name']
        exhibition['slug'] = slugify(request.form['name'])
        exhibition['artists'] = []

        for slug in request.form.getlist('artists'):
            artist = db.artists.find_one({'slug': slug})
            if artist <> None:
                exhibition['artists'].append(artist)

        db.exhibitions.update(
            {'_id': exhibition['_id']},
            exhibition
        )

        return redirect_flask(url_for('viewExhibition', slug=exhibition['slug']))

    artists = db.artists.find()

    if exhibition <> None:
        return render_template('admin/exhibition/exhibitionForm.html', exhibition=exhibition, artists=artists)
    else:
        abort(404)

@app.route("/admin/artists/")
def adminArtists():

    return render_template('admin/artists/artists.html')

@app.route("/admin/manage-gallery-info/", methods=['GET', 'POST'])
def adminGalleryInfo():

    return render_template('admin/gallery.html')

@app.route("/admin/manage-gallery-teammembers/", methods=['GET', 'POST'])
def createTeamMember():

    form = forms.GalleryEmployees()

    if form.validate_on_submit():
        teamMember = form.data
        teamMember['slug'] = slugify(teamMember['name'])

        db.teammember.insert(teamMember)

    teammember = db.teammember.find()

    return render_template('admin/galleryTeamMember.html', form=form, teammember=teammember,)

@app.route("/admin/manage-opening-hours/")
def listOpeningHours():
    form = forms.GalleryHours()
    openinghours = db.openinghours.find()

    return render_template('admin/galleryOpeningHours.html', openinghours=openinghours, form=form)

@app.route("/admin/edit-opening-hours/<_id>", methods=['GET', 'POST'])
def updateOpeningHours(_id):
    if request.method == 'POST':
        form = forms.GalleryHours()

        if form.validate_on_submit():
            data = form.data
            db.openinghours.update(
                {
                    "_id": ObjectId(_id)
                },
                {
                    "period": data['period'],
                    "hours": data['hours']
                },
                upsert=True
            )
            return redirect_flask(url_for('listOpeningHours'))
    else:
        data = db.openinghours.find_one({"_id": ObjectId(_id)})
        form = forms.GalleryHours(data=data)

    return render_template('admin/galleryOpeningHoursEdit.html', form=form, galleryHoursId=_id)

@app.route("/admin/edit-opening-hours/", methods=['GET', 'POST'])
def createOpeningHours():
    form = forms.GalleryHours()

    if form.validate_on_submit():
        openinghour = form.data
        db.openinghours.insert(openinghour)
        return redirect_flask(url_for('listOpeningHours'))
    return render_template('admin/galleryOpeningHoursCreate.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)

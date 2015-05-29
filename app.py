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

from forms import ExhibitionForm
from forms import GalleryInfo

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


# route for handling the login page logic
#@app.route('/login', methods=['GET', 'POST'])
#def login():
    #error = None
    #if request.method == 'POST':
        #if request.form['username'] <> 'admin' or request.form['password'] <> 'admin':
            #error = 'Invalid Credentials. Please try again.'
        #else:
            #return redirect_flask(url_for('home'))
    #return render_template('front/login.html', error=error)

@app.route("/exhibition/<slug>/")
def viewExhibition(slug):
    exhibition = db.exhibitions.find_one({'slug': slug})

    if exhibition <> None:
        return render_template('front/exhibition.html', exhibition=exhibition)
    else:
        abort(404)

@app.route("/gallery/")
def GalleryInfo():

    teammember = db.teammember.find()

    return render_template('front/gallery.html', teammember=teammember)

### ADMIN FUNCTIONALITY ###
@app.route("/exhibition/create/", methods=['GET', 'POST'])
def createExhibition():

    form = ExhibitionForm()

    if form.validate_on_submit():
        exhibition = form.data
        exhibition['slug'] = slugify(exhibition['name'])

        db.exhibitions.insert(exhibition)

        return redirect_flask(url_for('viewExhibition', slug=exhibition['slug']))

    artists = db.artists.find()

    return render_template('admin/exhibition/exhibitionForm.html', form=form, artists=artists)

    #exhibition = {
        #'name': '',
        #'slug': '',
        #'artists': [],
        #'datestart': '',
        #'dateend': '',
        #'keyimage': '',
        #'maintext': '',
        #'exhibitionviews': '',
        #'pressrelease': '',
    #}

    #if request.method == 'POST':
        #exhibition['name'] = request.form['name']
        #exhibition['slug'] = slugify(request.form['name'])
        #exhibition['description'] = request.form['description']

        #for slug in request.form.getlist('artists'):
            #artist = db.artists.find_one({'slug': slug})
            #if artist <> None:
                #exhibition['artists'].append(artist)

        #db.exhibitions.insert(exhibition)

        #return redirect_flask(url_for('viewExhibition', slug=exhibition['slug']))

    #artists = db.artists.find()
    #return render_template('admin/exhibition/exhibitionForm.html', exhibition=exhibition, artists=artists)

@app.route('/exhibition/update/<slug>/', methods=['GET', 'POST'])
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

@app.route("/admin/manage-gallery-info", methods=['GET', 'POST'])
def createTeamMember():

    form = GalleryInfo()

    if form.validate_on_submit():
        teamMember = form.data
        teamMember['slug'] = slugify(teamMember['name'])

        db.teammember.insert(teammember)

    #    return redirect_flask(url_for('galleryInfo'))

    return render_template('admin/exhibition/exhibitionForm.html', form=form, artists=artists)



if __name__ == '__main__':
    app.run(debug=True)

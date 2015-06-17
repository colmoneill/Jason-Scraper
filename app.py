#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python Standard Library
import os
from datetime import datetime

# Dependencies: Flask + PIL or Pillowexhibition/create/
from flask import Flask, send_from_directory, redirect as redirect_flask, render_template, url_for, request, abort
import pymongo
#import admin

from werkzeug import secure_filename
import utils
import forms

# Local imports
# from settings import *

app = Flask(__name__)
app.secret_key = "@My*C7KNeC@74#HC$F7FkpEEmECaZ@jH#ePwwz#Fo^#T3%(!bM^xSAG^&!#x*i#*"

client = pymongo.MongoClient()
db = client.artlogic

app.config['UPLOAD'] = {
    'PRESS_RELEASE': {
        'allowed_extensions': ['pdf'],
        'upload_folder': 'static/uploads/press/'
    }
}

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
        form_data = form.data
        exhibition = utils.handle_form_data({}, form_data, ['press_release_file'])
        exhibition['slug'] = utils.slugify(exhibition['name'])
        
        if request.files['press_release_file']:
            exhibition['press_release'] = utils.handle_uploaded_file(
                request.files['press_release_file'],
                app.config['UPLOAD']['PRESS_RELEASE'],
                '{0}.pdf'.format(exhibition['slug'])
            )
        
        db.exhibitions.insert(exhibition)

        return redirect_flask(url_for('viewExhibition', slug=exhibition['slug']))

    artists = db.artists.find()

    return render_template('admin/exhibition/exhibitionForm.html', form=form, artists=artists)

@app.route('/admin/exhibition/update/<slug>/', methods=['GET', 'POST'])
def updateExhibition (slug):
    exhibition = db.exhibitions.find_one({'slug': slug})
    
    if exhibition <> None:
        form = ExhibitionForm(data=exhibition)

        if form.validate_on_submit():
            form_data = form.data
            exhibition = utils.handle_form_data(exhibition, form_data, ['press_release_file'])
            
            if request.files['press_release_file']:
                exhibition['press_release'] = utils.handle_uploaded_file(
                    request.files['press_release_file'],
                    app.config['UPLOAD']['PRESS_RELEASE'],
                    '{0}.pdf'.format(exhibtion['slug'])
                )
                
            
            db.exhibitions.update({_id: exhibition['_id']}, exhibition, upsert=true )
            return redirect_flask(url_for('viewExhibition', slug=exhibition['slug']))

        artists = db.artists.find()
        return render_template('admin/exhibition/exhibitionForm.html', form=form, artists=artists)
    else:
        abort(404)

@app.route("/admin/artists/")
def adminArtists():
    return render_template('admin/artists/artists.html')

@app.route("/admin/manage-gallery-info/", methods=['GET', 'POST'])
@app.route("/admin/manage-gallery-info", methods=['GET', 'POST'])
def createTeamMember():

    form = forms.GalleryInfo()

    if form.validate_on_submit():
        teamMember = form.data
        teamMember['slug'] = utils.slugify(teamMember['name'])

        db.teammember.insert(teamMember)

    teammember = db.teammember.find()

    return render_template('admin/gallery.html', form=form, teammember=teammember,)

if __name__ == '__main__':
    app.run(debug=True)

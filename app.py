# -*- coding: utf-8 -*-

# Python Standard Library 
import os
from datetime import datetime

# Dependencies: Flask + PIL or Pillow
from flask import Flask, send_from_directory, redirect as redirect_flask, render_template
import pymongo

# Local imports
# from settings import *

app = Flask(__name__)

client = pymongo.MongoClient()
db = client.artlogic

@app.route("/")
def home():
    artworks = db.artworks.find().sort("id", -1)[:10]
    return render_template("home.html", artworks=artworks)

@app.route("/artists/")
def artists():
    artists = db.artists.find().sort("artist_sort", 1)
    return render_template("artists.html", artists=artists)

@app.route("/artists/<slug>/")
def artist(slug):
    artist = db.artists.find_one({ "slug": slug})
    return render_template("artist.html", artist=artist)

if __name__ == '__main__':
    app.run(debug=True)

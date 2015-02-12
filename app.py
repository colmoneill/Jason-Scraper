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

if __name__ == '__main__':
    app.run(debug=True)

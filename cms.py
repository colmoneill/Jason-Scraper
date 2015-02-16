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

@app.route('/', methods=['GET', 'POST'])
def exhibition():
    exhibition = None
    new = False
    if request.method == 'POST' and 'exhibition' in request.form:
        exhibition = request.form['exhibition']
        if db.exhibition.find_one({'exhibition': exhibition}) is None:
            # this is a new exhibition, add it to the database
            db.exhibition.insert({'exhibition': exhibition})
            new = True
    return render_template('exhibition.html', exhibition=exhibition, new=new)

if __name__ == '__main__':
    app.run(debug=True)
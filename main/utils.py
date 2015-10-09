#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import settings
import unicodedata

from werkzeug import secure_filename
from flask import redirect as redirect_flask, session, flash, url_for, request
from functools import wraps

def slugify(value):
    """ Note: This was modified from django.utils.text slugify """
    #value = unicode(value.decode('UTF-8'))
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = value.decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    value = re.sub('[-\s]+', '-', value)
    return str(value)


"""
    Extends given dictionary 'data' with given dictionary 'formdata'
    keys in 'ignore' are ignored
"""
def handle_form_data (data, formdata, ignore = []):
    for key, value in formdata.iteritems():
        if key not in ignore:
            data[key] = value

    return data

"""
    Moves file to desired location as defined in the config, also
    filters on filename and allows to set a new filename for the
    file
"""
def handle_uploaded_file (uploaded_file, config, filename = False):
    import os
        
    if allowed_file(uploaded_file.filename, config['allowed_extensions']):
        if filename == False:
            filename = uploaded_file.filename

        filepath = getsafepath(os.path.join(config['upload_folder'], secure_filename(filename)))
        uploaded_file.save(os.path.join(settings.appdir, filepath))
        
        return filepath

    return False

def getsafepath (path, count = 1):
    root, ext = os.path.splitext(path)
    safepath = root + '-' + str(count) + ext

    if os.path.exists(os.path.join(settings.appdir, safepath)):
        return getsafepath(path, (count+1))
    else:
        return safepath

def getfilesize (path):
    path = os.path.join(settings.appdir, path)
    
    if os.path.exists(path):
        labels = ['b', 'kb', 'mb', 'gb']
        label = labels.pop(0)
        size = os.path.getsize(path)
        
        while (size > 1024.0):
            size = size / 1024.0
            label = labels.pop(0)

        return "{0:.2f}{1}".format(size, label)
    else:
        return False
    
def setfilenameroot (oldname, name):
    root, ext = os.path.splitext(oldname)
    return '{0}{1}'.format(name, ext)

"""
    Tests whether the extension of the given file is allowed
"""
def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in allowed_extensions


# login decorator
def login_required(action):
    @wraps(action)
    def wrap (*args, **kwargs):
        if 'logged_in' in session:
            return action (*args, **kwargs)
        else:
            flash(u'You need to log in first.', 'danger')
            session['next'] = request.path
            return redirect_flask(url_for('login'))

    return wrap

def find_where (key, search, datalist):
    for row in datalist:
        if row[key] == search:
            return row
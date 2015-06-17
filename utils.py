# -*- coding: utf-8 -*-

import unicodedata
import re

# Copied from http://www.leftovercode.info/common_python.php

import os
from werkzeug import secure_filename

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
    if allowed_file(uploaded_file.filename, config['allowed_extensions']):
        if filename == False:
            filename = uploaded_file.filename
            
        filepath = os.path.join(config['upload_folder'], secure_filename(filename))
        uploaded_file.save(filepath)
        
        return filepath
    
    return False

"""
    Tests whether the extension of the given file is allowed
"""
def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in allowed_extensions
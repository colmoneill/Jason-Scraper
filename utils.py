# -*- coding: utf-8 -*-

import unicodedata
import re

# Copied from http://www.leftovercode.info/common_python.php

def slugify(value):
    """ Note: This was modified from django.utils.text slugify """
    value = unicode(value.decode('UTF-8'))
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = value.decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    value = re.sub('[-\s]+', '-', value)
    return str(value)

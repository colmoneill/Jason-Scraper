#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import SelectField, FileField, StringField
from wtforms.validators import DataRequired
example_price = "€1.000".decode("utf-8")

class Image(Form):
    artist = SelectField(u'Select artist *', validators=[DataRequired()])
    image_file = FileField(u'Image to upload *', validators=[DataRequired()])
    title = StringField(u'Title of the artwork')
    stock_number = StringField(u'Stock number')
    year = StringField(u'Year')
    medium = StringField(u'Artwork medium')
    dimensions = StringField(u'Artwork dimensions (include unit)' , render_kw={"placeholder": "depth x width x height CM"})
    edition = StringField(u'Artwork edition info')
    price = StringField(u'Artwork price (include currency symbol)', render_kw={"placeholder": example_price})

class ImageUpdate(Form):
    title = StringField(u'Title of the artwork')
    stock_number = StringField(u'Stock number')
    year = StringField(u'Year')
    medium = StringField(u'Artwork medium')
    dimensions = StringField(u'Artwork dimensions (include unit)', render_kw={"placeholder": "depth x width x height CM"})
    edition = StringField(u'Artwork edition info')
    price = StringField(u'Artwork price (include currency symbol)', render_kw={"placeholder": example_price})

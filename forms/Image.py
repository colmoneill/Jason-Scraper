from flask_wtf import Form
from wtforms import SelectField, FileField, StringField
from wtforms.validators import DataRequired

class Image(Form):
    artist = SelectField(u'Select artist *', validators=[DataRequired()])
    image_file = FileField(u'Image to upload *', validators=[DataRequired()])
    title = StringField(u'title of the artwork')
    year = StringField(u'year')
    medium = StringField(u'Artwork medium')
    dimensions = StringField(u'Artwork dimentions in CM')

class ImageUpdate(Form):
    title = StringField(u'title of the artwork', validators=[DataRequired()])
    year = StringField(u'year')
    medium = StringField(u'Artwork medium')
    dimensions = StringField(u'Artwork dimentions in CM')

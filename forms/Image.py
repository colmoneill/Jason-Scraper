from flask_wtf import Form
from wtforms import SelectField, FileField, StringField
from wtforms.validators import DataRequired

class Image(Form):
    artist = SelectField(u'Select artist *', validators=[DataRequired()])
    image_file = FileField(u'Image top upload *', validators=[DataRequired()])
    title_and_year = StringField(u'title and year of artwork, comma separated')
    medium = StringField(u'Artwork medium')
    dimensions = StringField(u'Artwork dimentions in CM')

from flask_wtf import Form
from wtforms import SelectField, FileField, StringField
from wtforms.validators import DataRequired

class ArtistExhibitionView(Form):
    exhibition_title = StringField(u'Exhibition views exhibition title')
    year = StringField(u'Year of the exhibition')
    institution = StringField(u'Institution')
    city = StringField(u'City')
    country = StringField(u'Country')

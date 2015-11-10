from flask_wtf import Form
from wtforms import SelectField, FileField, StringField
from wtforms.validators import DataRequired

class ExhibitionView(Form):
    artist = StringField(u'Artists visible in the view')
    exhibition_title = StringField(u'Exhibition views exhibition title')
    year = StringField(u'Year of the exhibition')
    institution = StringField(u'Institution')
    country = StringField(u'Country')

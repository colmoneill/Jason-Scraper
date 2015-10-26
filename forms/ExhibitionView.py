from flask_wtf import Form
from wtforms import SelectField, FileField, StringField
from wtforms.validators import DataRequired

class ExhibitionView(Form):
    artist = StringField(u'artists visible in the view')
    exhibition_title = StringField(u'exhibition views exhibition title')
    year = StringField(u'year of the exhibition')
    institution = StringField(u'institution')
    country = StringField(u'Country')

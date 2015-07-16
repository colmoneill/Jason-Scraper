from flask_wtf import Form
from flask_pagedown.fields import PageDownField
from wtforms import StringField, FileField
from wtforms.validators import DataRequired

class ArtistForm(Form):
    name = StringField(u'Artist name *', validators=[DataRequired()])
    wysiwig_artist_biography = PageDownField('artist biography')
    press_release_file = FileField('Press release files')

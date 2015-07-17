from flask_wtf import Form
from flask_pagedown.fields import PageDownField
from wtforms import StringField, FileField, TextAreaField
from wtforms.validators import DataRequired

class ArtistForm(Form):
    name = StringField(u'Artist name *', validators=[DataRequired()])
    #key image
    #images general
    wysiwig_artist_info = PageDownField('artist info text')
    wysiwig_artist_bio = PageDownField('artist bio & exhibition list')
    press_release_file = FileField('Press release files')
    iframe1 = TextAreaField('Paste in code for media iframe')
    iframe2 = TextAreaField('Paste in code for media iframe')
    iframe3 = TextAreaField('Paste in code for media iframe')

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
    link_name1 = StringField('name for link 1')
    link_url1 = StringField('Paste in full url of link 1')
    link_name2 = StringField('name for link 2')
    link_url2 = StringField('Paste in full url of link 2')
    link_name3 = StringField('name for link 3')
    link_url3 = StringField('Paste in full url of link 3')

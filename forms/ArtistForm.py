from flask_wtf import Form
from flask_pagedown.fields import PageDownField
from wtforms import StringField, FileField
from wtforms.validators import DataRequired

class ArtistForm(Form):
    name = StringField(u'Artist name *', validators=[DataRequired()])
    keyImage = StringField(u'key image to represent the artist *', validators=[DataRequired()])
    # other images = FileField('Other images from AL')
    images = StringField(u'images *', validators= [DataRequired()])
    wysiwig_artist_biography = PageDownField('artist biography')
    press_release_file = FileField('Press release files')
    # list of exhibitions that artist was involved in: checkbox list of available exhibitions for bottom of page lising

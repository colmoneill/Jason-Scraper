from flask_wtf import Form
from flask_pagedown.fields import PageDownField
from wtforms import StringField, DateTimeField, TextAreaField, FileField
from wtforms.validators import DataRequired

class ExhibitionForm(Form):
    artist = StringField(u'Artist Name *', validators=[DataRequired()])
    name = StringField('Title')
    start = DateTimeField('From', validators=[DataRequired()], format='%d-%m-%Y')
    end = DateTimeField('To', validators=[DataRequired()], format='%d-%m-%Y')
    # key_image = FileField('Exhibition key image')
    # other images = FileField('Other images from AL')
    wysiwig_exhibition_description = PageDownField('exhibition description')
    wysiwig_artist_bio = PageDownField('artist bio')
    press_release_file = FileField('Press release files')
    # press_release_file_en = FileField('Press release files EN')
    # press_release_file_fr = FileField('Press release files FR')
    # press_release_file_nl = FileField('Press release files NL')
    # submit = SubmitField('Submit')

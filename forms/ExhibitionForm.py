from flask_wtf import Form
from flask_pagedown.fields import PageDownField

from wtforms import StringField, DateTimeField,\
    SelectField, TextAreaField, FileField, \
    BooleanField

from wtforms.validators import DataRequired

class ExhibitionForm(Form):
    artist = SelectField(u'Select Artist *', validators=[DataRequired()])
    exhibition_name = StringField('Title')
    start = DateTimeField('From', validators=[DataRequired()], format='%d-%m-%Y')
    end = DateTimeField('To', validators=[DataRequired()], format='%d-%m-%Y')
    exhibition_key_img = FileField('exhibition key image')
    wysiwig_exhibition_description = PageDownField('exhibition description')
    wysiwig_artist_bio = PageDownField('artist bio')
    press_release_file = FileField('Press release files')
    is_published = BooleanField('Visible on public site')

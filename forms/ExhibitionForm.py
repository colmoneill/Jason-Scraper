from flask_wtf import Form
from flask_pagedown.fields import PageDownField
from wtforms import StringField, DateTimeField, SelectField, TextAreaField, FileField, SelectField
from wtforms.validators import DataRequired

class ExhibitionForm(Form):
    #artist = StringField(u'Artist Name *', validators=[DataRequired()])
    artist = SelectField(u'Select artist *', validators=[DataRequired()])
    exhibition_name = StringField('Title')
    start = DateTimeField('From', validators=[DataRequired()], format='%d-%m-%Y')
    end = DateTimeField('To', validators=[DataRequired()], format='%d-%m-%Y')
    exhibition_key_img = FileField('exhibition key image')
    wysiwig_exhibition_description = PageDownField('exhibition description')
    wysiwig_artist_bio = PageDownField('artist bio')
    press_release_file = FileField('Press release files')

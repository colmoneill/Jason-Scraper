from flask_wtf import Form
from flask_pagedown.fields import PageDownField

from wtforms import StringField, DateTimeField,\
    SelectField, TextAreaField, FileField, \
    BooleanField, TextAreaField, RadioField

from wtforms.validators import DataRequired
from wtforms.widgets import CheckboxInput



class ExhibitionForm(Form):
    artist = SelectField(u'Select Artist *', validators=[DataRequired()])
    exhibition_name = StringField('Exhibition title')
    start = DateTimeField('From', validators=[DataRequired()], format='%d-%m-%Y')
    end = DateTimeField('To', validators=[DataRequired()], format='%d-%m-%Y')
    location = RadioField(u'Gallery 32 or 35? *', choices = [('35', 'Livourne 35'), ('32', 'Livourne 32'), ('external', 'External show'), ('virtual', 'Virtual Show')], validators=[DataRequired()])
    external_location = StringField('external location details (Name of venue, event, space)')
    #exhibition_key_img = FileField('exhibition key image')
    wysiwig_exhibition_description = PageDownField('exhibition description')
    wysiwig_artist_bio = PageDownField('artist bio')
    press_release = FileField('Press release file')
    #is_published = BooleanField('Visible on public site')
    link_name1 = StringField('name for link 1')
    link_url1 = StringField('Paste in full url of link 1')
    link_name2 = StringField('name for link 2')
    link_url2 = StringField('Paste in full url of link 2')
    link_name3 = StringField('name for link 3')
    link_url3 = StringField('Paste in full url of link 3')
    embed_video = StringField('Paste embed code of video to display on the page')

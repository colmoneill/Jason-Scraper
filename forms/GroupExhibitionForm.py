from flask_wtf import Form
from flask_pagedown.fields import PageDownField
from wtforms import StringField, DateTimeField, SelectField, TextAreaField, FileField, SelectMultipleField, RadioField, TextAreaField
from wtforms.validators import DataRequired
from wtforms.widgets import CheckboxInput

class GroupExhibitionForm(Form):
    exhibition_name = StringField('Title')
    start = DateTimeField('From', validators=[DataRequired()], format='%d-%m-%Y')
    end = DateTimeField('To', validators=[DataRequired()], format='%d-%m-%Y')
    exhibition_key_img = FileField('exhibition key image')
    artists = RadioField(u'Select Artist *', option_widget=CheckboxInput(), validators=[DataRequired()])
    extra_artists = StringField(u'Extra artists names (non gallery artists)')
    wysiwig_exhibition_description = PageDownField('exhibition description')
    press_release_file = FileField('Press release files')
    link_name1 = StringField('name for link 1')
    link_url1 = StringField('Paste in full url of link 1')
    link_name2 = StringField('name for link 2')
    link_url2 = StringField('Paste in full url of link 2')
    link_name3 = StringField('name for link 3')
    link_url3 = StringField('Paste in full url of link 3')

from flask_wtf import Form
from flask_pagedown.fields import PageDownField
from wtforms import StringField, DateTimeField, SelectField, TextAreaField, FileField, SelectMultipleField, RadioField
from wtforms.validators import DataRequired
from wtforms.widgets import CheckboxInput

class GroupExhibitionForm(Form):
    exhibition_name = StringField('Title')
    start = DateTimeField('From', validators=[DataRequired()], format='%d-%m-%Y')
    end = DateTimeField('To', validators=[DataRequired()], format='%d-%m-%Y')
    exhibition_key_img = FileField('exhibition key image')
    artists = RadioField(u'Select Artist *', option_widget=CheckboxInput(), validators=[DataRequired()])
    extra_artists = StringField(u'Extra artists names (non gallery artists)', validators=[DataRequired()])
    wysiwig_exhibition_description = PageDownField('exhibition description')
    press_release_file = FileField('Press release files')

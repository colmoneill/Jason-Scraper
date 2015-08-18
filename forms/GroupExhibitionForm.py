from flask_wtf import Form
from flask_pagedown.fields import PageDownField
from wtforms import StringField, DateTimeField, SelectField, TextAreaField, FileField, SelectMultipleField, RadioField, TextAreaField
from wtforms.validators import DataRequired
from wtforms.widgets import CheckboxInput, ListWidget

class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class GroupExhibitionForm(Form):
    exhibition_name = StringField('Title')
    start = DateTimeField('From', format='%d-%m-%Y')
    end = DateTimeField('To', format='%d-%m-%Y')
    location = RadioField(u'Gallery 32 or 35? *', choices = [('35', 'Livourne 35'), ('32', 'Livourne 32')], validators=[DataRequired()])
    #exhibition_key_img = FileField('exhibition key image')
    artists = MultiCheckboxField(u'Select Artist *')
    extra_artists = StringField(u'Extra artists names (non gallery artists)')
    wysiwig_exhibition_description = PageDownField('exhibition description')
    press_release_file = FileField('Press release files')
    link_name1 = StringField('name for link 1')
    link_url1 = StringField('Paste in full url of link 1')
    link_name2 = StringField('name for link 2')
    link_url2 = StringField('Paste in full url of link 2')
    link_name3 = StringField('name for link 3')
    link_url3 = StringField('Paste in full url of link 3')

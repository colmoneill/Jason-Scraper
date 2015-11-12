from flask_wtf import Form
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

class externalExhibitionView(Form):
    artists = MultiCheckboxField(u'Select Artist *')
    image_file = FileField(u'Image to upload *', validators=[DataRequired()])
    exhibition_title = StringField(u'external exhibition title')
    year = StringField(u'Year of the exhibition')
    institution = StringField(u'Institution')
    city = StringField(u'City')
    country = StringField(u'Country')

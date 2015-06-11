from flask_wtf import Form
from wtforms import StringField, HiddenField
from wtforms.validators import DataRequired

class GalleryHours(Form):
    galleryHoursId = HiddenField()
    period = StringField('period', validators=[DataRequired()])
    hours = StringField('hours', validators=[DataRequired()])

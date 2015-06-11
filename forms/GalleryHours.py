from flask_wtf import Form
from wtforms import StringField, HiddenField
from wtforms.validators import DataRequired

class GalleryHours(Form):
    galleryHoursId = HiddenField()
    period = StringField(u'Period // example: Tuesday to Friday *', validators=[DataRequired()])
    hours = StringField(u'Hours // example: 12.00 > 19.00 *', validators=[DataRequired()])

from flask_wtf import Form
from wtforms import SelectField, FileField
from wtforms.validators import DataRequired

class Image(Form):
    artist = SelectField(u'Select artist *', validators=[DataRequired()])
    image_file = FileField(u'Image top uploadd*', validators=[DataRequired()])
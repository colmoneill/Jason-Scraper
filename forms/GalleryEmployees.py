from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired

class GalleryEmployees(Form):
    name = StringField('Team member name', validators=[DataRequired()])
    role = StringField('Team member role')
    email = StringField('Team member email', validators=[DataRequired()])

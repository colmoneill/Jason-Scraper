from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired

class GalleryInfo(Form):
    name = StringField('Team member name', validators=[DataRequired()])
    role = StringField('Team member role', validators=[DataRequired()])
    email = StringField('Team member email', validators=[DataRequired()])

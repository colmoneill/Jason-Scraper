from flask_wtf import Form
from wtforms import StringField, HiddenField
from wtforms.validators import DataRequired

class GalleryEmployees(Form):
    name = StringField(u'Team member name // example: Rodolphe Janssen *', validators=[DataRequired()])
    role = StringField(u'Team member role // example: Operation & Logistic Manager')
    email = StringField(u'Team member email *', validators=[DataRequired()])

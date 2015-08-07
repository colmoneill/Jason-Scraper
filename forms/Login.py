from flask_wtf import Form
from wtforms import SelectField, FileField, StringField
from wtforms.validators import DataRequired

class Login(Form):
    username = StringField(u'Username', validators=[DataRequired()])
    password = StringField(u'Password', validators=[DataRequired()])

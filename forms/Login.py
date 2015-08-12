from flask_wtf import Form
from wtforms import SelectField, FileField, StringField, PasswordField
from wtforms.validators import DataRequired

class Login(Form):
    username = StringField(u'Username', validators=[DataRequired()])
    password = PasswordField(u'Password', validators=[DataRequired()])

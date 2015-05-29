from flask_wtf import Form
from wtforms import StringField, DateField
from wtforms.validators import DataRequired

class ExhibitionForm(Form):
    name = StringField('Artist name', validators=[DataRequired()])
    start = DateField('From', validators=[DataRequired()], format='%d-%m-%Y')
    end = DateField('To', validators=[DataRequired()], format='%d-%m-%Y')
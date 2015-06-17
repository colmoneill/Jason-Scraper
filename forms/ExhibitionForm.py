from flask_wtf import Form
from wtforms import StringField, DateTimeField, TextAreaField, FileField
from wtforms.validators import DataRequired

class ExhibitionForm(Form):
    name = StringField('Title', validators=[DataRequired()])
    start = DateTimeField('From', validators=[DataRequired()], format='%d-%m-%Y')
    end = DateTimeField('To', validators=[DataRequired()], format='%d-%m-%Y')
    description = TextAreaField('Description', validators=[DataRequired()])
    press_release_file = FileField('Press release files') 
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired

class artistCreate(Form):
    name = StringField(u'Artist name *', validators=[DataRequired()])
    keyImage = StringField(u'key image to represent the artist *', validators=[DataRequired()])
    images = StringField(u'images *', validators= [DataRequired()])
    infoText = StringField(u'info text describing the artist's work')

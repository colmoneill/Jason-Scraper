from flask_wtf import Form
from flask_pagedown.fields import PageDownField
from wtforms import StringField, FileField, TextAreaField, RadioField
from wtforms.validators import DataRequired

class HomepageForm(Form):
    status = RadioField(u'Enable special homepage layout ?', choices = [
    ('no', 'no, use normal side by side exhibition layout, option 1'),
    ('yes', 'yes, using option 2, highlight only the show at *32* Livornostraat'),
    ('yes', 'yes, using option 3, highlight only the show at *35* Livornostraat'),
    ('yes', 'yes, using option 4, highlight an external show'),
    ('yes', 'yes, using option 5, triptych — show exhibitions in showrooms 32, 35 and a selected third exhibition'),
    ],validators=[DataRequired()])
    status = RadioField(u'Choose which external exhibition to highlight : ', choices = [])
    internal_link = StringField('paste here the link of the page users should get to when they click on this homepage element')

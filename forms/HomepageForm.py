from flask_wtf import Form
from flask_pagedown.fields import PageDownField
from wtforms import StringField, FileField, TextAreaField, RadioField, SelectField
from wtforms.validators import DataRequired

from main.settings import db
from bson import ObjectId

ext_exhibition = db.exhibitions.find({
    "is_published": True,
    "$or": [
        {"location": "external"},
        {"location": "virtual"},
    ]
    })

class HomepageForm(Form):
    status = RadioField(u'Enable special homepage layout ?', choices = [
    ('opt1', 'no, use normal side by side exhibition layout, option 1'),
    ('opt2', 'yes, using option 2, highlight only the show at *32* Livornostraat'),
    ('opt3', 'yes, using option 3, highlight only the show at *35* Livornostraat'),
    ('opt4', 'yes, using option 4, highlight an external show'),
    ('opt5', 'yes, using option 5, triptych - show exhibitions in showrooms 32, 35 and a selected third exhibition')])
    choosen_ext_exhibition_id = SelectField(choices=[(g['_id'], g['exhibition_name']) for g in ext_exhibition], coerce=ObjectId, label="Choose which external exhibition to highlight : ")
    internal_link = StringField('paste here the link of the page users should get to when they click on this homepage element')

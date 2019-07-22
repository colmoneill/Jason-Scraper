import os
import forms
from flask import Blueprint, render_template, abort,\
     url_for, redirect as redirect_flask, request, flash, Blueprint

from ..settings import db
from ..utils import login_required
from bson import ObjectId

from .. import settings, utils

from flask_wtf import Form
from flask_pagedown.fields import PageDownField
from wtforms import StringField, FileField, TextAreaField, RadioField, SelectField
from wtforms.validators import DataRequired

ext_exhibition = db.exhibitions.find({
    "is_published": True,
    "location": "external",
    })


class HomepageForm(Form):
    status = RadioField(u'Enable special homepage layout ?', choices = [
    ('opt1', 'no, use normal side by side exhibition layout, option 1'),
    ('opt2', 'yes, using option 2, highlight only the show at *32* Livornostraat'),
    ('opt3', 'yes, using option 3, highlight only the show at *35* Livornostraat'),
    ('opt4', 'yes, using option 4, highlight an external show')])
    choosen_ext_exhibition_id = SelectField(choices=[(g['_id'], g['exhibition_name']) for g in ext_exhibition], coerce=ObjectId, label="Choose which external exhibition to highlight : ")
    internal_link = StringField('paste here the link of the page users should get to when they click on this homepage element')

blueprint = Blueprint('homepage_management', __name__)

@blueprint.route("/", methods=['GET','POST'])
@login_required
def homepage_status():
    form = HomepageForm()
    # form.choosen_ext_exhibition_id.choices = [(g['_id'], g['exhibition_name']) for g in ext_exhibition]
    homepage_info = db.homepage.find_one({"_id": 'current_status'})
    print("choices:")
    print(form.choosen_ext_exhibition_id.choices)

    if form.validate_on_submit():
        formdata = form.data
        homepage_status = utils.handle_form_data({}, formdata)
        db.homepage.update({"_id":'current_status'},homepage_status, upsert=True)
        flash(u'You updated the homepage layout', 'success')
    return render_template('admin/homepage-management/index.html', ext_exhibition=ext_exhibition, form=form, homepage_info=homepage_info)


# str_choices = [(ext_exhibition[0]['_id'], ext_exhibition[0]['exhibition_name']),]
# str_choices = [('none', 'you are seeing this text because no exhibitions have been set to external')]
#
# quantity_ext_exhbition = db.exhibitions.find({
#     "is_published": True,
#     "location": "external",
#     }).count()
# print("amount of external exhibitions: ")
# print(quantity_ext_exhbition)
# if quantity_ext_exhbition == 1 :
#     str_choices = [(ext_exhibition[0]['_id'], ext_exhibition[0]['exhibition_name']),]
# if quantity_ext_exhbition == 2 :
#     str_choices = [
#     (ext_exhibition[0]['_id'], ext_exhibition[0]['exhibition_name']),
#     (ext_exhibition[1]['_id'], ext_exhibition[1]['exhibition_name']),
#     ]
# if quantity_ext_exhbition == 3:
#     str_choices = [
#     (ext_exhibition[0]['_id'], ext_exhibition[0]['exhibition_name']),
#     (ext_exhibition[1]['_id'], ext_exhibition[1]['exhibition_name']),
#     (ext_exhibition[2]['_id'], ext_exhibition[2]['exhibition_name']),
#     ]

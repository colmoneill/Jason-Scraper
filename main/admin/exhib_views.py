import os
import forms
from flask import Blueprint, render_template, abort,\
     url_for, redirect as redirect_flask, request, flash

from ..settings import db
from ..utils import login_required
from bson import ObjectId

from .. import settings, utils

blueprint = Blueprint('exhib_views', __name__)

@blueprint.route("/")
@login_required
def index():
    exhibition = db.exhibitions.find().sort([
            ("end", -1 ),
            ("start", -1 )
            ])
    return render_template('admin/exhib-views/index.html', exhibition=exhibition)

@blueprint.route("/list/<exhibition_id>")
@login_required
def individual_index(exhibition_id):
    exhibition = db.exhibitions.find_one({"_id": ObjectId(exhibition_id)})
    exhibition_view = db.exhibition.find()

    return render_template('admin/exhib-views/individual_index.html', exhibition=exhibition, exhibition_view=exhibition_view)

@blueprint.route("/update-views/<image_id>", methods=['GET', 'POST'])
@login_required
def update(image_id):
    image = db.exhibitions.find_one({"_id": ObjectId(image_id)})
    form = forms.ExhibitionView()

    if request.method == 'POST':
        if form.validate():
            formdata = form.data
            images = []
            images['path'] = image.path
            images['artist'] = form.artist.data
            images['exhbition_title'] = form.exhbition_title.data
            images['year'] = form.year.data
            images['institution'] = form.institution.data
            images['country'] = form.country.data

            db.exhibition.update(images)

            flash(u'You just updated this views meta data', 'success')
            return redirect_flask(url_for('.index'))

    else:
        form = forms.ExhibitionView(data=image)

    return render_template('admin/exhib-views/edit.html', image=image, form=form)


@blueprint.route("/delete/<image_id>", methods=['GET', 'POST'])
def delete(image_id):
    if request.method == 'POST':
        image = db.image.find_one({"_id": ObjectId(image_id)})
        os.remove(os.path.join(settings.appdir, image['path']))
        db.image.remove({"_id": ObjectId(image_id)})
        flash('You successfully deleted the image', 'success')
        return redirect_flask(url_for('.index'))

    return render_template('admin/image/delete.html')

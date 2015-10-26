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
    exhibition_views = db.exhibitions.find()
    return render_template('admin/exhib-views/index.html', exhibition_views=exhibition_views)

@blueprint.route("/update-views/<slug>", methods=['GET', 'POST'])
@login_required
def update(slug):
    image = db.exhibitions.find_one({"slug": slug})
    form = forms.ExhibitionView()

    if request.method == 'POST':
        if form.validate():
            formdata = form.data
            image = []
            image['path'] == image.path
            image['artist'] = form.artist.data
            image['exhbition_title'] = form.exhbition_title.data
            image['year'] = form.year.data
            image['institution'] = form.institution.data
            image['country'] = form.country.data

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
        #os.remove(os.path.join(settings.appdir, image['path']))
        db.exhibitions.remove({"_id": ObjectId(image_id)})
        flash('You successfully deleted the image', 'success')
        return redirect_flask(url_for('.index'))

    return render_template('admin/image/delete.html')

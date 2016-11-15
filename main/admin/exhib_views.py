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

@blueprint.route("/update/<image_id>", methods=['GET', 'POST'])
@login_required
def update(image_id):
    # Retreive exhibition which contains image
    exhibition = db.exhibitions.find_one({"images._id": ObjectId(image_id)})
    image = utils.find_where('_id', ObjectId(image_id), exhibition['images'])
    
    form = forms.ExhibitionView()

    if request.method == 'POST':
        if form.validate():
            formdata = form.data
            image['artist'] = form.artist.data
            image['exhibition_title'] = form.exhibition_title.data
            image['year'] = form.year.data
            image['institution'] = form.institution.data
            image['country'] = form.country.data

            db.exhibitions.update({'images._id': image['_id']}, {'$set': { 'images.$': image }})
            # Update the image if it's visible on an artist page
            db.artist.update({'selected_images._id': image['_id']}, {'$set': { 'selected_images.$': image }})
            
            flash(u'You just updated this views meta data', 'success')
            return redirect_flask(url_for('.individual_index', exhibition_id=str(exhibition['_id'])))

    else:
        form = forms.ExhibitionView(data=image)

    return render_template('admin/exhib-views/edit.html', image=image, form=form)


@blueprint.route("/delete/<image_id>", methods=['GET', 'POST'])
def delete(image_id):
    if request.method == 'POST':
        exhibition = db.exhibitions.find_one({"images._id": ObjectId(image_id)})
        image = utils.find_where('_id', ObjectId(image_id), exhibition['images'])
        os.remove(os.path.join(settings.appdir, image['path']))
        db.image.remove({"_id": ObjectId(image_id)})
        flash('You successfully deleted the image', 'success')
        return redirect_flask(url_for('.index'))

    return render_template('admin/image/delete.html')

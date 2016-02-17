import os
import forms
import config
from flask import Blueprint, render_template, abort,\
     url_for, redirect as redirect_flask, request, flash

from ..settings import db
from ..utils import login_required
from bson import ObjectId

from .. import settings, utils

blueprint = Blueprint('admin_artist_exhib_views', __name__)

@blueprint.route("/")
@login_required
def index():
    artists = db.artist.find().sort("artist_sort")
    return render_template('admin/artist-exhib-views/index.html', artists=artists)

@blueprint.route("/update/<view_id>", methods=['GET', 'POST'])
@login_required
def update(view_id):
    artist = db.artist.find_one({"views._id": ObjectId(view_id)})
    image = utils.find_where('_id', ObjectId(view_id), artist['views'])

    if image:
        form = forms.ArtistExhibitionView()

        if request.method == 'POST':
            if form.validate():
                formdata = form.data
                image['exhibition_title'] = form.exhibition_title.data
                image['year'] = form.year.data
                image['institution'] = form.institution.data
                image['city'] = form.city.data
                image['country'] = form.country.data

                db.artist.update({'views._id': image['_id']}, {'$set': { 'views.$': image }})
                db.artist.update({'selected_images._id': image['_id']}, {'$set': { 'selected_images.$': image }})

                artist = db.artist.find_one({"_id": artist['_id']})
                db.exhibitions.update({"artist._id": artist['_id']}, {"$set": { "artist": artist }}, multi=True)
                ## Should update this artist on group exhibitions as well
                db.exhibitions.update({"artists._id": artist['_id']}, {"$set": {"artists.$": artist}}, multi=True)

                flash(u'You just updated this images meta data', 'success')
                return redirect_flask(url_for('.index'))

        else:
            form = forms.ArtistExhibitionView(data=image)

    return render_template('admin/artist-exhib-views/edit.html', image=image, form=form)

@blueprint.route("/delete/<view_id>", methods=['GET', 'POST'])
def delete(view_id):
    if request.method == 'POST':
        artist = db.artist.find_one({"views._id": ObjectId(view_id)})
        image = utils.find_where('_id', ObjectId(view_id), artist['views'])
        os.remove(os.path.join(settings.appdir, image['path']))
        db.artist.update({ '_id': artist['_id'] }, { '$pull': { 'views': {'_id': image['_id'] }, 'selected_images': {'_id': image['_id'] } } });

        artist = db.artist.find_one({"_id": artist['_id']})
        db.exhibitions.update({"artist._id": artist['_id']}, {"$set": { "artist": artist }}, multi=True)
        ## Should update this artist on group exhibitions as well
        db.exhibitions.update({"artists._id": artist['_id']}, {"$set": {"artists.$": artist}}, multi=True)

        flash('You successfully deleted the image', 'success')
        return redirect_flask(url_for('.index'))

    return render_template('admin/artist-exhib-views/delete.html')

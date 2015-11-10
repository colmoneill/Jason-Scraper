import os
import forms
import config
from flask import Blueprint, render_template, abort,\
     url_for, redirect as redirect_flask, request, flash

from ..settings import db
from ..utils import login_required
from bson import ObjectId

from .. import settings, utils

blueprint = Blueprint('admin_image', __name__)

@blueprint.route("/")
@login_required
def index():
    form = forms.Image()
    form.artist.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find().sort("artist_sort")]
    artists = db.artist.find().sort("artist_sort")
    return render_template('admin/image/index.html', artists=artists, form=form)

@blueprint.route("/create/", methods=['GET', 'POST'])
@login_required
def create():
    form = forms.Image()
    form.artist.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find().sort("artist_sort")]

    if form.validate_on_submit():
        formdata = form.data

        artist = db.artist.find_one({'_id': ObjectId(formdata['artist'])})

        image = {
            '_id': ObjectId(),
            'path': utils.handle_uploaded_file(
                request.files['image_file'],
                config.upload['ARTWORK_IMAGE'],
                utils.setfilenameroot(request.files['image_file'].filename, artist['slug'])
            ),
            'published': True,
            'title': form.title.data,
            'year': form.year.data,
            'medium': form.medium.data,
            'dimensions': form.dimensions.data,
            'edition': form.edition.data
        }

        artist['images'].append(image)

        db.artist.update({"_id": ObjectId(formdata['artist'])}, artist)
        ## Update this artist on exhibitions as well
        db.exhibitions.update({"artist._id": ObjectId(formdata['artist'])}, {"$set": { "artist": artist }}, multi=True)
        ## Should update this artist on group exhibitions as well
        db.exhibitions.update({"artists._id": ObjectId(formdata['artist'])}, {"$set": {"artists.$": artist}}, multi=True)

        flash(u'You successfully added an image', 'success')
        return redirect_flask(url_for('.index'))

    return render_template('admin/image/create.html', form=form)

@blueprint.route("/update/<image_id>", methods=['GET', 'POST'])
@login_required
def update(image_id):
    artist = db.artist.find_one({"images._id": ObjectId(image_id)})
    image = utils.find_where('_id', ObjectId(image_id), artist['images'])

    if image:
        form = forms.ImageUpdate()

        if request.method == 'POST':
            if form.validate():
                formdata = form.data
                image['stock_number'] = form.stock_number.data
                image['title'] = form.title.data
                image['year'] = form.year.data
                image['medium'] = form.medium.data
                image['dimensions'] = form.dimensions.data
                image['edition'] = form.edition.data

                db.artist.update({'images._id': image['_id']}, {'$set': { 'images.$': image }})
                db.exhibitions.update({'artworks._id': image['_id']}, {'$set': { 'artworks.$': image }}, multi=True)

                artist = db.artist.find_one({"_id": artist['_id']})
                db.exhibitions.update({"artist._id": artist['_id']}, {"$set": { "artist": artist }}, multi=True)
                ## Should update this artist on group exhibitions as well
                db.exhibitions.update({"artists._id": artist['_id']}, {"$set": {"artists.$": artist}}, multi=True)

                flash(u'You just updated this images meta data', 'success')
                return redirect_flask(url_for('.index'))

        else:
            form = forms.ImageUpdate(data=image)

    return render_template('admin/image/edit.html', image=image, form=form)


@blueprint.route("/delete/<image_id>", methods=['GET', 'POST'])
def delete(image_id):
    if request.method == 'POST':
        artist = db.artist.find_one({"images._id": ObjectId(image_id)})
        image = utils.find_where('_id', ObjectId(image_id), artist['images'])
        os.remove(os.path.join(settings.appdir, image['path']))
        db.artist.update({ '_id': artist['_id'] }, { '$pull': { 'images': {'_id': image['_id'] } } });
        db.exhibitions.update({}, { '$pull': { 'artworks': {'_id': image['_id'] } } }, multi=True);

        artist = db.artist.find_one({"_id": artist['_id']})
        db.exhibitions.update({"artist._id": artist['_id']}, {"$set": { "artist": artist }}, multi=True)
        ## Should update this artist on group exhibitions as well
        db.exhibitions.update({"artists._id": artist['_id']}, {"$set": {"artists.$": artist}}, multi=True)

        flash('You successfully deleted the image', 'success')
        return redirect_flask(url_for('.index'))

    return render_template('admin/image/delete.html')

import os
import forms
import config
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
    form = forms.externalExhibitionView()
    form.artists.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find().sort("artist_sort")]
    artists = db.artist.find().sort("artist_sort")
    exhibition = db.exhibitions.find().sort([
            ("end", -1 ),
            ("start", -1 )
            ])
    return render_template('admin/exhib-views/index.html', form=form, artist=artist, exhibition=exhibition)

@blueprint.route("/list/<exhibition_id>")
@login_required
def individual_index(exhibition_id):
    exhibition = db.exhibitions.find_one({"_id": ObjectId(exhibition_id)})
    exhibition_view = db.exhibition.find()

    return render_template('admin/exhib-views/individual_index.html', exhibition=exhibition, exhibition_view=exhibition_view)

@blueprint.route("/create", methods=['GET', 'POST'])
@login_required
def create():
    form = forms.externalExhibitionView()
    form.artists.choices = [(str(artist['_id']), artist['name']) for artist in   db.artist.find().sort("artist_sort")]

    if form.validate_on_submit():
        formdata = form.data
        # artist = db.artist.find_one({'_id': ObjectId(formdata['artists'])})

        externalExhibitionView = {
            '_id': ObjectId(),
            'path': utils.handle_uploaded_file(
                request.files['image_file'],
                config.upload['EXTERNAL_EXHIBITION_VIEW'],
                utils.setfilenameroot(request.files['image_file'].filename, artist['slug'])
                ),
            'external_exhibiton_view': True,
            'published': True,
            'exhibition_title': form.exhibition_title.data,
            'year': form.year.data,
            'institution': form.institution.data,
            'city': form.city.data,
            'country': form.country.data,
        }

        artist['external_exhibition_view'].append(externalExhibitionView)

        ##db.artist.update({"_id": ObjectId(formdata['artist'])}, artist)
        ## Update this artist on exhibitions as well
        #db.exhibitions.update({"artist._id": ObjectId(formdata['artist'])}, {"$set": { "artist":    artist }}, multi=True)
        ## Should update this artist on group exhibitions as well
        #db.exhibitions.update({"artists._id": ObjectId(formdata['artist'])}, {"$set":   {"artists.$": artist}}, multi=True)

        flash(u'You successfully added an external exhibition view', 'success')
        return redirect_flask(url_for('.index'))

    return render_template('admin/exhib-views/create.html', form=form, artist=artist)

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
            image['exhbition_title'] = form.exhibition_title.data
            image['year'] = form.year.data
            image['institution'] = form.institution.data
            image['country'] = form.country.data

            db.exhibitions.update({'images._id': image['_id']}, {'$set': { 'images.$': image }})

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

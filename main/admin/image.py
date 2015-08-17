import forms
from flask import Blueprint, render_template, abort,\
     url_for, redirect as redirect_flask, request, flash
 
from ..settings import db
from utils import login_required
from bson import ObjectId

blueprint = Blueprint('admin_image', __name__)

@blueprint.route("/")
@login_required
def index():
    form = forms.Image()
    form.artist.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]
    images = db.image.find()

    return render_template('admin/image/index.html', images=images, form=form)

@blueprint.route("/create/", methods=['GET', 'POST'])
@login_required
def create():
    form = forms.Image()
    form.artist.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]

    if form.validate_on_submit():
        formdata = form.data


        image = {
            'artist': db.artist.find_one({'_id': ObjectId(formdata['artist'])}),
            'path': utils.handle_uploaded_file(
                request.files['image_file'],
                app.config['UPLOAD']['ARTWORK_IMAGE'],
            ),
            'title': form.title.data,
            'year': form.year.data,
            'medium': form.medium.data,
            'dimensions': form.dimensions.data,
        }
        db.image.insert(image)
        flash(u'You successfully added an image', 'success')
        return redirect_flask(url_for('.index'))

    return render_template('admin/image/create.html', form=form)

@blueprint.route("/update/<image_id>", methods=['GET', 'POST'])
@login_required
def update(image_id):
    image = db.image.find_one({"_id": ObjectId(image_id)})
    form = forms.ImageUpdate()
    form.artist.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]
    
    if request.method == 'POST':
        if form.validate():
            formdata = form.data
            image['title'] = form.title.data
            image['year'] = form.year.data
            image['medium'] = form.medium.data
            image['dimensions'] = form.dimensions.data
            image['artist'] = db.artist.find_one({'_id': ObjectId(form.artist.data)})
            
            db.image.update({"_id": ObjectId(image_id)}, image)

            flash(u'You just updated this images meta data', 'success')
            return redirect_flask(url_for('.index'))

    else:
        image['artist'] = str(image['artist']['_id'])
        form = forms.ImageUpdate(data=image)
        form.artist.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]

    return render_template('admin/image/edit.html', image=image, form=form)


@blueprint.route("/delete/<image_id>", methods=['GET', 'POST'])
def delete(image_id):
    if request.method == 'POST':
        image = db.image.find_one({"_id": ObjectId(image_id)})
        os.remove(image['path'])
        db.image.remove({"_id": ObjectId(image_id)})
        flash('You successfully deleted the image')
        return redirect_flask(url_for('listImages'))

    return render_template('admin/image/delete.html')

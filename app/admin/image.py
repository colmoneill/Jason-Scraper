from flask import Blueprint, render_template, abort

blueprint = Blueprint('admin_image', __name__, template_folder='../../template/admin/image')

@blueprint.route("/")
def index():
    form = forms.Image()
    form.artist.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]
    images = db.image.find()

    return render_template('admin/image/index.html', images=images, form=form)

@blueprint.route("/create/", methods=['GET', 'POST'])
def createImage():
    form = forms.Image()
    form.artist.choices = [(str(artist['_id']), artist['name']) for artist in db.artist.find()]

    if form.validate_on_submit():
        formdata = form.data
        image = {
            'artist': db.artist.find_one({'_id': ObjectId(formdata['artist'])}),
            'path': utils.handle_uploaded_file(
                request.files['image_file'],
                app.config['UPLOAD']['ARTWORK_IMAGE']
            )
        }
        db.image.insert(image)

        return redirect_flask(url_for('listImages'))

    return render_template('admin/image/create.html', form=form)

@blueprint.route("/delete/<image_id>", methods=['GET', 'POST'])
def delete(image_id):
    if request.method == 'POST':
        image = db.image.find_one({"_id": ObjectId(image_id)})
        os.remove(image['path'])
        db.image.remove({"_id": ObjectId(image_id)})
        flash('You successfully deleted the image')
        return redirect_flask(url_for('listImages'))

    return render_template('admin/image/delete.html')



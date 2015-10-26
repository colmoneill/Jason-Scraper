import settings
import utils
import shutil
import os.path
import re
from bson import ObjectId

for exhibition in settings.db.exhibitions.find():
    if not exhibition['slug'] and 'is_group_expo' not in exhibition:
        filenamebase = exhibition['artist']['slug'] + '-' + exhibition['start'].strftime('%d-%m-%Y')
        
        if 'images' in exhibition:
            for key, image in enumerate(exhibition['images']):
                if image['path'] and re.test(r"jpg\-\d+", image.['path']):
                    newpath = utils.getsafepath('static/uploads/exhibition-view/' + filenamebase + '.jpg')
                    shutil.move(os.path.join(settings.appdir, image['path']), os.path.join(settings.appdir, newpath))
                    exhibition['images'][key]['path'] = newpath
        
        if 'press_release' in exhibition and exhibition['press_release']:
            newpath = utils.getsafepath('static/uploads/press/' + filenamebase + '.pdf')
            shutil.move(os.path.join(settings.appdir,exhibition['press_release']), os.path.join(settings.appdir,newpath))
            exhibition['press_release'] = newpath

        settings.db.exhibitions.update({"_id": exhibition['_id']}, exhibition)
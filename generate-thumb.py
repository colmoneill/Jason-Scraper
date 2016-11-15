from main.settings import db
from PIL import Image
import glob, os

for artist in db.artist.find():
    for item in artist['images']:
        path = item['path']
        try:
            im = Image.open(path)
            im.thumbnail((240, 160), Image.ANTIALIAS)
            folder, name = os.path.split(path)
            base, ext = os.path.splitext(name)
            outpath = os.path.join(folder, base+"-thumb"+ext)
            print outpath
            if not os.path.exists(outpath):
                db.artist.update({'selected_images._id': item['_id']}, {'$set': { 'selected_images.$.thumbpath': outpath }})
                db.artist.update({'images._id': item['_id']}, {'$set': { 'images.$.thumbpath': outpath }})
                db.artist.update({'views._id': item['_id']}, {'$set': { 'views.$.thumbpath': outpath }})
                db.exhibitions.update({'artworks._id': item['_id']}, {'$set': { 'artworks.$.thumbpath': outpath }}, multi=True)

                artist = db.artist.find_one({"_id": artist['_id']})
                db.exhibitions.update({"artist._id": artist['_id']}, {"$set": { "artist": artist }}, multi=True)
                ## Should update this artist on group exhibitions as well
                db.exhibitions.update({"artists._id": artist['_id']}, {"$set": {"artists.$": artist}}, multi=True)

                im.save(outpath)
        except IOError:
            print "image corrupt; skipping"

for artist in db.artist.find():
    for item in artist['views']:
        path = item['path']
        try:
            im = Image.open(path)
            im.thumbnail((240, 160), Image.ANTIALIAS)
            folder, name = os.path.split(path)
            base, ext = os.path.splitext(name)
            outpath = os.path.join(folder, base+"-thumb"+ext)
            print outpath
            if not os.path.exists(outpath):
                db.artist.update({'views._id': item['_id']}, {'$set': { 'views.$.thumbpath': outpath }})
                im.save(outpath)
        except IOError:
            print "image corrupt; skipping"

        #db.artist.update({'images._id': image['_id']}, {'$set': { 'images.$': image }})
        #db.artist.update({'selected_images._id': image['_id']}, {'$set': { 'selected_images.$': image }})
        #db.exhibitions.update({'artworks._id': image['_id']}, {'$set': { 'artworks.$': image }}, multi=True)

        #artist = db.artist.find_one({"_id": artist['_id']})
        #db.exhibitions.update({"artist._id": artist['_id']}, {"$set": { "artist": artist }}, multi=True)
        ### Should update this artist on group exhibitions as well
        #db.exhibitions.update({"artists._id": artist['_id']}, {"$set": {"artists.$": artist}}, multi=True)


# 15:31:23 - gdh: So when you generate thumbs for artist.images you also want to update exhibitions.artworks
# 15:32:56 - gdh: Actually, you can take the logic from main/admin/image.py line 51 -> 55
# 15:34:08 - gdh: I'm sorry line 81 to 88. That involves the same arrays, collections etc.
# 15:35:05 - gdh: You could then do the same for artist_exhib_views, which are the external exhibition views and exhib_views, which are the internal exhibition views. If I understand it well

#for image in glob.glob(os.path.join(infolder, "*.jpg")):
#    path, name = os.path.split(image)
#    base, ext = os.path.splitext(name)
#    im = Image.open(image)
    #print im
    #try:
    #    im = Image.open(image)
    #    print "generating reg thumbnail " + (outfolder) + (name)
    #    im.thumbnail((240, 160), Image.ANTIALIAS)
    #    outpath_reg = os.path.join(outfolder, base+".jpg")
    #    if not os.path.exists(outpath_reg):
    #        print(outpath_reg)
    #        im.save(outpath_reg)
    #        settings.db.image.insert(reg_thumb_path = outpath_reg)
    #    im = Image.open(image)
    #    print "generating big thumbnail " + (outfolder2) + (name)
    #    im.thumbnail((480, 320), Image.ANTIALIAS)
    #    outpath_big = os.path.join(outfolder2, base+".jpg")
    #    if not os.path.exists(outpath_big):
    #        print(outpath_big)
    #        im.save(outpath_big)
    #except IOError:
    #    print "image corrupt; skipping"

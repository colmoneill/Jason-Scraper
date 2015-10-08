import settings
from PIL import Image
import glob, os

infolder = "static/uploads/artworks"
outfolder = "static/uploads/artworks/thumbs-reg/"
outfolder2 = "static/uploads/artworks/thumbs-big/"

for f in glob.glob(os.path.join(infolder, "*.jpg")):
    path, name = os.path.split(f)
    base, ext = os.path.splitext(name)
    try:
        im = Image.open(f)
        print "generating reg thumbnail" + (name)
        im.thumbnail((240, 160), Image.ANTIALIAS)
        outpath_reg = os.path.join(outfolder, base+".jpg")
        if not os.path.exists(outpath_reg):
            print(outpath_reg)
            im.save(outpath_reg)
            settings.db.image.insert(reg_thumb_path = outpath_reg)
        im = Image.open(f)
        print "generating big thumbnail" + (name)
        im.thumbnail((480, 320), Image.ANTIALIAS)
        outpath_big = os.path.join(outfolder2, base+".jpg")
        if not os.path.exists(outpath_big):
            print(outpath_big)
            im.save(outpath_big)
    except IOError:
        print "image corrupt; skipping"

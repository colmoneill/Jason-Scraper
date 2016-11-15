from PIL import Image
import glob, os

infolder = "static/uploads/artworks"
infolder2 = "static/uploads/cover"
infolder3 = "static/uploads/exhibition-cover"
infolder4 = "static/uploads/exhibition-view"
outfolder = "static/thumbs/"

for image in glob.glob(os.path.join(infolder, "*.jpg")):
    path, name = os.path.split(image)
    base, ext = os.path.splitext(name)
    try:
        im = Image.open(image)
        print "generating reg thumbnail " + (outfolder) + (name)
        im.thumbnail((240, 160), Image.ANTIALIAS)
        outpath = os.path.join(outfolder, base+ext)
        if not os.path.exists(outpath_reg):
            im.save(outpath)
    except IOError:
        print "image corrupt; skipping"

for image in glob.glob(os.path.join(infolder2, "*.jpg")):
    path, name = os.path.split(image)
    base, ext = os.path.splitext(name)
    try:
        im = Image.open(image)
        print "generating reg thumbnail " + (outfolder) + (name)
        im.thumbnail((240, 160), Image.ANTIALIAS)
        outpath = os.path.join(outfolder, base+ext)
        if not os.path.exists(outpath_reg):
            im.save(outpath)
    except IOError:
        print "image corrupt; skipping"

for image in glob.glob(os.path.join(infolder3, "*.jpg")):
    path, name = os.path.split(image)
    base, ext = os.path.splitext(name)
    try:
        im = Image.open(image)
        print "generating reg thumbnail " + (outfolder) + (name)
        im.thumbnail((240, 160), Image.ANTIALIAS)
        outpath = os.path.join(outfolder, base+ext)
        if not os.path.exists(outpath_reg):
            im.save(outpath)
    except IOError:
        print "image corrupt; skipping"

for image in glob.glob(os.path.join(infolder4, "*.jpg")):
    path, name = os.path.split(image)
    base, ext = os.path.splitext(name)
    try:
        im = Image.open(image)
        print "generating reg thumbnail " + (outfolder) + (name)
        im.thumbnail((240, 160), Image.ANTIALIAS)
        outpath = os.path.join(outfolder, base+ext)
        if not os.path.exists(outpath_reg):
            im.save(outpath)
    except IOError:
        print "image corrupt; skipping"

import settings
import utils
import shutil
import os.path
import re
from bson import ObjectId
from PIL import Image
import glob, os

infolder = "static/uploads/artworks"
outfolder = "static/uploads/artworks/thumbs-reg/"
outfolder2 = "static/uploads/artworks/thumbs-big/"


for f in glob.glob(os.path.join(infolder, "*.jpg")):
    path, name = os.path.split(f)
    base, ext = os.path.splitext(name)
    im = Image.open(f)
    im.thumbnail((240, 160), Image.ANTIALIAS)
    outpath_reg = os.path.join(outfolder, base+"-thumb240.jpg")
    if not os.path.exists(outpath_reg):
        print(outpath_reg)
        im.save(outpath_reg)

# for f in glob.glob(os.path.join(infolder, "*.jpg")):
#     path, name = os.path.split(f)
#     base, ext = os.path.splitext(name)
#     im = Image.open(f)
#     im.thumbnail((480, 320), Image.ANTIALIAS)
#     outpath_big = os.path.join(outfolder, base+"-thumb480.jpg")
#     image['big_thumb_path'] = outpath_big
#     if not os.path.exists(outpath_big):
#         print(outpath_big)
#         im.save(outpath_big)
#

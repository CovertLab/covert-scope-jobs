#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import imread
from os.path import join
from glob import glob
import sys
import os
from os.path import join, dirname
import tifffile as tiff

sys.path.append('/home/adi/covert/CellTK')
sys.path.append('/home/adi/covert/CellTK/celltk')
sys.path.append('/home/adi/covert/CellTK/celltk/utils')
from preprocess_operation import shading_correction

from PIL import Image
from PIL.TiffTags import TAGS
import json


refpath = 'http://archive.simtk.org/ktrprotocol/temp/ffref_{0}x{1}bin.npz'.format(magnification, binning)
darkrefpath = 'http://archive.simtk.org/ktrprotocol/temp/ffdarkref_{0}x{1}bin.npz'.format(magnification, binning)
ref, darkref = retrieve_ff_ref(refpath, darkrefpath)

def correct_shade(img, ref, darkref, ch):
    img = img.astype(np.float)
    d0 = img.astype(np.float) - darkref[ch]
    d1 = ref[ch] - darkref[ch]
    return d1.mean() * d0/d1


imgpath = sys.argv[1] # NOTE: assume full path e.g. /scratch/blah/blah/blah/image.tif

with Image.open(imgpath) as img:
    # metadata extraction
    meta_dict = {TAGS[key] : img.tag[key] for key in img.tag.iterkeys()}
    meta_dict['IMAGE_PATH'] = imgpath
    meta_path = dirname(imgpath)+"/files_metadata.json"
    with open(meta_path, "a") as j:
        j.write(json.dumps(meta_dict))

    #flatfielding
    with open(join(dirname(imgpath), 'metadata.txt')) as mfile:
        data = json.load(mfile)
        channels = data['Summary']['ChNames']
        for chnum, ch in enumerate(channels):
            try:
                img_sc = correct_shade(imread(path), ref, darkref, ch)
            except:
                img_sc = img
    tiff.imsave(imgpath, img_sc.astype(np.float32))



#!/usr/bin/python

import numpy as np
from scipy.ndimage import imread
from os.path import join
from glob import glob                                                                             
import ast                                                                             
import sys
import os
from os.path import join, dirname
import tifffile as tiff
from tifffile import TiffFile
from urllib.request import urlretrieve
import tempfile
import shutil

sys.path.append('/home/adi/covert/CellTK')
sys.path.append('/home/adi/covert/CellTK/celltk')
sys.path.append('/home/adi/covert/CellTK/celltk/utils')
# from preprocess_operation import shading_correction

from PIL import Image
from PIL.TiffTags import TAGS
import json


def retrieve_ff_ref(refpath, darkrefpath):
    """
    refpath: 'http://archive.simtk.org/ktrprotocol/temp/ffref_20x3bin.npz'
    darkrefpath: 'http://archive.simtk.org/ktrprotocol/temp/ffdarkref_20x3bin.npz'
    """
    try:
        temp_dir = tempfile.mkdtemp()
        urlretrieve(refpath, join(temp_dir, 'ref.npz'))
        ref = np.load(join(temp_dir, 'ref.npz'))
        urlretrieve(darkrefpath, join(temp_dir, 'darkref.npz'))
        darkref = np.load(join(temp_dir, 'darkref.npz'))
    finally:
        shutil.rmtree(temp_dir)  # delete directory
    return ref, darkref

def correct_shade(img, ref, darkref, ch):
    img = img.astype(np.float)
    d0 = img.astype(np.float) - darkref[ch]
    d1 = ref[ch] - darkref[ch]
    return d1.mean() * d0/d1



imgpath = sys.argv[1] # NOTE: assume full path e.g. /scratch/blah/blah/blah/image.tif


# metadata extraction
with TiffFile(imgpath) as tif:
    md = tif.imagej_metadata
    info = ast.literal_eval(md['Info'])
    try:
        binning = int(info['Neo-Binning']['PropVal'][0])
    except:
        binning = 3
    try:
        magnification = int(info['TINosePiece-Label']['PropVal'][11:13])
    except:
        magnification = 20
    try:
        exposure = int(info['Exposure-ms'])
    except:
        exposure = -1

# flatfielding
refpath = 'http://archive.simtk.org/ktrprotocol/temp/ffref_{0}x{1}bin.npz'.format(magnification, binning)
darkrefpath = 'http://archive.simtk.org/ktrprotocol/temp/ffdarkref_{0}x{1}bin.npz'.format(magnification, binning)
try:
    ref, darkref = retrieve_ff_ref(refpath, darkrefpath)
except:
    refpath = 'http://archive.simtk.org/ktrprotocol/temp/ffref_{0}x{1}bin.npz'.format(20, 3)
    darkrefpath = 'http://archive.simtk.org/ktrprotocol/temp/ffdarkref_{0}x{1}bin.npz'.format(20, 3)
    ref, darkref = retrieve_ff_ref(refpath, darkrefpath)

with open(join(dirname(imgpath), 'metadata.txt')) as mfile:
    data = json.load(mfile)

    # flatfielding
    channels = data['Summary']['ChNames']
    for chnum, ch in enumerate(channels):
        try:
            img_sc = correct_shade(tiff.imread(imgpath), ref, darkref, ch)
        except:
            img+sc = tiff.imread(imgpath)
    tiff.imsave(imgpath, np.array(img_sc, np.float32))

    # metadata dumping
    if 'filedata' in data:
        data['filedata'][imgpath] = {'binning' : binning, 
                                 'magnification' : magnification, 
                                 'exposure' : exposure}
    else:
        data ['filedata'] = {imgpath : {'binning' : binning, 
                                        'magnification' : magnification, 
                                        'exposure' : exposure}}

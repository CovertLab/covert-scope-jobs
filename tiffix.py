#!/usr/bin/python

"""
TODO: fix metadata so that it can be read out in ImageJ. 
      Currently Tifffile can read it but not ImageJ.
TODO: d1.mean() * d0/d1 is arbitrary, which possibly causes an issue if saved in uint16.
TODO: collect more shading correction reference.
"""



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
try:
    from urllib.request import urlretrieve
except:
    from urllib import urlretrieve
import tempfile
import shutil
import re
import json
import multiprocessing
import math


ch_table = {('FITC', 'FITC'): 'FITC',
            ('mCherry', 'mCherry'): 'CHERRY',
            ('CFP', 'CFP'): 'CFP',
            ('YFP', 'YFP'): 'YFP',
            ('DAPI', 'DAPI'): 'DAPI',
            ('TRITC', 'TRITC'): 'TRITC',
            ('Far-Red', 'Far-Red'): 'FAR-RED',
            ('Orange', 'Orange'): 'Orange',
            ('Hoechst', 'DAPI'): 'AMCA',
            ('CFP', 'YFP'): 'FRET'}


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


def run_correct_shade(tif, md):
    info = ast.literal_eval(md['Info'])
    binning = int(info['Neo-Binning']['PropVal'][0])
    magnification = int(re.search("([0-9]*)x.*", info['TINosePiece-Label']['PropVal']).groups(0)[0])
    exposure = int(info['Exposure-ms'])
    emission_label = info['Emission Filter-Label']['PropVal']
    excitation_label = info['Excitation Filter-Label']['PropVal']

    # flatfielding
    # refpath = 'http://archive.simtk.org/ktrprotocol/temp/ffref_{0}x{1}bin.npz'.format(magnification, binning)
    # darkrefpath = 'http://archive.simtk.org/ktrprotocol/temp/ffdarkref_{0}x{1}bin.npz'.format(magnification, binning)
    refpath = 'data/ffref_{0}x{1}bin.npz'.format(magnification, binning)
    darkrefpath = 'data/ffdarkref_{0}x{1}bin.npz'.format(magnification, binning)

    try:
        ref, darkref = retrieve_ff_ref(refpath, darkrefpath)
    except:
        ref, darkref = None, None

    try:
        emission_label =  re.search(r"\(([A-Za-z0-9_-]+)\)", emission_label).groups(0)[0]
        excitation_label =  re.search(r"\(([A-Za-z0-9_-]+)\)", excitation_label).groups(0)[0]
        ch = ch_table[excitation_label, emission_label]
    except:
        emission_label, excitation_label = None, None

    md['tk_info'] = info
    md['postprocess'] = 'shading_correction'

    img_sc = tif.asarray()
    if ref is not None or emission_label is not None:
        try:
            img_sc = correct_shade(img_sc, ref, darkref, ch)
            img_sc[img_sc < 0] = 0
        except:
            pass  # channel is probably not existed in ref.
    return img_sc.astype(np.uint16), md


def _main(imgpath):
    with TiffFile(imgpath) as tif:
        md = tif.imagej_metadata
        img_sc = tif.asarray()
        if "Info" in md:
            img_sc, md = run_correct_shade(tif, md)
        elif 'postprocess' in md:
            if md['postprocess'] == 'shading_correction':
                return
        tiff.imsave(imgpath, img_sc, imagej=True,
                    metadata=md, compress=9)


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


if __name__ == "__main__":
    tiffile = sys.argv[1] # NOTE: assume full path e.g. /scratch/blah/blah/blah/image.tif
    with open(tiffile) as f:
        content = f.readlines()
    content = [x.strip() for x in content]

    num_cores = 7

    split_lists = list(chunks(content, int(math.ceil(len(content)/num_cores))))
    pool = multiprocessing.Pool(num_cores, maxtasksperchild=1)
    pool.map(single_call, split_lists, chunksize=1)
    pool.close()
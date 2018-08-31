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


def correct_shade(img, ref, darkref):
    img = img.astype(np.float)
    d0 = img.astype(np.float) - darkref
    d1 = ref - darkref
    return d1.mean() * d0/d1


def run_correct_shade(tif, md, reffile, darkreffile):
    info = ast.literal_eval(md['Info'])
    binning = int(info['Neo-Binning']['PropVal'][0])
    magnification = int(re.search("([0-9]*)x.*", info['TINosePiece-Label']['PropVal']).groups(0)[0])
    exposure = int(info['Exposure-ms'])
    emission_label = info['Emission Filter-Label']['PropVal']
    excitation_label = info['Excitation Filter-Label']['PropVal']

    try:
        emission_label =  re.search(r"\(([A-Za-z0-9_-]+)\)", emission_label).groups(0)[0]
        excitation_label =  re.search(r"\(([A-Za-z0-9_-]+)\)", excitation_label).groups(0)[0]
        ch = ch_table[excitation_label, emission_label]
    except:
        emission_label, excitation_label = None, None

    md['tk_info'] = info
    md['postprocess'] = 'shading_correction'

    img_sc = tif.asarray()
    if emission_label is not None:
        try:
            ref = reffile['{0}x_{1}bin_{2}'.format(magnification, binning, ch)]
            darkref = darkreffile['{0}x_{1}bin_{2}'.format(magnification, binning, ch)]
            img_sc = correct_shade(img_sc, ref, darkref)
            img_sc[img_sc < 0] = 0
        except:
            pass  # channel is probably not existed in ref.
    return img_sc.astype(np.uint16), md


def call_process(imgpath, reffile, darkreffile):
    with TiffFile(imgpath) as tif:
        md = tif.imagej_metadata
        img_sc = tif.asarray()
        if "Info" in md:
            img_sc, md = run_correct_shade(tif, md, reffile, darkreffile)
        elif 'postprocess' in md:
            if md['postprocess'] == 'shading_correction':
                return
        tiff.imsave(imgpath, img_sc, imagej=True,
                    metadata=md, compress=9)

reffile = dict(np.load('data/ref.npz'))
darkreffile = dict(np.load('data/darkref.npz'))

def _main(imgpath_list):
    #import time
    #time.sleep(np.random.randint(10))
    r0 = reffile.copy()
    r1 = darkreffile.copy()
    #call_process(imgpath_list[0], r0, r1)
    for imgpath in imgpath_list:
        try:
            call_process(imgpath, r0, r1)
        except:
            with open('error.txt', 'a') as f:
                f.write(imgpath+'\n')


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


if __name__ == "__main__":
    tiffile = sys.argv[1] # NOTE: assume full path e.g. /scratch/blah/blah/blah/image.tif
    with open(tiffile) as f:
        content = f.readlines()
    content = [x.strip() for x in content]

    import time

    start = time.time()

    num_cores = 7
    split_lists = list(chunks(content, int(math.ceil(len(content)/num_cores))))
    pool = multiprocessing.Pool(num_cores, maxtasksperchild=1)
    pool.map(_main, split_lists, chunksize=1)
    pool.close()

    end = time.time()
    print end - start, len(content)
   #_main(split_lists[1])

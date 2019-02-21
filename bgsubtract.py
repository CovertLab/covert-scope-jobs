#!/usr/bin/python

"""

"""



import numpy as np
from scipy.ndimage import imread
from os.path import join
from glob import glob
import ast
import sys
import os
from os.path import join, dirname, abspath
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
from functools import partial



def call_subtract(imgpath, bgdict):
    r = re.search('.*img_channel([0-9]*)', imgpath)
    chnum = int(r.groups()[0])
    with TiffFile(imgpath) as tif:
        md = tif.imagej_metadata
        img_sc = tif.asarray()
        if 'bg_subtract' in md:
            print "already subtracted"
            return
        else:
            img_sc = img_sc - bgdict[chnum]
            md['bg_subtract'] = 'Done'
            tiff.imsave(imgpath, img_sc.astype(np.float32), imagej=True,
                        metadata=md, compress=9)


def _subtract(imgpath_list, bgdict):
    for imgpath in imgpath_list:
        try:
            call_subtract(imgpath, bgdict)
        except IOError:
            with open('corrupted.txt', 'a') as f:
                f.write(imgpath+'\n')
        except:
            with open('error.txt', 'a') as f:
                f.write(imgpath+'\n')


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def parse_image_files(inputs):
    if "/" not in inputs:
        return (inputs, )
    store = []
    li = []
    while inputs:
        element = inputs.pop(0)
        if element == "/":
            store.append(li)
            li = []
        else:
            li.append(element)
    store.append(li)
    return zip(*store)


def _parse_command_line_args():
    """
    image:  Path to a tif or png file (e.g. data/nuc0.png).
            To pass multiple image files (size can be varied), use syntax like
            "-i im0.tif / im1.tif / im2.tif", and pass the same number of labels.
    labels: (e.g. data/labels0.tif)
    nsteps: A number of steps per epoch. A total patches passed to a model will be
            batch * nsteps.
    batch:  Typically 10-32? This will affect a memory usage.
    """

    import argparse
    parser = argparse.ArgumentParser(description='predict')
    parser.add_argument('-i', '--image', help='folder containing images', nargs="*")
    parser.add_argument('-b', '--backgrounds', help='folder containing background images', nargs="*")
    # parser.add_argument('-o', '--output', default='.', help='output directory')
    return parser.parse_args()


def _main():
    args = _parse_command_line_args()
    images = parse_image_files(args.image)[0][0]
    backgrounds = parse_image_files(args.backgrounds)[0]
    background_subtraction(images, backgrounds)



def calc_background(bgdirlist):
    content = []
    print bgdirlist
    for bgdir in bgdirlist:
        for dirname, subdirlist, filelist in os.walk(bgdir):
            for i in filelist:
                if i.endswith('.tif'):
                    content.append(join(dirname, i))

    bgdict = {}
    c = 0
    while True:
        r = re.compile('.*img_channel{0:03}'.format(c))
        pathlist = filter(r.match, content)
        if pathlist:
            imlist = [tiff.imread(i) for i in pathlist]
            ff = np.median(np.dstack(imlist), axis=2)
            bgdict[c] = ff
            c += 1
        else:
            break
    return bgdict


def background_subtraction(inputfolder, backgroundfolder):
    """
    Covert lab specific.
    Not to be called by preprocess_operation. Use it in separate from a pipeline.
    """

    bgdict = calc_background(backgroundfolder)
    print "{0} channels found...".format(len(bgdict))

    content = []
    for dirname, subdirlist, filelist in os.walk(inputfolder):
        for i in filelist:
            if i.endswith('.tif'):
                content.append(join(dirname, i))
    print "{0} tif files found...".format(len(content))

    num_cores = 7
    if len(content) > num_cores:
        split_lists = list(chunks(content, int(math.ceil(len(content)/num_cores))))
        pool = multiprocessing.Pool(num_cores, maxtasksperchild=1)
        pool.map(partial(_subtract, bgdict=bgdict), split_lists, chunksize=1)
        pool.close()
    else:
        _subtract(content, bgdict)




if __name__ == "__main__":
    _main()

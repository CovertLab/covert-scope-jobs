from __future__ import division
from tiffix import _main, chunks, call_process
from os.path import join
import os
import sys
import multiprocessing
import math
import numpy as np
from os.path import join, dirname, abspath


reffile = dict(np.load(join(dirname(abspath(__file__)), 'data/ref.npz')))
darkreffile = dict(np.load(join(dirname(abspath(__file__)), 'data/darkref.npz')))


def _fix(imgpath_list):
    r0 = reffile.copy()
    r1 = darkreffile.copy()
    for imgpath in imgpath_list:
        try:
            call_process(imgpath, r0, r1)
        except IOError:
            with open('corrupted.txt', 'a') as f:
                f.write(imgpath+'\n')
        except:
            with open('error.txt', 'a') as f:
                f.write(imgpath+'\n')


def call_tiffix(inputfolder, binning=3, magnification=20):
    """
    Covert lab specific.
    Not to be called by preprocess_operation. Use it in separate from a pipeline.
    """
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
        pool.map(_fix, split_lists, chunksize=1)
        pool.close()
    else:
        _fix(content)




if __name__ == "__main__":
    inputfolder = sys.argv[1] # NOTE: assume full path e.g. /scratch/blah/blah/blah/image.tif

    call_tiffix(inputfolder)
from __future__ import division
from tiffix import _main, chunks, run_correct_shade
from os.path import join
import os
import sys
import multiprocessing
import math
import numpy as np
from os.path import join, dirname, abspath
import argparse
from tifffile import TiffFile
import tifffile as tiff

reffile = dict(np.load(join(dirname(abspath(__file__)), 'data/ref.npz')))
darkreffile = dict(np.load(join(dirname(abspath(__file__)), 'data/darkref.npz')))


def call_process(imgpath, reffile, darkreffile):
    with TiffFile(imgpath) as tif:
        md = tif.imagej_metadata
        img_sc = tif.asarray()
        if "Info" in md:
            img_sc, md = run_correct_shade(tif, md, reffile, darkreffile)
            return img_sc, md
        elif 'postprocess' in md:
            if md['postprocess'] == 'shading_correction':
                with open('skipped.txt', 'a') as f:
                    f.write(imgpath + '\n')
                return img_sc, md


def _gen_outputdir(parentfolder, outputfolder, dirname):
    sfol_name = dirname.split(parentfolder)[-1]
    sfol_name = sfol_name if not sfol_name.startswith('/') else sfol_name[1:]
    outputdir = join(outputfolder, sfol_name)
    return outputdir


def _fix(set_arg):
    r0 = reffile.copy()
    r1 = darkreffile.copy()
    for (parentfolder, outputfolder, dirname, imgpath) in set_arg:
        outputdir = _gen_outputdir(parentfolder, outputfolder, dirname)
        try:
            img, md = call_process(join(dirname, imgpath), r0, r1)
            tiff.imsave(join(outputdir, imgpath), img.astype(np.uint16),
                        imagej=True, metadata=md, compress=9)
        except IOError:
            with open('corrupted.txt', 'a') as f:
                f.write(join(dirname, imgpath) + '\n')
        except:
            with open('error.txt', 'a') as f:
                f.write(join(dirname, imgpath) + '\n')


def call_tiffix(inputfolder, outputfolder, binning=3, magnification=20, num_cores=1):
    """
    Covert lab specific.
    Not to be called by preprocess_operation. Use it in separate from a pipeline.
    """
    if outputfolder is None:
        outputfolder = inputfolder

    content = []
    for dirname, subdirlist, filelist in os.walk(inputfolder):
        for i in filelist:
            if i.endswith('.tif'):
                content.append((inputfolder, outputfolder, dirname, i))
        outputdir = _gen_outputdir(inputfolder, outputfolder, dirname)
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)

    print "{0} tif files found...".format(len(content))
    print "processing with {0} cores".format(num_cores)

    if len(content) > num_cores:
        split_lists = list(chunks(content, int(math.ceil(len(content)/num_cores))))
        pool = multiprocessing.Pool(num_cores, maxtasksperchild=1)
        pool.map(_fix, split_lists, chunksize=1)
        pool.close()
    else:
        _fix(content)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--cores", help="number of cores for multiprocessing",
                        type=int, default=1)
    parser.add_argument("-o", "--output", help="output folder",
                        type=str, default=None)
    parser.add_argument("input", nargs="*", help="input folder")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    inputfolder = args.input[0]
    call_tiffix(inputfolder, args.output, num_cores=args.cores)



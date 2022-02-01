#!/usr/bin/env python
"""Simple Bot to find files recusrive by file extension, copy to a destination target and check integrity
"""

from os.path import join
from argparse import ArgumentParser
import os

import re
import mmap
import hashlib
import shutil

parser = ArgumentParser()

parser.add_argument("-s", "--sourcedir", dest="sourcedirpath",
                    help="Directory to find and copy files from", metavar="DIRECTORY")

parser.add_argument("-t", "--targetdir", dest="targetddirpath",
                    help="Directory for destination of files to copy", metavar="DIRECTORY")

parser.add_argument("-e", "--fileextension", dest="fileext",
                    help="Filter for file extensions to copy", default=".zip")

args = parser.parse_args()

def run_fast_scandir(dir, ext):    # dir: str, ext: list
    # https://stackoverflow.com/a/59803793/2441026

    subfolders, files = [], []

    for f in os.scandir(dir):
        if f.is_dir():
            subfolders.append(f.path)
        if f.is_file():
            if os.path.splitext(f.name)[1].lower() in ext:
                files.append(f.path)

    for dir in list(subfolders):
        sf, f = run_fast_scandir(dir, ext)
        subfolders.extend(sf)
        files.extend(f)
    return subfolders, files

if __name__ == '__main__':
    if args.sourcedirpath:
        sourceDir = os.path.abspath(args.sourcedirpath)
        #targetDir = os.path.abspath(args.targetddirpath)
        try:
            # search all the files to copy
            subfolders, files = run_fast_scandir(sourceDir, [args.fileext])
            #print(files)
            for f in files:
                # open each file as memory mapped file object
                with open(f, mode='rb') as fin:
                    mf = mmap.mmap(fin.fileno(), 0, access=mmap.ACCESS_READ)
                    m = hashlib.md5()
                    #print(mf.read())
                    m.update(mf)

                    # output md5 hash for this file
                    filehash = m.hexdigest()
                    filename = os.path.basename(f)
                    #print(filename + ": " + filehash)

                    # copy file to destination
                    if args.targetddirpath:
                        if not os.path.exists(args.targetddirpath):
                            os.mkdir(args.targetddirpath)
                        fulltarget = os.path.join(args.targetddirpath, filename)
                        shutil.copy(f, fulltarget)

                        # verify md5 hash again
                        with open(os.path.abspath(fulltarget), mode='rb') as fin2:
                            mf2 = mmap.mmap(fin2.fileno(), 0, access=mmap.ACCESS_READ)
                            m2 = hashlib.md5()
                            m2.update(mf2)
                            filehash2 = m2.hexdigest()
                            print(filename + ": " + filehash + " <> " + filehash2)
                            print(mf2)
                            if filehash == filehash2:
                                print("SUCCESS " + filename)
                            else:
                                print("FAILED " + filename)
                    else: 
                        print("target directory not set")

        except Exception as e:
            print(e)
    else:
        print("Argument --sourcedir (-s) was missing.")
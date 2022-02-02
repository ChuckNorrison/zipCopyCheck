#!/usr/bin/env python
"""Simple Bot to find files recusrive by file extension, copy to a destination target and check integrity
"""
import logging

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

logger = logging.getLogger("zipCopyCheck")
formatter = logging.Formatter("%(asctime)s.%(msecs)03d - %(name)s - %(message)s","%Y-%m-%d %H:%M:%S")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

errCnt = 0
errFiles = []

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
    logger.info("Start zipCopyCheck script")

    if args.sourcedirpath:
        sourceDir = os.path.abspath(args.sourcedirpath)
        logger.info("Source: " + str(sourceDir))

        if args.targetddirpath:
            targetDir = os.path.abspath(args.targetddirpath)
            logger.info("Destination: " + str(targetDir))
        else:
            logger.warning("target directory not set")

        try:
            # search all the files to copy
            subfolders, files = run_fast_scandir(sourceDir, [args.fileext])
            for f in files:
                # open each file as memory mapped file object
                with open(f, mode='rb') as fin:
                    mf = mmap.mmap(fin.fileno(), 0, access=mmap.ACCESS_READ)
                    m = hashlib.md5()
                    m.update(mf)

                    # remember hash for this file
                    filehash = m.hexdigest()
                    filename = os.path.basename(f)

                    # copy file to destination
                    if not os.path.exists(targetDir):
                        os.mkdir(targetDir)
                    targetPath = os.path.join(targetDir, filename)
                    shutil.copy(f, targetPath)

                    # verify md5 hash again
                    with open(os.path.abspath(targetPath), mode='rb') as fin2:
                        mf2 = mmap.mmap(fin2.fileno(), 0, access=mmap.ACCESS_READ)
                        m2 = hashlib.md5()
                        m2.update(mf2)
                        filehash2 = m2.hexdigest()
                        logger.debug(filename + ": " + filehash + " <> " + filehash2)
                        if filehash == filehash2:
                            logger.info("SUCCESS " + filename)
                        else:
                            errCnt+=1
                            errFiles.append(targetPath)
                            logger.critical("FAILED " + filename)

        except Exception as e:
            logger.critical(e)
        if errCnt != 0:
            logger.critical("Some errors occured:")
            for f in errFiles:
                logger.critical(str(f))
    else:
        logger.warning("Argument --sourcedir (-s) was missing. Nothing to do.")
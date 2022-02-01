#!/usr/bin/env python
"""Simple Bot to find files recusrive by file extension, copy to a destination target and check integrity
"""

from os.path import join
from argparse import ArgumentParser
import os

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
			if args.fileext:
				fileext = args.fileext
			else: 
				fileext = "zip"
				print("Default file extension is '" + fileext + "'")

			subfolders, files = run_fast_scandir(sourceDir, [fileext])
			print(files)
		except:
			print("Directory not found")
	else:
		print("Argument --sourcedir (-s) was missing.")
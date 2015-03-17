#!/usr/bin/env python
import ROOT as r
import logging as lng
import os
from sys import exit

def splash():
    print "*"*40
    print "\n\tICF rootfile jet converter\n"
    print "*"*40
    print ""

def gather_input_files():
    if not opts.indir:
        lng.error("No input directory specified.")
        exit("Exiting.")

    in_files = []

    for ent in os.walk(opts.indir):
        for f in ent[-1]:
            if f[-5:] == ".root":
                in_files.append(f)

    num = len(in_files)
    lng.info("Found %d file%s for conversion." % (len(in_files), "s" if num > 1 else ""))
    lng.debug("Found: %s" % ", ".join(in_files))
    
    return in_files

def convert(fname = None):
    lng.debug("Converting file: %s" % fname)

def main():
    
    infiles = gather_input_files()

    for fname in infiles:
        convert(fname)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description ='Convert ICF rootfiles to different jet binning')
    parser.add_argument('-i', help = 'input file directory',
                        dest = 'indir', type =str)
    parser.add_argument('-o', help = 'output file directory',
                        dest = 'outdir', type =str)
    parser.add_argument('-d', help = 'For debug use',
                        dest = 'debug', default = False,
                        action="store_true")
    parser.add_argument('--log', help = 'Set logging level (WARNING/DEBUG/INFO/ERROR/CRITICAL)',
                        dest = 'loglevel', default = 'INFO')
    parser.add_argument('-j', help = 'Target jet binning (fine/coarse)',
                        dest = 'jbin', default = 'fine')
    opts = parser.parse_args()

    if opts.debug:
        opts.loglevel = 'DEBUG'

    lng.basicConfig(level=opts.loglevel.upper())

    splash()

    if opts.jbin in ['c', 'coarse', 'crse', 'cr']:
        lng.info("Converting: fine -> coarse.")
    elif opts.jbin in ['f', 'fine', 'fn']:
        lng.info("Converting: coarse -> fine.")

    main()

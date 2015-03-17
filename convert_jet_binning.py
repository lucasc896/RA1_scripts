#!/usr/bin/env python
import ROOT as r
import logging as lng
from sys import exit

def splash():
    print "*"*40
    print "\n\tICF rootfile jet converter\n"
    print "*"*40
    print ""







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
    parser.add_argument('-j', help = 'Target jet binning (fine/coarse)',
                        dest = 'jbin', default = 'fine')
    opts = parser.parse_args()

    lng.basicConfig(level=lng.INFO)

    splash()

    if opts.jbin in ['c', 'coarse', 'crse', 'cr']:
        lng.info("Converting: fine -> coarse.")
    elif opts.jbin in ['f', 'fine', 'fn']:
        lng.info("Converting: coarse -> fine.")

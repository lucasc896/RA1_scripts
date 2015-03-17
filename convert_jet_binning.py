#!/usr/bin/env python
import ROOT as r
import logging as lng
import os
from sys import exit
from copy import deepcopy

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

def print_yields(dic = {}):
    for d in dic:
        if not dic[d]: continue
        print d
        print dic[d].GetEntries()

def validate_yields(old = {}, new = {}):
    lng.debug("Validating yields.")

    old_ents = {}
    new_ents = {}
    for k in old:
        old_ents[k] = old[k].GetEntries() if old[k] else 0

    for k in new:
        new_ents[k] = new[k].GetEntries() if new[k] else 0

    # list of possible problems
    tests = [
                "new_ents['all'] != old_ents['all']",
                "new_ents['2'] != (old_ents['1'] + old_ents['2'])",
                "new_ents['3'] != (old_ents['3'] + old_ents['4'])",
                "new_ents['all'] != (new_ents['2'] + new_ents['3'])",
            ]

    valid = True
    while valid:
        for test in tests:
            outcome = eval(test)
            if outcome:
                lng.error("Test: %s returned %s." % (test, str(valid)))
                exit("Exiting.")
        return True
    return False



def process_hist(file = None, dirname = '', histname = ''):
    lng.debug("Processing hist: %s/%s" % (dirname, histname))

    multis = ["all", "1", "2", "3", "4"]
    old_hists = dict.fromkeys(multis)
    new_hists = dict.fromkeys(multis)

    # open the old hists
    for m in multis:
        h = file.Get("%s/%s_%s" % (dirname, histname, m))
        old_hists[m] = h

    lng.debug("Old_hists: %s" % str(old_hists))

    # create new histograms from old (make sure to clone the right
    # ones, to preserve hist titles)
    # inclusive
    new_hists['all'] = deepcopy(old_hists['all'])

    # le3j
    new_hists['2'] = deepcopy(old_hists['2'].Clone())
    new_hists['2'].Add(old_hists['1'])

    # ge4j
    new_hists['3'] = deepcopy(old_hists['3'].Clone())
    new_hists['3'].Add(old_hists['4'])

    lng.debug("New_hists: %s" % str(new_hists))

    validate_yields(old_hists, new_hists)

    return new_hists

def process_dir(file = None, dirname = ''):
    lng.debug("Processing directory: %s" % dirname)
    
    dir = file.Get(dirname)
    
    # get list of histogram names in directory
    hist_names = []
    for hkey in dir.GetListOfKeys():
        hname = hkey.GetName().split("_")[:-1]
        hname = "_".join(hname)
        if hname not in hist_names:
            hist_names.append(hname)

    lng.debug("Found %d hists in directory %s." % (len(hist_names), dirname))

    new_dirs = {}
    for ent in hist_names:
        if ent != "AlphaT": continue #tmp mask for only AlphaT distro
        new_dirs = process_hist(file, dirname, ent)

    return new_dirs

def write_new_file(filename = '', content = {}):
    lng.info("Writing new file: %s" % filename)

    if opts.outdir:
        outdir = opts.outdir
    else:
        outdir = "/tmp"
        lng.info("No output directory specified. Using %s" % outdir)

    lng.debug("File output: %s/%s" % (outdir, filename))

    # create new file
    ofile = r.TFile.Open("%s/%s" % (outdir, filename), "RECREATE")
    for newdirname in content:
        ofile.mkdir(newdirname)
        ofile.cd(newdirname)
        for hist in content[newdirname].values():
            if hist: hist.Write()
        ofile.cd()

    ofile.Close()
    lng.debug("File written and closed.")


def convert_file(fname = None):
    lng.info("Converting file: %s/%s" % (opts.indir, fname))

    file = r.TFile.Open("%s/%s" % (opts.indir, fname))
    new_content = {}

    for dkey in file.GetListOfKeys():
        dir = dkey.GetTitle()
        new_content[dir] = process_dir(file, dir)
    
    # close this rootfile - all hists deepcopy'd, so fine to do
    file.Close()

    write_new_file(fname.replace(".root", "_coarseNJet.root"), new_content)

def main():
    
    infiles = gather_input_files()

    for fname in infiles:
        convert_file(fname)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description ='Convert fine ICF rootfiles to coarse jet binning')
    parser.add_argument('-i', help = 'input file directory',
                        dest = 'indir', type =str)
    parser.add_argument('-o', help = 'output file directory',
                        dest = 'outdir', type =str)
    parser.add_argument('-d', help = 'For debug use',
                        dest = 'debug', default = False,
                        action="store_true")
    parser.add_argument('--log', help = 'Set logging level (WARNING/DEBUG/INFO/ERROR/CRITICAL)',
                        dest = 'loglevel', default = 'INFO')
    opts = parser.parse_args()

    if opts.debug:
        opts.loglevel = 'DEBUG'

    lng.basicConfig(level=opts.loglevel.upper())

    splash()

    main()

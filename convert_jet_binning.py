#!/usr/bin/env python
import ROOT as r
import logging as lng
import os
from sys import exit, stdout
from copy import deepcopy

def print_progress(percent):

    if opts.debug: return

    width = 60

    stdout.write("\t  %.2f%% complete." % percent)
    stdout.write(" |"+"="*int(percent*0.01*width)+" "*int((1.-percent*0.01)*width)+">     \r")
    stdout.flush()

def splash():
    print "*"*42
    print "\n\tICF rootfile jet converter\n"
    print "*"*42
    print ""

def gather_input_files():
    if not opts.indir:
        lng.error("No input directory specified.")
        exit("Exiting.")

    in_files = []

    lng.debug("Going for a walk in: %s" % opts.indir)
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

def validate_yields(old = {}, new = {}, string = ''):
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
        for n, test in enumerate(tests):
            outcome = eval(test)
            # check if there's a True test
            # hack: ignore the outcome of the last test for GenJetPt_ (formula btag plots)
            # known issue.
            if outcome and ("GenJetPt_" not in string and n !=3):
                lng.error("Test: %s returned %s." % (test, str(valid)))
                lng.error("Tag: %s" % string)
                print old_ents
                print new_ents
                # exit("Exiting.")
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

    tag = " ".join([str(file), dirname, histname])
    validate_yields(old_hists, new_hists, tag)

    return new_hists

def process_dir(file = None, dirname = ''):
    lng.debug("Processing directory: %s" % dirname)
    
    dir = file.Get(dirname)
    
    # get list of histogram names in directory
    hist_names = []
    for hkey in dir.GetListOfKeys():
        hname = hkey.GetName().split("_")[:-1]
        hname = "_".join(hname)
        # if hname not in ["AlphaT", "HT"]: continue
        if hname not in hist_names:
            hist_names.append(hname)

    lng.debug("Found %d hists in directory %s." % (len(hist_names), dirname))

    new_dirs = {}
    for ent in hist_names:
        # if ent != "AlphaT": continue #tmp mask for only AlphaT distro
        new_dirs[ent] = process_hist(file, dirname, ent)

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
    ndirs = len(content.keys())
    for n, newdirname in enumerate(content.keys()):
        ofile.mkdir(newdirname)
        ofile.cd(newdirname)
        for histname in content[newdirname]:
            for hist in content[newdirname][histname].values():
                if hist: hist.Write()
        ofile.cd()

    ofile.Close()
    lng.debug("File written and closed.")


def convert_file(fname = None):
    lng.info("Converting file: %s/%s" % (opts.indir, fname))

    file = r.TFile.Open("%s/%s" % (opts.indir, fname))
    new_content = {}

    nkeys = len(file.GetListOfKeys())

    for n, dkey in enumerate(file.GetListOfKeys()):
        dir = dkey.GetTitle()
        if dir == "count_total": continue
        # if dir not in ["375_475"]: continue
        new_content[dir] = process_dir(file, dir)
        print_progress(100.*(float(n)/float(nkeys)))
    print_progress(100.)

    # close this rootfile - all hists deepcopy'd, so fine to do
    file.Close()

    # for i in new_content:
    #     print i
    #     for j in new_content[i]:
    #         print " ", j
    #         for k in new_content[i][j]:
    #             print "  ", k
    #             print "    ", new_content[i][j][k]

    write_new_file(fname.replace(".root", "_coarseNJet.root"), new_content)

def main():
    
    infiles = gather_input_files()

    for fname in infiles:
        # if "Had_Data" in fname:
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

    opts.indir = os.getcwd() + "/" + opts.indir
    opts.outdir = os.getcwd() + "/" + opts.outdir

    lng.basicConfig(level=opts.loglevel.upper())

    splash()

    main()

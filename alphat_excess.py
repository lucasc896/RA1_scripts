#!/usr/bin/env python
import plot_grabber as grabr
import ROOT as r
import os
# import argparse
from itertools import product
from sys import exit
from simplify_tables import harvest_values, remove_whitespace
from object_cat import event_cat

# options = argparse.ArgumentParser(description ='Produce RA1 Results')

# # options.add_argument('-c',help= 'Make RA1 Closure Tests, Choose all, 1, 2 or 3 or jetcat',nargs='+', type=str)
# # options.add_argument('-u',help= 'Make RA1 Tables Uncorrected Yields', nargs='+', type=str)
# # options.add_argument('-m',help= 'Make RA1 MC Normalisation Tables',action="store_true")
# # options.add_argument('-r',help= 'Make RA1 Root Files, Choose all, 1, 2 or 3',nargs='+',type=str)
# # options.add_argument('-n',help= 'Make RA1 Tables, Choose all, 1, 2 or 3',nargs='+',type=str)
# # options.add_argument('-t',help= 'Make Template fitting',choices = ['had','muon']) 
# # options.add_argument('-j',help= 'Set jet categories fit to default 2,3,4,>=5', nargs='+',type = str,default=["2","3","4","5"])
# options.add_argument('-d',help= 'For debug use', action="store_true")
# opts = options.parse_args()

r.gStyle.SetOptStat(0)
grabr.set_palette()

def dict_printer(dicto = {}, indent = 1):

  print "{ (%d keys)\n" % len(dicto)
  for key in dicto:
    print "\t"*indent, "'%s': " % key,
    if dict == type(dicto[key]):
      dict_printer(dicto[key], indent+1)
    else:
      print dicto[key]
  print "\t"*indent, "}\n"

def convert_val(val = ''):
    if val == "-":
        return 0.
    return float(val)

def harvest_excess_yields(file = None):

    ht_bins = ["237.5", "300", "350", "425", "525", "625", "725", "825", "925", "1025", "1075"]
    data = []
    pred = []
    pred_err = []
    excess = []
    excess_err = []

    for n, line in enumerate(file.readlines()):
        if n>50: # skip lines beyond first table 
            break
        line_split = line.split("&")
        line_split = remove_whitespace(line_split)
        if line_split[0] == "Total SM prediction":
            # print ">>> BG harvest:"
            harvest_values(line_split, pred, pred_err)
        elif line_split[0] == "Hadronic yield from data":
            # print ">>> Data harvest:"
            harvest_values(line_split, data)

    # return an event_cat object, which handles excess and err calc
    return event_cat(data, pred, pred_err)

def get_file_key(str = ''):

    tmp_split = str.split("/")[-1]
    tmp_split = tmp_split.split(".")[0]
    tmp_split = tmp_split.split("_")
    
    bcat = "ge0" if tmp_split[-3] == "Inc" else tmp_split[-3]
    jcat = "ge2" if tmp_split[-1] == "inclusive" else tmp_split[-1]

    jcat = jcat.replace("greq", "ge")

    return "%sb_%sj" % (bcat, jcat)

def get_excess():
    print ">>> Getting excess yields."

    yields = {}

    in_dir = "/Users/chrislucas/SUSY/AnalysisCode/RA1_scripts/in"
    for dir in os.walk(in_dir):
        # change this for mutliple dirs with diff aT thresholds
        if dir[-1]:
            for file in dir[-1]:
                file_path = dir[0]+"/"+file
                this_key = get_file_key(file_path)
                file = open(file_path)
                cat_obj = harvest_excess_yields(file)
                cat_obj._catstring = this_key
                yields[this_key] = cat_obj
                file.close()

    return yields

def get_qcd():

    print ">>> Getting QCD yields."

    HTbins = ["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"]
    ht_scheme = ["incl", "excl"][1]
    n_j = ["eq2j", "eq3j", "eq4j", "ge5j"]
    n_b = ["eq0b", "eq1b", "eq2b", "eq3b", "ge0b"]
    selec = ["OneMuon", "DiMuon", "Had"][2]
    hist_title = ["AlphaT"][0]
    my_path = "Root_Files_22Feb_gt0p3_latest_aT_0p507_v0"

    if ht_scheme == "incl":
        my_iter = [HTbins]
        ht_string = "inclHT"
    elif ht_scheme == "excl":
        my_iter = HTbins

    canv = r.TCanvas()
        
    yields = {}

    for nb, nj in product(n_b, n_j):
        vals = []
        errs = []
        for htbin in my_iter:
            h_mc = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Had_QCD.root" % my_path,
                                    sele = selec, h_title = hist_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
            this_err = r.Double(0.)
            # check this is giving the correct, weighted vals for QCD MC
            val = h_mc.IntegralAndError(1, h_mc.GetNbinsX(), this_err)
            vals.append(val)
            errs.append(this_err)
        # print nb, nj
        # print yields
        # print errs
        this_key = "%s_%s" % (nb, nj)
        this_cat = event_cat(pred = vals, pred_err = errs)
        this_cat._catstring = this_key
        yields[this_key] = this_cat

    # dict_printer(yields)
    return yields

def make_plots(excess = {}, qcd = {}):

    for cat in excess:
        if cat not in qcd.keys():
            continue
        excess_val, excess_err = excess[cat].the_excess()
        qcd_val, qcd_err = excess[cat].the_preds()
        for i in range(len(excess_val)):
            print excess_val[i], qcd_val[i]

def main():
    # get excess yields
    excess = get_excess()
    # get qcd yields
    qcd = get_qcd()

    # make comparison plots
    make_plots(excess, qcd)

if __name__ == "__main__":
    main()
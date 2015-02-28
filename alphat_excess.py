import plot_grabber as grabr
import ROOT as r
import os
# import argparse
from itertools import product
from sys import exit
from simplify_tables import harvest_values, remove_whitespace

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
        val = 0.
    val = float(val)

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
            harvest_values(line_split, pred, pred_err)
        elif line_split[0] == "Hadronic yield from data":
            harvest_values(line_split, data)

    for dval, pval, perr in zip(data, pred, pred_err):
        convert_val(dval)
        convert_val(pval)
        convert_val(perr)

        print dval, type(dval), "hey"
        excess.append(dval-pval)
        excess_err.append(perr)

    # now return excess and calculate error
    return excess, excess_err

def get_file_key(str = ''):

    tmp_split = str.split("/")[-1]
    tmp_split = tmp_split.split(".")[0]
    tmp_split = tmp_split.split("_")
    
    bcat = "ge0" if tmp_split[-3] == "Inc" else tmp_split[-3]
    jcat = "ge2" if tmp_split[-1] == "Inc" else tmp_split[-1]

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
                yields[this_key] = harvest_excess_yields(file)
                file.close()

    dict_printer(yields)    

    return yields

def get_qcd():

    HTbins = ["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"][3:]
    ht_scheme = ["incl", "excl"][0]
    n_j = ["eq2j", "eq3j", "eq4j", "ge5j"]
    n_b = ["eq0b", "eq1b", "eq2b", "eq3b", "ge0b", "ge1b"][-2:-1]
    selec = ["OneMuon", "DiMuon", "Had"][2]
    hist_title = ["genMetJetPtFrac", "genMetHTFrac", "neutVectPt_ov_genMet", "numGenNeutrino", "genMetOverJetPt_vs_CSV"][-1:]
    my_path = "Root_Files_22Feb_gt0p3_latest_aT_0p507_v0"

    if ht_scheme == "incl":
        my_iter = [HTbins]
        ht_string = "inclHT"
    elif ht_scheme == "excl":
        my_iter = HTbins

    canv = r.TCanvas()

    for my_title in hist_title:
        is_th2 = False
        for htbin in my_iter:
            if ht_scheme == "excl":
                ht_string = htbin
            n_bin = 1
            
            for nb, nj in product(n_b, n_j):
                h_mc = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Had_QCD.root" % my_path,
                                        sele = selec, h_title = my_title, njet = nj, btag = nb, ht_bins = htbin)
                if "TH1" in str(type(h_mc)):
                    h_mc.Draw()
                elif "TH2" in str(type(h_mc)):
                    is_th2 = True
                    h_mc.Draw("colz")

                if my_title == "neutVectPt_ov_genMet":
                    h_mc.GetXaxis().SetRangeUser(0., 1.5)
                    canv.SetLogy(1)

                if is_th2:
                    h_mc.GetXaxis().SetTitle("genMet/JetPt")
                    h_mc.GetYaxis().SetTitle("CSV Disciminator")
                    h_mc.RebinX(10)
                    h_mc.RebinY(10)

                canv.Print("out/qcdplots_%s_%s_%s_%s.pdf" % (selec, my_title, nb, nj))

def main():
    # get excess yields
    excess = get_excess()

if __name__ == "__main__":
    main()
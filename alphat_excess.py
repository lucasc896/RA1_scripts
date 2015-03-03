#!/usr/bin/env python
import plot_grabber as grabr
import ROOT as r
import os
import math as ma
from itertools import product
from sys import exit
from simplify_tables import harvest_values, remove_whitespace
from object_cat import event_cat

# r.gStyle.SetOptStat(0)
r.gStyle.SetOptFit()
r.gROOT.SetBatch(1)
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
        # change this for multiple dirs with diff aT thresholds
        if dir[-1]:
            alpha_key = dir[0].split("_")[-1]
            yields[alpha_key] = {}
            for file in dir[-1]:
                file_path = dir[0]+"/"+file
                this_key = get_file_key(file_path)
                file = open(file_path)
                cat_obj = harvest_excess_yields(file)
                cat_obj._catstring = this_key
                yields[alpha_key][this_key] = cat_obj
                file.close()

    # print ""
    # for key in yields:
    #     print key, yields[key]

    return yields

def get_qcd(alphat_vals = ["0p507"]):

    print ">>> Getting QCD yields."

    HTbins = ["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"][3:]
    ht_scheme = ["incl", "excl"][1]
    n_j = ["eq2j", "eq3j", "eq4j", "ge5j"]
    n_b = ["eq0b", "eq1b", "eq2b", "eq3b", "ge0b"]
    selec = ["OneMuon", "DiMuon", "Had"][2]
    hist_title = ["AlphaT"][0]

    if ht_scheme == "incl":
        my_iter = [HTbins]
        ht_string = "inclHT"
    elif ht_scheme == "excl":
        my_iter = HTbins

    canv = r.TCanvas()
        
    yields = {}

    for alpha_key in alphat_vals:
        yields[alpha_key] = {}
        my_path = "Root_Files_22Feb_lt0p3_latest_aT_%s_v0" % alpha_key
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

            this_key = "%s_%s" % (nb, nj)
            this_cat = event_cat(pred = vals, pred_err = errs)
            this_cat._catstring = this_key
            yields[alpha_key][this_key] = this_cat

    return yields

def make_plots(excess = {}, qcd = {}):

    HTbins = ["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"][3:]
    canv = r.TCanvas("canv", "canv", 600, 500)

    # get list of alphat vals to plot
    alpha_keys = []
    for alpha in excess:
        if alpha not in qcd.keys(): continue
        alpha_keys.append(alpha)

    for cat in excess[alpha_keys[0]]:
        if cat not in qcd[alpha_keys[0]]: continue

        # skip eq2j cats, as we're looking at lt0p3
        if "eq2j" in cat: continue

        yvals_ex_incl = []
        yvals_qcd_incl = []

        for iht in range(len(HTbins)):
            
            xvals= []
            yvals_ex = []
            yvals_qcd = []

            # loop all the viable alphat values
            for n, a_key in enumerate(alpha_keys):
                # very inefficient...
                ex_vals, ex_err = excess[a_key][cat].the_excess()
                qcd_vals, qcd_err = qcd[a_key][cat].the_preds()

                xvals.append( [float(a_key.replace("p", ".")), 0.0005] )
                yvals_ex.append( [ex_vals[iht], ex_err[iht]] )
                yvals_qcd.append( [qcd_vals[iht], qcd_err[iht]] )

                # sum the excess inclusive selection
                if n+1 > len(yvals_ex_incl):
                    yvals_ex_incl.append( [ex_vals[iht], ex_err[iht]] )
                else:
                    yvals_ex_incl[n][0] += ex_vals[iht]
                    yvals_ex_incl[n][1] += ex_err[iht]
                # sum the qcd inclusive selection
                if n+1 > len(yvals_qcd_incl):
                    yvals_qcd_incl.append( [qcd_vals[iht], qcd_err[iht]] )
                else:
                    yvals_qcd_incl[n][0] += qcd_vals[iht]
                    yvals_qcd_incl[n][1] += qcd_err[iht]

            ex_distro = make_single_plot(xvals, yvals_ex, "Excess")
            ex_distro.SetMarkerColor(r.kBlue)
            qcd_distro = make_single_plot(xvals, yvals_qcd, "QCD")
            qcd_distro.SetMarkerColor(r.kRed)

            mgraph = make_combined_plot([ex_distro, qcd_distro], cat)
            canv.BuildLegend(0.7, 0.8, 0.89, 0.89)
            # canv.Print("out/alphat_excess_%s_%s.pdf" % (cat, HTbins[iht]))

        fit_func = ["pol1", "expo"][1]

        # now make inclusive HT selection plot
        ex_distro = make_single_plot(xvals, yvals_ex_incl, "Excess")
        ex_distro.SetMarkerColor(r.kBlue)
        ex_distro.Fit(fit_func, "q")
        ex_distro.GetFunction(fit_func).SetLineColor(r.kBlue)
        ex_distro.Draw("ap*")

        qcd_distro = make_single_plot(xvals, yvals_qcd_incl, "QCD")
        qcd_distro.SetMarkerColor(r.kRed)
        qcd_distro.Fit(fit_func, "q")
        qcd_distro.Draw("ap*")

        ratio_vals = []
        for a, b, in zip(yvals_qcd_incl, yvals_ex_incl):
            try:
                ratio = a[0]/b[0]
                ratio_err = ratio * ma.sqrt( ma.pow(a[1]/a[0], 2) + ma.pow(b[1]/b[0], 2) )
                ratio_vals.append( [ratio, ratio_err] )
            except ZeroDivisionError:
                ratio_vals.append( [0, 0.0] )
        ratio_graph = make_single_plot(xvals, ratio_vals, "%s - QCD/Excess" % cat)
        ratio_graph.Draw("ap*")
        ratio_graph.GetXaxis().SetTitle("#alpha_{T}")
        ratio_graph.GetYaxis().SetTitle("Events")
        ratio_graph.GetYaxis().SetRangeUser(0., 2.)
        ratio_graph.Fit("pol0", "q")
        canv.Print("out/alphat_excess_%s_%s_ratio.pdf" % (cat,
            "incl_%s-%s" % (HTbins[0].split("_")[0], "inf" if HTbins[-1] == "1075" else HTbins[-1].split("_")[1])))

        mgraph = make_combined_plot([ex_distro, qcd_distro], "%s - Yields" % cat)

        canv.BuildLegend(0.7, 0.8, 0.89, 0.89)
        canv.SetGridx(1)
        canv.SetGridy(1)
        # canv.SetLogy(1)

        r.gPad.Update()
        stats_ex = ex_distro.GetListOfFunctions().FindObject("stats")
        stats_ex.SetTextColor(r.kBlue)
        stats_ex.SetX1NDC(0.75)
        stats_ex.SetX2NDC(0.89)
        stats_ex.SetY1NDC(0.7)
        stats_ex.SetY2NDC(0.79)
        stats_ex.Draw()

        stats_qcd = qcd_distro.GetListOfFunctions().FindObject("stats")
        stats_qcd.SetTextColor(r.kRed)
        stats_qcd.SetX1NDC(0.75)
        stats_qcd.SetX2NDC(0.89)
        stats_qcd.SetY1NDC(0.6)
        stats_qcd.SetY2NDC(0.69)
        stats_qcd.Draw()

        canv.Modified()

        canv.Print("out/alphat_excess_%s_%s.pdf" % (cat,
            "incl_%s-%s" % (HTbins[0].split("_")[0], "inf" if HTbins[-1] == "1075" else HTbins[-1].split("_")[1])))

def make_single_plot(xvals = [], yvals = [], title = ''):
    gr = r.TGraphErrors(len(xvals))
    gr.SetTitle(title)

    if len(xvals) != len(yvals):
        print len(xvals), len(yvals)
        exit("Bad length.")
    
    for i in range(len(xvals)):
        gr.SetPoint(i, xvals[i][0], yvals[i][0])
        gr.SetPointError(i, xvals[i][1], yvals[i][1])
    
    return gr

def make_combined_plot(graphs = [], title = ''):
    multi_graph = r.TMultiGraph()

    for gr in graphs:
        multi_graph.Add(gr)
    
    multi_graph.SetTitle(title)
    multi_graph.Draw("ap*")
    multi_graph.SetMinimum(0.001)
    multi_graph.GetXaxis().SetTitle("#alpha_{T}")
    multi_graph.GetYaxis().SetTitle("Events")

    return multi_graph

def main():
    # get excess yields
    excess = get_excess()
    
    # get qcd yields
    qcd = get_qcd(excess.keys())

    # make comparison plots
    make_plots(excess, qcd)

if __name__ == "__main__":
    main()
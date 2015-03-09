#!/usr/bin/env python
import alphat_excess as yield_tools
import ROOT as r
import math as ma

def btag_prob(yield_dict = {}, jcats = []):
    print ">>> Making btag_prob plots."

    for nj in jcats:
        graphs = []
        for nb in ["eq0b", "eq1b", "eq2b"]:
            cat = "%s_%s" % (nb, nj)
            # make single plot for a b-tag cat
            vals = []
            for alpha in yield_tools.alpha_order(yield_dict.keys()):
                try:
                    yields, yield_errs = yield_dict[alpha][cat].the_excess()
                except KeyError:
                    print "> Warning: KeyError, %s" % cat
                    continue
                try:
                    tot_yields, tot_yield_errs = yield_dict[alpha]["ge0b_%s" % nj].the_excess()
                except KeyError:
                    print "> Warning: KeyError, ge0b_%s" % nj
                    continue
                if len(yields) != len(tot_yields):
                    print "> Warning: length error. %s" % cat
                    continue
                
                alpha_vals = []
                excl_yield = 0.
                excl_err = 0.
                incl_yield = 0.
                incl_err = 0.
                for i in range(len(yields)):
                    # try:
                    #     ratio_val = float(yields[i]/tot_yields[i])
                    # except ZeroDivisionError:
                    #     ratio_val = 0.
                    # ratio_err = 0.01
                        
                    # alpha_vals.append((ratio_val, ratio_err))
                    excl_yield += yields[i]
                    excl_err += ma.pow(yield_errs[i], 2)
                    incl_yield += tot_yields[i]
                    incl_err += ma.pow(tot_yields[i], 2)
                excl_err = ma.pow(excl_err, 0.5)
                incl_err = ma.pow(incl_err, 0.5)
                try:
                    ratio_val = float(excl_yield/incl_yield)
                    ratio_err = ma.sqrt( ma.pow(excl_err/excl_yield, 2) + ma.pow(incl_err/incl_yield, 2) )
                except:
                    ratio_val = 0.
                    ratio_err = 0.
                vals.append((float(alpha.replace("p", ".")), (ratio_val, ratio_err)))
            graphs.append( make_single_graph(vals, nb) )
        print_multi_graph(graphs, "btag_prob_alphat_%s_inclHT" % nj)

def make_single_graph(vals = [], title = ''):
    gr = r.TGraphErrors(len(vals))

    for n, entry in enumerate(vals):
        gr.SetPoint(n, entry[0], entry[1][0])
        gr.SetPointError(n, 0.005, entry[1][1])
    gr.SetTitle(title)

    return gr

def print_multi_graph(graphs = [], title = ''):
    canv = r.TCanvas()
    mg = r.TMultiGraph()
, r.kYellow-3, r.kGreen-2]
    marks = [r.kFullCircle, r.kFullSquare, r.kFullTriangleUp]

    for gr, col, mark in zip(graphs, cols, marks):
        gr.SetMarkerColor(col)
        gr.SetMarkerSize(2)
        gr.SetMarkerStyle(mark) # why isn't this working?
        mg.Add(gr)
    mg.SetTitle(title)

    mg.Draw("ap")
    mg.SetMinimum(-0.2)
    mg.SetMaximum(1.2)
    canv.BuildLegend(0.11, 0.75, 0.3, 0.89)
    canv.Print("out/" + title + ".pdf")

def main():

    jcats = ["eq2j", "eq3j", "eq4j", "ge5j", "ge2j"][1:]
    bcats = ["eq0b", "eq1b", "eq2b"]

    # get excess yields
    excess = yield_tools.get_excess()
    
    btag_prob(excess, jcats)

    # get qcd yields
    # qcd = yield_tools.get_qcd(excess.keys())

    # yield_tools.dict_printer(excess)
    # for key in excess:
    #     for kkey in excess['0p55']:
    #         print kkey

if __name__ == "__main__":
    main()
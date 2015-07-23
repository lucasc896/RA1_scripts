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
            vals_excl = []
            vals_incl = []
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
                # try:
                #     ratio_val = float(excl_yield/incl_yield)
                #     ratio_err = ma.sqrt( ma.pow(excl_err/excl_yield, 2) + ma.pow(incl_err/incl_yield, 2) )
                # except:
                #     ratio_val = 0.
                #     ratio_err = 0.
                # vals.append([float(alpha.replace("p", ".")), [ratio_val, ratio_err]])
                vals_excl.append([float(alpha.replace("p", ".")), [excl_yield, excl_err]])
                vals_incl.append([float(alpha.replace("p", ".")), [incl_yield, incl_err]])

            # make differential
            for j in range(len(vals_excl)):
                if j == len(vals_excl)-1: continue
                vals_excl[j][1][0] -= vals_excl[j+1][1][0] # subtract higher yield
                vals_excl[j][1][1] = ma.pow(vals_excl[j][1][1], 2) - ma.pow(vals_excl[j+1][1][1], 2)
                vals_excl[j][1][1] = ma.pow(vals_excl[j][1][1], 0.5)

                vals_incl[j][1][0] -= vals_incl[j+1][1][0] # subtract higher yield
                vals_incl[j][1][1] = ma.pow(vals_incl[j][1][1], 2) - ma.pow(vals_incl[j+1][1][1], 2)
                vals_incl[j][1][1] = ma.pow(vals_incl[j][1][1], 0.5)

            # now calculate ratio
            # time consuming, but good to seperate
            for k in range(len(vals_excl)):
                try:
                    ratio_val = float(vals_excl[k][1][0]/vals_incl[k][1][0])
                    ratio_err = ma.sqrt( ma.pow(vals_excl[k][1][1]/vals_excl[k][1][0], 2) + ma.pow(vals_incl[k][1][1]/vals_incl[k][1][0], 2) )
                except:
                    ratio_val = 0.
                    ratio_err = 0.

                vals.append( (vals_excl[k][0], (ratio_val, ratio_err)) )

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
    cols = [r.kRed-3, r.kYellow-3, r.kGreen-2]
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
    mg.GetXaxis().SetTitle("#alpha_{T}")
    mg.GetYaxis().SetTitle("Probability")
    canv.BuildLegend(0.11, 0.75, 0.3, 0.89)
    canv.Print("out/" + title + ".pdf")

def main():

    HTbins = ["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"][3:]
    jcats = ["eq2j", "eq3j", "eq4j", "ge5j", "ge2j"][1:]
    bcats = ["eq0b", "eq1b", "eq2b"]

    # get excess yields
    excess = yield_tools.get_excess(HTbins)

    btag_prob(excess, jcats)

    # get qcd yields
    # qcd = yield_tools.get_qcd(excess.keys())

    # yield_tools.dict_printer(excess)
    # for key in excess:
    #     for kkey in excess['0p55']:
    #         print kkey

if __name__ == "__main__":
    main()
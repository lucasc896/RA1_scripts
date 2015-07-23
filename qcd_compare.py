import plot_grabber as grabr
import ROOT as r
from itertools import product
from copy import deepcopy

r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(1)
grabr.set_palette()

def colours():
    return [r.kBlack, r.kRed, r.kBlue-2, r.kGreen-2, r.kYellow+1]

def get_hist_max(hist = None):
    max = 0.
    for i in range(1, hist.GetNbinsX()+1):
        cont = hist.GetBinContent(i)
        if cont > max:
            max = cont

    return max

def print_hist(vals = None, title = '', d = {}):
    
    title += "%.2f-%.2f" % (d["xbinlo"], d["xbinhi"])
    # print title
    # WARNING: no error handling!!
    canv = r.TCanvas()
    hist = r.TH1D("meh", title, len(vals), 0., 1.)
    for v in vals:
        bin = hist.FindBin(v[0])
        if v[1][0] > 0:
            hist.SetBinContent(bin, v[1][0])
            hist.SetBinError(bin, v[1][1])
    hist.Draw("")
    hist.GetXaxis().SetTitle("CSV")
    hist.GetYaxis().SetTitle("Count")
    canv.Print("out/qcdplots_%s_%s_%s_%s_xstrip_%s-%s.pdf" % (d["selec"],
                        d["title"], d["nj"], d["nb"], d["xbinlo"], d["xbinhi"]))

    return hist.Clone()

def print_x_strips(hist = None, details = {}):
    if not hist: return

    hist_list = []
    for xbin in range(1, hist.GetNbinsX()+1):
        vals = []
        details["xbinlo"] = hist.GetXaxis().GetBinLowEdge(xbin)
        details["xbinhi"] = hist.GetXaxis().GetBinUpEdge(xbin)
        for ybin in range(1, hist.GetNbinsY()+1):
            vals.append( (hist.GetYaxis().GetBinCenter(ybin), (hist.GetBinContent(xbin, ybin), hist.GetBinError(xbin, ybin))) )
        slice_hist = print_hist(vals, 'genMet/genJetPt = ', details)
        # print details['xbinlo']
        # if details["xbinlo"] < 1.:
        if len(hist_list) < 5:
            hist_list.append(slice_hist)
    descrip = "%s_%s_%s" % (details['title'][-1], details['nb'], details['nj'])
    print_combined_strips(hist_list, 'genMet/genJetPt', descrip)

def print_combined_strips(hists = [], title = '', descrip = ''):
    canv = r.TCanvas()
    lg = r.TLegend(0.23, 0.6, 0.45, 0.89)
    ymax = 0.
    for n, hist in enumerate(hists):

        integ = hist.Integral()
        if integ > 0.: hist.Scale(1./integ)

        if n==0:
            hist.Draw("hist")
        else:
            hist.Draw("histsame")
        hist.SetLineColor(colours()[n])
        hist.SetLineWidth(2)
        title = deepcopy(hist.GetTitle())
        lg.AddEntry(hist, title, "L")
        
        hmax = get_hist_max(hist)
        if hmax > ymax:
            ymax = hmax

    hist.GetXaxis().SetTitle("CSV")
    hist.GetYaxis().SetTitle("Normalised Counts")
    hists[0].SetTitle("CSV Summary")
    lg.Draw()
    lg.SetLineColor(0)
    lg.SetFillColor(0)
    hist.SetMaximum(ymax*1.1) # what is the correct command for this?

    canv.Print("out/qcd_plots_csv_summary_%s.pdf" % descrip)



def main():

    HTbins = ["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"][3:]
    ht_scheme = ["incl", "excl"][0]
    n_j = ["eq2j", "eq3j", "eq4j", "ge5j", "ge2j"]
    n_b = ["ge0b", "eq0b", "eq1b", "eq2b", "eq3b", "ge1b"][:1]
    selec = ["OneMuon", "DiMuon", "Had"][2]
    hist_title = ["genMetPt", "genMetJetPtFrac", "genMetHTFrac"][1:]
    my_path = "Root_Files_08Mar_genMETQCD_v2"

    if ht_scheme == "incl":
        my_iter = [HTbins]
        ht_string = "inclHT"
    elif ht_scheme == "excl":
        my_iter = HTbins

    canv = r.TCanvas()

    for my_title in hist_title:
        for htbin in my_iter:
            if ht_scheme == "excl":
                ht_string = htbin
            n_bin = 1
            
            for nb, nj in product(n_b, n_j):
                h_mc_old = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Had_QCD_skim.root" % my_path,
                                        sele = selec, h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                h_mc_new = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Had_QCD_skim_oldCC_BeamHalo.root" % my_path,
                                        sele = selec, h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                h_mc_new_old = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Had_QCD_skim_newCC_BeamHalo.root" % my_path,
                                        sele = selec, h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                h_mc_old.Draw("hist")
                h_mc_old.SetLineColor(r.kGreen-2)
                h_mc_new_old.Draw("histsame")
                h_mc_new_old.SetLineColor(r.kOrange)
                h_mc_new.Draw("histsame")
                h_mc_new.SetLineColor(r.kRed)
                h_mc_old.RebinX(4)
                h_mc_new.RebinX(4)
                h_mc_new_old.RebinX(4)

                lg = r.TLegend(0.5, 0.75, 0.89, 0.89)
                lg.AddEntry(h_mc_old, "QCD Skim, NewCC, noBeamHaloFilter - %d evts" % h_mc_old.Integral(), "L")
                lg.AddEntry(h_mc_new_old, "QCD Skim, NewCC, withBeamHaloFilter - %d evts" % h_mc_new_old.Integral(), "L")
                lg.AddEntry(h_mc_new, "QCD Skim, OldCC, withBeamHaloFilter - %d evts" % h_mc_new.Integral(), "L")
                lg.Draw()
                lg.SetLineColor(0)
                lg.SetFillColor(0)

                canv.Print("out/qcdcompare_%s_%s_%s_%s.pdf" % (selec, my_title, nb, nj))

if __name__ == "__main__":
    main()
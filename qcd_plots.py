import plot_grabber as grabr
import ROOT as r
from itertools import product
from copy import deepcopy

r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(1)
grabr.set_palette()

def colours():
    return [r.kBlack, r.kRed, r.kBlue-2, r.kGreen-2, r.kYellow]

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
        print xbin
        vals = []
        details["xbinlo"] = hist.GetXaxis().GetBinLowEdge(xbin)
        details["xbinhi"] = hist.GetXaxis().GetBinUpEdge(xbin)
        for ybin in range(1, hist.GetNbinsY()+1):
            print xbin, ybin, hist.GetBinContent(xbin, ybin), hist.GetBinError(xbin, ybin)
            vals.append( (hist.GetYaxis().GetBinCenter(ybin), (hist.GetBinContent(xbin, ybin), hist.GetBinError(xbin, ybin))) )
        slice_hist = print_hist(vals, 'genMet/genJetPt = ', details)
        # print details['xbinlo']
        # if details["xbinlo"] < 1.:
        if len(hist_list) < 4:
            hist_list.append(slice_hist)

    print_combined_strips(hist_list, 'genMet/genJetPt')

def print_combined_strips(hists = [], title = ''):
    canv = r.TCanvas()
    lg = r.TLegend(0.23, 0.6, 0.45, 0.89)
    for n, hist in enumerate(hists):
        print n

        integ = hist.Integral()
        print integ
        if integ > 0.: hist.Scale(1./integ)

        if n==0:
            hist.Draw("hist")
        else:
            hist.Draw("histsame")
        hist.SetLineColor(colours()[n])
        hist.SetLineWidth(2)
        title = deepcopy(hist.GetTitle())
        lg.AddEntry(hist, title, "L")

    hist.GetXaxis().SetTitle("CSV")
    hist.GetYaxis().SetTitle("Normalised Counts")
    hists[0].SetTitle("CSV Summary")
    lg.Draw()
    lg.SetLineColor(0)
    lg.SetFillColor(0)

    canv.Print("out/test.pdf")



def main():

    HTbins = ["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"][3:]
    ht_scheme = ["incl", "excl"][0]
    n_j = ["eq2j", "eq3j", "eq4j", "ge5j", "ge2j"][-1:]
    n_b = ["ge0b", "eq0b", "eq1b", "eq2b", "eq3b", "ge1b"][:1]
    selec = ["OneMuon", "DiMuon", "Had"][2]
    hist_title = ["genMetJetPtFrac", "genMetHTFrac",
                    "neutVectPt_ov_genMet", "numGenNeutrino",
                    "genMetOverJetPt_vs_CSV", "genMetOverJetPt_vs_CSV_c", "genMetOverJetPt_vs_CSV_b",
                    "genMetOverJetPt_vs_CSV_other"][-2:-1]
    my_path = "Root_Files_08Mar_genMETQCD_v2"

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
                                        sele = selec, h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                if "TH1" in str(type(h_mc)):
                    h_mc.Draw()
                elif "TH2" in str(type(h_mc)):
                    is_th2 = True
                    h_mc.Draw("colz")

                if my_title == "neutVectPt_ov_genMet":
                    h_mc.GetXaxis().SetRangeUser(0., 1.5)
                    canv.SetLogy(1)

                if is_th2:
                    h_mc.GetXaxis().SetTitle("genMet/genJetPt")
                    h_mc.GetYaxis().SetTitle("CSV Discriminator")
                    h_mc.RebinX(20)
                    h_mc.RebinY(20)
                    deets = {"nb":nb, "nj": nj, "selec":selec, "title":my_title}
                    print_x_strips(h_mc, deets)
                canv.Print("out/qcdplots_%s_%s_%s_%s.pdf" % (selec, my_title, nb, nj))

if __name__ == "__main__":
    main()
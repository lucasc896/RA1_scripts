import plot_grabber as grabr
import ROOT as r
from itertools import product

r.gStyle.SetOptStat(0)
grabr.set_palette()

def get_distro(key = ""):

    HTbins = ["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"][4:]
    my_path = "QCDKiller_GOLDEN/Root_Files_30April_0p00_fullLatest_noPhi_v0"

    hist = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Had_%s.root" % (my_path, key),
                            sele = "Had", h_title = "AlphaTCorrelation", njet = "ge2j",
                            btag = "ge0b", ht_bins = HTbins, quiet = True)

    return hist

def normalise_unity(h = None):

    for i in range(1, h.GetNbinsX()+1):
        for j in range(1, h.GetNbinsY()+1):
            val = h.GetBinContent(i, j)
            h.SetBinContent(i, j, float(val/h.Integral()))

    return h

def alphat_func(val = 0.55):
    return r.TF1("at_%s" % str(val), "1.0-2.0*("+str(val)+")*sqrt(1.0-x*x)", 0., 1.)

def mht_func(val = 0.55):
    return r.TF1("mht_at_%s" % str(val), "x*(1.-(1./(4*"+str(val)+"**2)))**0.5", 0., 1000.)

def make_bg_plots(bg = None):

    canv = r.TCanvas("c1", "c1", 560, 500)

    bghist = get_distro(bg)

    normalise_unity(bghist)

    bghist.RebinY(2)
    bghist.Draw("col")
    # bghist.SetTitle(bg)

    if bg == "Zinv":
        bghist.SetMaximum(0.02)
        bghist.SetMinimum(0.001)
    elif bg == "QCD":
        bghist.SetMaximum(0.17)
        bghist.SetMinimum(0.002)
    elif bg == "T2cc_250_240":
        # bghist.SetTitle("T2cc (250, 240)")
        bghist.SetMaximum(0.1)
        bghist.SetMinimum(0.008)

    lg = r.TLegend(0.15, 0.7, 0.4, 0.89)

    alphat = {
                "0.65":alphat_func(0.65),
                "0.60":alphat_func(0.60),
                "0.55":alphat_func(0.55),
                "0.54":alphat_func(0.54),
                "0.53":alphat_func(0.53),
                "0.525":alphat_func(0.525),
                "0.52":alphat_func(0.52),
                "0.51":alphat_func(0.51),
                "0.50":alphat_func(0.5),
            }

    colours = [r.kGreen, r.kGreen-2, r.kGreen-5, r.kGreen-3, r.kGreen-4, r.kGreen-5]

    a_vals = sorted(alphat.keys())
    a_vals = ["0.50", "0.55", "0.60", "0.65"]

    for n, val in enumerate(a_vals):
        alphat[val].Draw("same")
        # alphat[val].SetLineColor(colours[n])
        alphat[val].SetLineColor(r.kBlack)
        alphat[val].SetLineWidth(2+2*n)
        lg.AddEntry(alphat[val], "#alpha_{T} = %s" % val, "L")

    bghist.SetTitleSize(0.04, "X")
    bghist.SetTitleSize(0.04, "Y")

    lg.SetLineWidth(0)
    lg.SetLineColor(0)
    lg.SetFillColor(r.kWhite)
    # lg.SetFillStyle(0)
    lg.Draw()

    canv.SetGridx(1)
    canv.SetGridy(1)

    canv.Print("out/alphat_correlation_%s.pdf" % bg)

def make_mht_ht_plots():
    alphat = {
                "0.65":mht_func(0.65),
                "0.60":mht_func(0.60),
                "0.55":mht_func(0.55),
                "0.54":mht_func(0.54),
                "0.53":mht_func(0.53),
                "0.525":mht_func(0.525),
                "0.52":mht_func(0.52),
                "0.51":mht_func(0.51),
                "0.507":mht_func(0.507),
                "0.50":mht_func(0.5),
            }

    canv = r.TCanvas("c1", "c1", 560, 500)

    r.gPad.SetLeftMargin(.12)
    r.gPad.SetRightMargin(.05)
    r.gPad.SetBottomMargin(0.11)
    r.gPad.SetTopMargin(0.05)

    lg = r.TLegend(0.18, 0.65, 0.42, 0.94)

    a_keys = ["0.65", "0.60", "0.55", "0.507"]
    cols = [r.kViolet-6, r.kViolet-1, r.kViolet, r.kViolet-4,] #descending shades of kViolet

    for n, at in enumerate(a_keys):
        if n == 0: alphat[at].Draw()
        else: alphat[at].Draw("same")
        alphat[at].SetLineColor(cols[n])
        alphat[at].SetLineWidth(8-n)
        lg.AddEntry(alphat[at], "#alpha_{T} = %s" % at, "L")

    alphat[a_keys[0]].GetXaxis().SetTitle("H_{T} (GeV)")
    alphat[a_keys[0]].GetYaxis().SetTitle("MH_{T} (GeV)")
    alphat[a_keys[0]].GetXaxis().SetTitleSize(0.045)
    alphat[a_keys[0]].GetXaxis().SetLabelSize(0.04)
    alphat[a_keys[0]].GetXaxis().SetTitleOffset(1.15)
    alphat[a_keys[0]].GetYaxis().SetTitleSize(0.045)
    alphat[a_keys[0]].GetYaxis().SetLabelSize(0.04)
    alphat[a_keys[0]].GetYaxis().SetTitleOffset(1.2)
    alphat[a_keys[0]].SetTitle("")

    lg.SetLineWidth(0)
    lg.SetLineColor(0)
    lg.SetFillColor(r.kWhite)
    # lg.SetFillStyle(0)
    lg.Draw()

    canv.Print("out/mht_correlation.pdf")


def main():

    if [False, True][0]:
        bg = ["QCD", "Zinv", "T2cc_250_240"]
        for b in bg: make_bg_plots(b)
    else:
        make_mht_ht_plots()

if __name__ == "__main__":
    main()
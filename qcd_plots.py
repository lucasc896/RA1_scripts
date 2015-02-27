import plot_grabber as grabr
import ROOT as r
from itertools import product

r.gStyle.SetOptStat(0)
grabr.set_palette()

def main():

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

if __name__ == "__main__":
    main()
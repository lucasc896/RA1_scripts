import plot_grabber as grabr
import ROOT as r
from itertools import product

r.gStyle.SetOptStat(0)
grabr.set_palette()

def main():

    HTbins = ["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"]
    ht_scheme = ["incl", "excl"][0]
    n_j = ["le3j", "ge4j", "ge2j"][:2]
    n_j = ["eq2j", "eq3j", "eq4j", "ge5j"]
    n_b = ["eq0b", "eq1b", "eq2b", "eq3b", "ge0b", "ge1b"][:-2]
    selec = ["OneMuon", "DiMuon", "Had"][2]
    my_path = "Root_Files_09Jan_allLatest_bTagDPhiPlots_dPhi_lt0p3_v0"
    my_title = "MinBiasJetIsB"

    if ht_scheme == "incl":
        my_iter = [HTbins]
        ht_string = "inclHT"
    elif ht_scheme == "excl":
        my_iter = HTbins

    canv = r.TCanvas()
    hist_grid = r.TH2D("MinBiasJetIsB", "MinBiasJetIsB", 2, 0., 2., 16, 0., 16.)
    hist_grid.GetXaxis().SetBinLabel(1, "Not B")
    hist_grid.GetXaxis().SetBinLabel(2, "B")

    for htbin in my_iter:
        if ht_scheme == "excl":
            ht_string = htbin
        n_bin = 1
        for nb, nj in product(n_b, n_j):
            h_data = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Had_Data.root" % my_path,
                                        sele = selec, h_title = my_title, njet = nj,
                                        btag = nb, ht_bins = htbin)
            # h_data.Draw("histtext")
            tot_entries = h_data.GetEntries()
            num_notb = h_data.GetBinContent(1)
            num_b = h_data.GetBinContent(2)

            print "> Cat:", nb, nj
            hist_grid.GetYaxis().SetBinLabel(n_bin, "%s, %s" % (nb, nj))
            print "\tNotB\tB"
            if tot_entries > 0:
                print "\t%.2f%%\t%.2f%%" % (float(num_notb/tot_entries)*100., float(num_b/tot_entries)*100.)
                hist_grid.SetBinContent(1, n_bin, float(num_notb/tot_entries))
                hist_grid.SetBinContent(2, n_bin, float(num_b/tot_entries))
            else:
                print "\tnan nan"
                hist_grid.SetBinContent(1, n_bin, 0.)
                hist_grid.SetBinContent(2, n_bin, 0.)
            # print nb, nj, h_data.GetBinContent(1), h_data.GetBinContent(2), h_data.GetEntries()
            n_bin += 1

    hist_grid.Draw("colztext")
    hist_grid.GetZaxis().SetRangeUser(-0.00001, 1.)
    canv.Print("out/MinBias_isB_grid.pdf")

if __name__ == "__main__":
    main()
import ROOT as r
from itertools import product
import plot_grabber as grabr

def main():

    HTbins = ["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"][:2]
    ht_scheme = ["incl", "excl"][0]
    n_j = ["eq2j", "eq3j", "eq4j", "ge5j"]
    n_b = ["eq0b", "eq1b", "eq2b", "eq3b", "ge0b", "ge1b"][:1]
    selec = ["OneMuon", "DiMuon", "Had"][2]
    my_path = "Root_Files_16Feb_hotspotsFiles_v0/dphi_lt0p3"
    my_title = "ComMinBiasDPhi_jetMap"

    if ht_scheme == "incl":
        my_iter = [HTbins]
        ht_string = "inclHT"
    elif ht_scheme == "excl":
        my_iter = HTbins

    canv = r.TCanvas()

    for htbin in my_iter:
        if ht_scheme == "excl":
            ht_string = htbin
        for nb, nj in product(n_b, n_j):
            h_had_data = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Had_Data.root" % my_path,
                                            sele = "Had", h_title = my_title, njet = nj,
                                            btag = nb, ht_bins = htbin)
            h_had_mc = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Had_EWK.root" % my_path,
                                        sele = "Had", h_title = my_title, njet = nj,
                                        btag = nb, ht_bins = htbin)
            
            # h_mu_data = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Muon_Data.root" % my_path,
            #                                 sele = "OneMuon", h_title = my_title, njet = nj,
            #                                 btag = nb, ht_bins = htbin)
            # h_mu_mc = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Muon_EWK.root" % my_path,
            #                             sele = "OneMuon", h_title = my_title, njet = nj,
            #                             btag = nb, ht_bins = htbin)
            
            h_had_data.Draw("colz")
            canv.Print("out/hotspots_haddata_%s_%s_%s.pdf" % (ht_string, nb, nj))

            h_had_mc.Draw("colz")
            canv.Print("out/hotspots_hadmc_%s_%s_%s.pdf" % (ht_string, nb, nj))            





if __name__ == "__main__":
    main()
import plot_grabber as grabr
import ROOT as r
import math as ma
from itertools import product
from copy import deepcopy

# r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(1)
grabr.set_palette()

class Yield(object):
    def __init__(self, val = 0., err = 0.):
        self.val = val
        self.err = err
        if val > 0.:
            self.fracerr = err/val
        else:
            self.fracerr = 0.

def log():
    return [False, True][1]

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

def alphat_strips(hist = None):
    out_hists = []
    # loop through alphaT values
    for ybin in range(1, hist.GetNbinsY()+1):
        alphat = hist.GetYaxis().GetBinLowEdge(ybin)
        if alphat < 0.5:
            continue
        if alphat>0.65:
            break
        tag = "%.2f_strip" % alphat
        h_strip = r.TH1D(tag, tag, hist.GetNbinsX(), 0., 3.2) # hardcode values as they shouldn't change
        for xbin in range(1, hist.GetNbinsX()+1):
            val = hist.GetBinContent(xbin, ybin)
            err = hist.GetBinError(xbin, ybin)
            # print alphat, hist.GetXaxis().GetBinCenter(xbin), val
            h_strip.SetBinContent(xbin, val)
            h_strip.SetBinError(xbin, err)
        out_hists.append(h_strip)

    return out_hists

def get_dphi_vals(hist = None, cut = 0.3):
    ltcut = 0.
    ltcut_err = 0.
    gtcut = 0.
    gtcut_err = 0.

    for xbin in range(1, hist.GetNbinsX()+1):
        dphi = hist.GetBinCenter(xbin)
        val = hist.GetBinContent(xbin)
        err = hist.GetBinContent(xbin)
        if dphi > cut:
            gtcut += val
            gtcut_err += ma.pow(err, 2)
        else:
            ltcut += val
            ltcut_err += ma.pow(err, 2)

    gtcut_err = ma.sqrt(gtcut_err)
    ltcut_err = ma.sqrt(ltcut_err)

    # if ltcut == 0 or gtcut == 0:
    #     rat = 0
    #     rat_err = 0
    # else:
    #     rat = gtcut/ltcut
    #     rat_err = rat  * ma.sqrt( ma.pow(gtcut_err/gtcut, 2) + ma.pow(ltcut_err/ltcut, 2) )
    
    return Yield(abs(ltcut), ltcut_err), Yield(abs(gtcut), gtcut_err)

def process_dphi_v_at(hist = None, tag = ''):
    
    canv = r.TCanvas()

    tag += "_log" if log() else ""

    # hist.GetYaxis().SetRangeUser(0.5, 0.7)
    # hist.RebinY(4) # set into 0.1 aT binning

    # # draw 2d distro
    # hist.Draw("colz")
    # canv.Print("out/dphi_vs_alphat_%s.pdf" % tag)

    strip_hists = alphat_strips(hist)

    h_dphi_ratio = r.TH1D("dphi_ratio", "dphi_ratio", len(strip_hists), 0.5, 0.65)
    h_dphi_above = r.TH1D("dphi_above", "dphi_above", len(strip_hists), 0.5, 0.65)
    h_dphi_below = r.TH1D("dphi_below", "dphi_below", len(strip_hists), 0.5, 0.65)

    gr_dphi_ratio = r.TGraphErrors(len(strip_hists))
    gr_dphi_above = r.TGraphErrors(len(strip_hists))
    gr_dphi_below = r.TGraphErrors(len(strip_hists))

    cols = [r.kBlack, r.kRed, r.kBlue, r.kGreen-2, r.kOrange, r.kYellow-2, r.kBlue+3, r.kGreen+3,]

    for n, sh in enumerate(strip_hists):
        alphat = float(sh.GetTitle().split("_")[0])
        alphat_bin = h_dphi_ratio.FindBin(alphat)        
        # make plot
        # if n < 8:
        #     if n == 0:
        #         sh.Draw()
        #         sh.GetXaxis().SetTitle("dPhiStar")
        #         sh.GetYaxis().SetTitle("count")
        #     else:
        #         sh.Draw("same")
        #     sh.SetTitle(str(alphat))
        #     sh.SetLineColor(cols[n])

        #     if n==7:
        #         canv.BuildLegend(0.77, 0.13, 0.89, 0.41)
        #         canv.Print("out/dPhiStar_%s_%s.pdf" % (str(alphat).replace(".", "p"), tag))

        # sh.Draw()
        # canv.Print("out/dPhiStar_%s_%s.pdf" % (str(alphat).replace(".", "p"), tag))

        # dphi above and below cut value (0.3)
        dphi_below, dphi_above = get_dphi_vals(sh, 0.3)

        h_dphi_above.SetBinContent(alphat_bin, dphi_above.val)
        h_dphi_above.SetBinError(alphat_bin, dphi_above.err)
        h_dphi_below.SetBinContent(alphat_bin, dphi_below.val)
        h_dphi_below.SetBinError(alphat_bin, dphi_below.err)

        gr_dphi_above.SetPoint(n, alphat+0.0005, dphi_above.val)
        gr_dphi_above.SetPointError(n, 0.005, dphi_above.err)
        gr_dphi_below.SetPoint(n, alphat-0.0005, dphi_below.val)
        gr_dphi_below.SetPointError(n, 0.005, dphi_below.err)

        # ratio between the two
        if dphi_below.val == 0 or dphi_above.val == 0:
            rat = 0
            rat_err = 0
        else:
            rat = dphi_above.val/dphi_below.val
            rat_err = rat  * ma.sqrt( ma.pow(dphi_above.err/dphi_above.val, 2) + ma.pow(dphi_below.err/dphi_below.val, 2) )

        ratio = Yield(rat, rat_err)

        h_dphi_ratio.SetBinContent(alphat_bin, ratio.val)
        h_dphi_ratio.SetBinError(alphat_bin, ratio.err)

        gr_dphi_ratio.SetPoint(n, alphat, ratio.val)
        gr_dphi_ratio.SetPointError(n, 0.005, ratio.err)

    # h_dphi_above.Draw()
    # h_dphi_above.SetLineColor(r.kBlue)
    # h_dphi_below.Draw("same")
    # h_dphi_below.SetLineColor(r.kRed)
    # h_dphi_above.SetTitle("dPhi Yields")
    
    canv.SetLogy(log())
    canv.SetGridy(1)
    r.gStyle.SetOptStat(0)

    # lg = r.TLegend(0.7, 0.75, 0.89, 0.89)
    # lg.AddEntry(h_dphi_above, "dPhiStar > 0.3", "L")
    # lg.AddEntry(h_dphi_below, "dPhiStar < 0.3", "L")
    # lg.SetLineColor(0)
    # lg.SetFillColor(0)
    # lg.Draw()
    # canv.Print("out/dphi_yield_vs_alphat_%s.pdf" % tag)

    # # draw ratio plots
    # h_dphi_ratio.Draw("e1")
    # h_dphi_ratio.GetXaxis().SetTitle("alphaT")
    # h_dphi_ratio.GetYaxis().SetTitle("R(dPhi>0.3/dPhi<0.3)")
    # canv.Print("out/dphi_rat_vs_alphat_%s.pdf" % tag)

    # draw graphs

    mgr_dphi = r.TMultiGraph()

    # gr_dphi_below.Draw("AP")
    gr_dphi_below.SetMarkerStyle(7)
    gr_dphi_below.SetLineColor(r.kRed)
    gr_dphi_below.SetMarkerColor(r.kRed)
    gr_dphi_below.SetTitle("#Delta #phi * < 0.3")
    gr_dphi_below.GetXaxis().SetTitle("#alpha_{T}")
    gr_dphi_below.GetYaxis().SetTitle("Yield")

    mgr_dphi.Add(gr_dphi_below)

    # gr_dphi_above.Draw("AP")
    gr_dphi_above.SetMarkerStyle(7)
    gr_dphi_above.SetLineColor(r.kBlue)
    gr_dphi_above.SetMarkerColor(r.kBlue)
    gr_dphi_above.SetTitle("#Delta #phi * > 0.3")
    gr_dphi_above.GetXaxis().SetTitle("#alpha_{T}")

    mgr_dphi.Add(gr_dphi_above)
    mgr_dphi.Draw("AP")
    mgr_dphi.GetXaxis().SetTitle("#alpha_{T}")
    mgr_dphi.GetYaxis().SetTitle("Yield")
    canv.BuildLegend(0.7, 0.8, 0.89, 0.89)
    canv.Print("out/gr_dphi_yields_%s.pdf" % tag)

    gr_dphi_ratio.Draw("AP")
    gr_dphi_ratio.SetTitle("R(#Delta #phi * > 0.3) / R(#Delta #phi * < 0.3)")
    gr_dphi_ratio.GetXaxis().SetTitle("#alpha_{T}")
    gr_dphi_ratio.GetYaxis().SetTitle("Ratio")
    canv.Print("out/gr_dphi_ratio_%s.pdf" % tag)

def make_cumu(hist = None):
    cumu = hist.Clone()

    cumu_val = 0
    cumu_err = 0
    for n in list(reversed(range(1, hist.GetNbinsX()+1))):
        val = hist.GetBinContent(n)
        err = hist.GetBinError(n)
        cumu_val += val
        cumu_err = ma.sqrt(ma.pow(cumu_err, 2) + ma.pow(err, 2))
        cumu.SetBinContent(n, cumu_val)
        cumu.SetBinError(n, cumu_err)
        if hist.FindBin(0.679) == n:
            cutval = cumu_val
    print "Fraction above 0.679: %.3f" % float(cutval/cumu_val)
    cumu.SetTitle(hist.GetTitle() + " - cumu")

    return cumu

def make_pred_plot(h_sig_mc = None, h_cont_data = None, h_cont_mc = None, flat = False):

    h_sig_pred = h_sig_mc.Clone()
    if flat:
        transfer = float(h_cont_data.Integral()/h_cont_mc.Integral())
        h_sig_pred.Scale(transfer)
    else:
        h_sig_pred.Multiply(h_cont_data)
        h_sig_pred.Divide(h_cont_mc)

    return h_sig_pred

def main():

    HTbins = ["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"][-4:]
    ht_scheme = ["incl", "excl"][0]
    n_j = ["eq2j", "eq3j", "eq4j", "ge5j", "ge2j"]
    n_j = ["le3j", "ge4j", "ge2j"]
    n_b = ["ge0b", "eq0b", "eq1b", "eq2b", "eq3b", "ge1b"][:1]
    selec = ["OneMuon", "DiMuon", "Had"][2]
    hist_title = ["genMetJetPtFrac", "genMetHTFrac",
                    "neutVectPt_ov_genMet", "numGenNeutrino",
                    "genMetOverJetPt_vs_CSV", "genMetOverJetPt_vs_CSV_c", "genMetOverJetPt_vs_CSV_b",
                    "genMetOverJetPt_vs_CSV_other", "ComMinBiasDPhi_vs_alphaT", "dphiJet_CSV", "dphiJet_vs_CSV"][-3:-2]
    # hist_title = ["AlphaT"]
    scenario = ["data_gt0p3", "data_lt0p3", "qcd_lt0p3", "other"][3]

    if scenario == "data_gt0p3":
        my_path = "QCDKiller_GOLDEN/Root_Files_03April_0p507_fullLatest_htTrigs_dphigt0p3_v0"
    elif scenario == "data_lt0p3":
        my_path = "QCDKiller_GOLDEN/Root_Files_03April_0p507_fullLatest_htTrigs_dphilt0p3_v0"
    elif scenario == "qcd_lt0p3":
        my_path = "QCDKiller_GOLDEN/Root_Files_03April_0p507_fullLatest_htTrigs_v0"
    elif scenario == "other":
        my_path = "QCDKiller_GOLDEN/Root_Files_19May_0p00_fullLatest_noPhi_v0"
    
    print scenario

    if ht_scheme == "incl":
        my_iter = [HTbins]
        ht_string = "inclHT"
    elif ht_scheme == "excl":
        my_iter = HTbins

    canv = r.TCanvas()

    r.gStyle.SetOptStat(0)

    for my_title in hist_title:
        is_th2 = False
        for htbin in my_iter:
            if ht_scheme == "excl":
                ht_string = htbin
            n_bin = 1
            
            for nb, nj in product(n_b, n_j):
                
                # h_had_data = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Had_Data.root" % my_path,
                #                                 sele = "Had", h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                # h_had_mc_zinv = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Had_Zinv.root" % my_path,
                #                                     sele = "Had", h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                # h_had_mc_tt = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Had_TTbar.root" % my_path,
                #                                 sele = "Had", h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                # h_had_mc_wj = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Had_WJets.root" % my_path,
                #                                     sele = "Had", h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                # h_had_mc_dibo = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Had_DiBoson.root" % my_path,
                #                                     sele = "Had", h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                # h_had_mc_dy = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Had_DY.root" % my_path,
                #                                 sele = "Had", h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                # h_had_mc_t = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Had_SingleTop.root" % my_path,
                #                                     sele = "Had", h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                if "data" not in scenario:
                    h_had_mc_qcd = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Had_QCD_v2.root" % my_path,
                                                        sele = "Had", h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                else:
                    h_had_mc_qcd = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Had_Data_updatedPlots.root" % my_path,
                                                        sele = "Had", h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                # h_had_mc_qcd.SetTitle("dPhi_jet CSV")
                # # had ttw numer is all apart from zinv
                # h_had_mc_ttw_num = h_had_mc_tt.Clone()
                # h_had_mc_ttw_num.Add(h_had_mc_wj)
                # h_had_mc_ttw_num.Add(h_had_mc_dy)
                # h_had_mc_ttw_num.Add(h_had_mc_t)
                # h_had_mc_ttw_num.Add(h_had_mc_dibo)

                # # had zinv numer is zinv
                # h_had_mc_zinv_num = h_had_mc_zinv.Clone()

                # h_mu_data = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Muon_Data.root" % my_path,
                #                             sele = "OneMuon", h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                # h_mu_mc_zinv = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Muon_Zinv.root" % my_path,
                #                                     sele = "OneMuon", h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                # h_mu_mc_tt = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Muon_TTbar.root" % my_path,
                #                                 sele = "OneMuon", h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                # h_mu_mc_wj = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Muon_WJets.root" % my_path,
                #                                     sele = "OneMuon", h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                # h_mu_mc_dibo = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Muon_DiBoson.root" % my_path,
                #                                     sele = "OneMuon", h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                # h_mu_mc_dy = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Muon_DY.root" % my_path,
                #                                 sele = "OneMuon", h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                # h_mu_mc_t = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Muon_SingleTop.root" % my_path,
                #                                     sele = "OneMuon", h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                
                # # denom is everything
                # h_mu_mc_denom = h_mu_mc_zinv.Clone()
                # h_mu_mc_denom.Add(h_mu_mc_tt)
                # h_mu_mc_denom.Add(h_mu_mc_wj)
                # h_mu_mc_denom.Add(h_mu_mc_dy)
                # h_mu_mc_denom.Add(h_mu_mc_t)
                # h_mu_mc_denom.Add(h_mu_mc_dibo)



                # h_mumu_data = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Muon_Data.root" % my_path,
                #                                 sele = "DiMuon", h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                # h_mumu_mc_zinv = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Muon_Zinv.root" % my_path,
                #                                     sele = "DiMuon", h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                # h_mumu_mc_tt = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Muon_TTbar.root" % my_path,
                #                                 sele = "DiMuon", h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                # h_mumu_mc_wj = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Muon_WJets.root" % my_path,
                #                                     sele = "DiMuon", h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                # h_mumu_mc_dibo = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Muon_DiBoson.root" % my_path,
                #                                     sele = "DiMuon", h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                # h_mumu_mc_dy = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Muon_DY.root" % my_path,
                #                                 sele = "DiMuon", h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                # h_mumu_mc_t = grabr.grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/%s/Muon_SingleTop.root" % my_path,
                #                                     sele = "DiMuon", h_title = my_title, njet = nj, btag = nb, ht_bins = htbin, quiet = True)
                
                # # mumu denom is everything
                # h_mumu_mc_denom = h_mumu_mc_zinv.Clone()
                # h_mumu_mc_denom.Add(h_mumu_mc_tt)
                # h_mumu_mc_denom.Add(h_mumu_mc_wj)
                # h_mumu_mc_denom.Add(h_mumu_mc_dy)
                # h_mumu_mc_denom.Add(h_mumu_mc_t)
                # h_mumu_mc_denom.Add(h_mumu_mc_dibo)

                # h_ttw_pred = make_pred_plot(h_sig_mc = h_had_mc_ttw_num,
                #                             h_cont_data = h_mu_data,
                #                             h_cont_mc = h_mu_mc_denom)
                # h_ttw_pred_flat = make_pred_plot(h_sig_mc = h_had_mc_ttw_num,
                #                                     h_cont_data = h_mu_data,
                #                                     h_cont_mc = h_mu_mc_denom, flat = True)

                # # zinv pred from mumu sample only (no photons!)
                # h_zinv_pred = make_pred_plot(h_sig_mc = h_had_mc_zinv_num,
                #                                 h_cont_data = h_mumu_data,
                #                                 h_cont_mc = h_mumu_mc_denom)
                # h_zinv_pred_flat = make_pred_plot(h_sig_mc = h_had_mc_zinv_num,
                #                                     h_cont_data = h_mumu_data,
                #                                     h_cont_mc = h_mumu_mc_denom, flat = True)

                # procs = [ "wj", "tt", "t", "dy", "zinv", "dibo"]

                # print "\nHAD"
                # had_mc_tot = 0
                # for proc in procs:
                #     histo = eval("h_had_mc_%s" % proc)
                #     inte = histo.Integral()
                #     had_mc_tot += inte
                #     print proc, "\t",  inte
                # print "had mc tot:\t", had_mc_tot

                # print "\nMU"
                # mu_mc_tot = 0
                # for proc in procs:
                #     histo = eval("h_mu_mc_%s" % proc)
                #     inte = histo.Integral()
                #     mu_mc_tot += inte
                #     print proc, "\t",  inte
                # print "mu mc tot:\t", mu_mc_tot
                # print "mu data:\t", h_mu_data.Integral()

                # print "\nMUMU"
                # mumu_mc_tot = 0
                # for proc in procs:
                #     histo = eval("h_mumu_mc_%s" % proc)
                #     inte = histo.Integral()
                #     mumu_mc_tot += inte
                #     print proc, "\t",  inte
                # print "mumu mc tot:\t", mumu_mc_tot
                # print "mumu data:\t", h_mumu_data.Integral()

                # print "\nPREDS"
                # h_ttw_pred.Draw("colz")
                # print "ttw pred:\t", h_ttw_pred.Integral()
                # h_ttw_pred.GetZaxis().SetRangeUser(0., 2000.)
                # # canv.Print("out/had_pred_ttw.pdf")

                # h_zinv_pred.Draw("colz")
                # print "zinv pred:\t", h_zinv_pred.Integral()
                # # canv.Print("out/had_pred_zinv.pdf")

                # print "pred:\t\t", h_ttw_pred.Integral()+h_zinv_pred.Integral()

                # # excess = data - (ttw_pred + zinv_pred)
                # h_had_excess = h_had_data.Clone()
                # h_had_excess.Add(h_ttw_pred, -1.)
                # h_had_excess.Add(h_zinv_pred, -1.)

                # h_had_excess_flat = h_had_data.Clone()
                # h_had_excess_flat.Add(h_ttw_pred_flat, -1.)
                # h_had_excess_flat.Add(h_zinv_pred_flat, -1.)

                # h_had_excess_flat.Draw("colz")
                # print "had data:\t", h_had_data.Integral()
                # print "had excess:\t", h_had_excess_flat.Integral()
                # h_had_excess_flat.GetZaxis().SetRangeUser(0., 100.)
                # # canv.Print("out/had_excess.pdf")

                # process_dphi_v_at(h_had_excess_flat, "%s_%s" % (nb, nj))

                # continue

                if "TH1" in str(type(h_had_mc_qcd)):
                    h_had_mc_qcd.Draw()
                elif "TH2" in str(type(h_had_mc_qcd)):
                    is_th2 = True
                    h_had_mc_qcd.Draw("colz")

                if my_title == "neutVectPt_ov_genMet":
                    h_had_mc_qcd.GetXaxis().SetRangeUser(0., 1.5)
                    canv.SetLogy(1)

                if "dphiJet_CSV" == my_title:
                    h_had_mc_qcd.RebinX(1)
                    h_had_mc_qcd.SetMarkerStyle(20)

                if "dphiJet_vs_CSV" == my_title:
                    # h_had_mc_qcd.RebinX(2)
                    h_had_mc_qcd.RebinY(30)

                if is_th2:
                    if "genMetOverJetPt_vs_CSV" in my_title:
                        h_had_mc_qcd.GetXaxis().SetTitle("genMet/genJetPt")
                        h_had_mc_qcd.GetYaxis().SetTitle("CSV Discriminator")
                        h_had_mc_qcd.RebinX(20)
                        h_had_mc_qcd.RebinY(20)
                        deets = {"nb":nb, "nj": nj, "selec":selec, "title":my_title}
                        print_x_strips(h_had_mc_qcd, deets)
                    elif "ComMinBiasDPhi_vs_alphaT" in my_title:
                        process_dphi_v_at(h_had_mc_qcd, "%s_%s" % (nb, nj))
                        # h_had_mc_qcd.GetYaxis().SetRangeUser(0.5, 0.7)
                        # h_had_mc_qcd.RebinY(4)
                        # continue
                        # h_had_mc_qcd.SetMaximum(100000)
                        canv.SetLogz(1)
                        h_had_mc_qcd.GetXaxis().SetRangeUser(0., 0.5)
                        h_had_mc_qcd.GetYaxis().SetRangeUser(0.45, 0.6)
                canv.Print("out/qcdplots_%s_%s_%s_%s_%s.pdf" % (selec, my_title, nb, nj, scenario))

                if not is_th2:
                    cumu_qcd = make_cumu(h_had_mc_qcd)
                    cumu_qcd.Draw("")
                    cumu_qcd.SetMarkerColor(r.kCyan+1)
                    canv.Print("out/qcdplots_%s_%s_%s_%s_cumu_%s.pdf" % (selec, my_title, nb, nj, scenario))                

if __name__ == "__main__":
    main()
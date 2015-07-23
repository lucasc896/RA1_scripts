import ROOT as r
from copy import deepcopy
from array import array

def set_palette(name="", ncontours=100):
    """Set a color palette from a given RGB list
    stops, red, green and blue should all be lists of the same length
    see set_decent_colors for an example"""

    if name == "gray" or name == "grayscale":
        stops = [0.00, 0.34, 0.61, 0.84, 1.00]
        red   = [1.00, 0.84, 0.61, 0.34, 0.00]
        green = [1.00, 0.84, 0.61, 0.34, 0.00]
        blue  = [1.00, 0.84, 0.61, 0.34, 0.00]
    # elif name == "whatever":
        # (define more palettes)
    else:
        # default palette, looks cool
        stops = [0.00, 0.34, 0.61, 0.84, 1.00]
        red   = [0.50, 0.00, 0.87, 1.00, 0.51]
        green = [0.00, 0.81, 1.00, 0.20, 0.00]
        blue  = [0.81, 1.00, 0.12, 0.00, 0.00]

    stops_ = array('d', stops)
    red_ = array('d', red)
    green_ = array('d', green)
    blue_ = array('d', blue)

    npoints = len(stops_)
    r.TColor.CreateGradientColorTable(npoints, stops_, red_, green_, blue_, ncontours)
    r.gStyle.SetNumberContours(ncontours)

def get_dirs(htbins = None, sele = "", btag = "", keyword = ""):
    """get the list of dirs to access multi files"""

    btag_str = btag_string(btag)

    # if htbins is a string, make it a single length list
    if type(htbins) == type(""):
        htbins = [htbins]

    out = []
    for ht in htbins:
        this_bin = []
        if sele == "QCD": this_bin.append(sele)
        if btag_str: this_bin.append(btag_str)
        if sele not in ["Had", "QCD"]:
            this_bin.append(sele)
        this_bin.append(ht)
        if keyword: this_bin.append(keyword)
        out.append("_".join(this_bin))
    return out

def btag_string(btag = ""):
    """get the relevant btag histo string"""

    d = {
            "eq0b": "btag_zero",
            "eq1b": "btag_one",
            "eq2b": "btag_two",
            "eq3b": "btag_three",
            "ge0b": "",
            "ge1b": "btag_morethanzero"
        }

    return d[btag]

def jet_string(jet = ""):
    """get the relevant jet histo string"""

    jet_cats = {
        "eq2j": "1",
        "eq3j": "2",
        "eq4j": "3",
        "ge5j": "4",
        "ge2j": "all",
        "le3j": "2",
        "ge4j": "3",
    }

    try:
        return jet_cats[jet]
    except KeyError:
        return None

def trig_eff(sele = "OneMuon", ht = "", njet = "", quiet = False, fineJet = True):
    """ list trigger efficiencies """

    if fineJet:
        # if inclusive jet selection, use ge5j effs
        if njet == "all":
            njet = "4"

        if "OneMuon" in sele:
            d = {"150_1": 0.872,"150_2": 0.872,"150_3": 0.881,"150_4": 0.881,
                    "200_1": 0.875,"200_2": 0.875,"200_3": 0.881,"200_4": 0.881,
                    "275_1": 0.878,"275_2": 0.878,"275_3": 0.882,"275_4": 0.882,
                    "325_1": 0.879,"325_2": 0.879,"325_3": 0.884,"325_4": 0.884,
                    "375_1": 0.881,"375_2": 0.881,"375_3": 0.886,"375_4": 0.886,
                    "475_1": 0.882,"475_2": 0.882,"475_3": 0.888,"475_4": 0.888,
                    "575_1": 0.884,"575_2": 0.884,"575_3": 0.889,"575_4": 0.889,
                    "675_1": 0.885,"675_2": 0.885,"675_3": 0.890,"675_4": 0.890,
                    "775_1": 0.886,"775_2": 0.886,"775_3": 0.891,"775_4": 0.891,
                    "875_1": 0.888,"875_2": 0.888,"875_3": 0.890,"875_4": 0.890,
                    "975_1": 0.887,"975_2": 0.887,"975_3": 0.890,"975_4": 0.890,
                    "1075_1":0.884,"1075_2":0.884,"1075_3":0.896,"1075_4":0.896,}
        if "DiMuon" in sele:
            d = {"150_1": 0.984, "150_2": 0.984, "150_3": 0.984, "150_4": 0.984,
                    "200_1": 0.985, "200_2": 0.985, "200_3": 0.984, "200_4": 0.984,
                    "275_1": 0.985, "275_2": 0.985, "275_3": 0.984, "275_4": 0.984,
                    "325_1": 0.986, "325_2": 0.986, "325_3": 0.986, "325_4": 0.986,
                    "375_1": 0.986, "375_2": 0.986, "375_3": 0.985, "375_4": 0.985,
                    "475_1": 0.986, "475_2": 0.986, "475_3": 0.986, "475_4": 0.986,
                    "575_1": 0.986, "575_2": 0.986, "575_3": 0.986, "575_4": 0.986,
                    "675_1": 0.987, "675_2": 0.987, "675_3": 0.986, "675_4": 0.986,
                    "775_1": 0.986, "775_2": 0.986, "775_3": 0.986, "775_4": 0.986,
                    "875_1": 0.987, "875_2": 0.987, "875_3": 0.986, "875_4": 0.986,
                    "975_1": 0.987, "975_2": 0.987, "975_3": 0.988, "975_4": 0.988,
                    "1075_1":0.987, "1075_2":0.987, "1075_3":0.987, "1075_4":0.987,}
        if sele in ["Had", "QCD"]:
            # note: these effs should be updated with new numbers from Adam
            d = {"200_1":0.84,"200_2":0.78, "200_3":0.72, "200_4":0.72, #200_4 is nan, so assume same as 200_3
                    "275_1":0.95,"275_2":0.95, "275_3":0.92,"275_4":0.95,
                    "325_1":0.99,"325_2":0.97, "325_3":0.97,"325_4":1.,
                    "375_1":0.99,"375_2":0.99, "375_3":0.99,"375_4":0.97,
                    "475_1":1.,  "475_2":1.,   "475_3":1.0, "475_4":1.0,
                    "575_1":1.,  "575_2":1.,   "575_3":1.,  "575_4":1.,
                    "675_1":1.,  "675_2":1.,   "675_3":1.,  "675_4":1.,
                    "775_1":1.,  "775_2":1.,   "775_3":1.,  "775_4":1.,
                    "875_1":1.,  "875_2":1.,   "875_3":1.,  "875_4":1.,
                    "975_1":1.,  "975_2":1.,   "975_3":1.,  "975_4":1.,
                    "1075_1":1., "1075_2":1.,  "1075_3":1., "1075_4":1.,}
    else:
        if njet == "all":
            njet = "2"

        if "OneMuon" in sele:
            d = {"150_2": 0.872,"150_3": 0.881,
                      "200_2": 0.875,"200_3": 0.881,
                      "275_2": 0.878,"275_3": 0.882,
                      "325_2": 0.879,"325_3": 0.884,
                      "375_2": 0.881,"375_3": 0.886,
                      "475_2": 0.882,"475_3": 0.888,
                      "575_2": 0.884,"575_3": 0.889,
                      "675_2": 0.885,"675_3": 0.890,
                      "775_2": 0.886,"775_3": 0.891,
                      "875_2": 0.888,"875_3": 0.890,
                      "975_2": 0.887,"975_3": 0.890,
                      "1075_2":0.884,"1075_3":0.896,}
        if "DiMuon" in sele:
            d = {"150_2": 0.984,"150_3": 0.984,
                        "200_2": 0.985,"200_3": 0.984,
                        "275_2": 0.985,"275_3": 0.984,
                        "325_2": 0.986,"325_3": 0.986,
                        "375_2": 0.986,"375_3": 0.985,
                        "475_2": 0.986,"475_3": 0.986,
                        "575_2": 0.986,"575_3": 0.986,
                        "675_2": 0.987,"675_3": 0.986,
                        "775_2": 0.986,"775_3": 0.986,
                        "875_2": 0.987,"875_3": 0.986,
                        "975_2": 0.987,"975_3": 0.988,
                        "1075_2":0.987,"1075_3":0.987,}
        if sele in ["Had", "QCD"]:
            # note: these effs should be updated with new numbers from Adam
            d = {
                    "200_2":0.818,  "200_3":0.789,
                    "275_2":0.952,  "275_3":0.900,
                    "325_2":0.978,  "325_3":0.959,
                    "375_2":0.992,  "375_3":0.987,
                    "475_2":0.998,  "475_3":0.996,
                    "575_2":1.,     "575_3":1.,
                    "675_2":1.,     "675_3":1.,
                    "775_2":1.,     "775_3":1.,
                    "875_2":1.,     "875_3":1.,
                    "975_2":1.,     "975_3":1.,
                    "1075_2":1.,    "1075_3":1.,}

    if not quiet:
        print "> Trig corr (%s): %.3f" % (ht+"_"+njet, d[ht+"_"+njet])

    return d[ht+"_"+njet]

def lumi(sele = "mu", quiet = False):
    """get the luminosity in fb-1"""

    d = {
            "QCD": 18.493,
            "Had": 18.493,
            "OneMuon": 19.131,
            "DiMuon": 19.131,
            "ph": 19.12,
    }

    if not quiet:
        print "> Lumi corr (%s): %.3f (*10.)" % (sele, d[sele])

    return d[sele]*10.

def sb_corr(samp = "", quiet = False):
    """get the process sideband correction"""

    if not samp:
        return 1.

    d = {
            "Zinv": .94,
            "WJets": .93,
            "DY": .94,
            "TTbar": 1.18,
            "DiBoson": 1.,
            "SingleTop": 1.18,
            "EWK": 1.,
            "QCD": 1.,
    }

    if not quiet:
        print "> Sb corr (%s): %.2f" % (samp, d[samp])
        if samp == "EWK":
            print ">>> Note: EWK root file has no distinct sb corr. Weight = 1."

    return d[samp]

def grab_plots(f_path = "", h_title = "", sele = "OneMuon", njet = "", btag = "", ht_bins = [], quiet = False, weight = None):
    """main function to extract single plot from various cats"""

    if f_path:
        f = r.TFile.Open(f_path)
        if not quiet:
            print "> Opening file:", f_path
    else:
        return

    h_total = None
    for d in get_dirs(htbins = ht_bins, sele = sele, btag = btag):
        
        try:
            h = f.Get("%s/%s_%s" % (d, h_title, jet_string(njet))).Clone()
            if not quiet:
                print "> Grabbing histogram: %s/%s_%s" % (d, h_title, jet_string(njet)) 
        except ReferenceError:
            print ">>> Failed to get histogram."
            print "-    %s" % f_path
            print "-    %s/%s_%s" % (d, h_title, jet_string(njet))
            exit()
        if "Data" not in f_path:
            # apply ht bin trig effs
            h.Scale( trig_eff(sele = sele,
                            ht = d.split("_")[-2] if "1075" != d[-4:] else d.split("_")[-1],
                            njet = jet_string(njet), quiet = quiet,
                            fineJet = False) )
            if "SMS" not in f_path.split("/")[-1]:
                h.Scale( sb_corr(f_path.split("/")[-1].split("_")[1][:-5], quiet = quiet) )
            h.Scale( lumi(sele, quiet = quiet) )
        
        if weight:
            h.Scale(weight)

        if not h_total:
            h_total = h.Clone()
        else:
            h_total.Add(h)

    if "TH2" in str(type(h_total)):
        h_total.RebinX(1)
        # h_total.RebinY(10)

    h_total_clone = deepcopy(h_total)
    f.Close()

    return h_total_clone

if __name__ == "__main__":
    print ">>> Running plot_grabber debugger."
    try:
        for jet_cat in ["eq2j", "eq3j", "eq4j", "ge5j"]:
            for b_cat in ["eq0b", "eq1b"]:
                dave = grab_plots(f_path = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/Root_Files_21Dec_alphaT_0p53_fullHT_fixedCC_fineJetMulti_dPhi_lt0p3_v0/Muon_DY.root",
                                    sele = "OneMuon", h_title = "AlphaT", njet = jet_cat,
                                    btag = b_cat, ht_bins = ["475_575"])
    except:
        print "\n\n", "*"*40
        print "\tBalls up."
        print "*"*40, "\n"
        raise
    else:
        print "\n\n", "*"*40
        print "\tHoo mutha fuckin ray!"
        print "*"*40, "\n"
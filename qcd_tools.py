import ROOT as r
from sys import exit
from copy import deepcopy
from alphat_excess import dict_printer
import plot_grabber as grabr

######################################################################

# TO-DO

# 1. Get HT trigger effs
# 2. Setup QCD muon selection in plot grabber
# 3. Wrap the yield collector into an object
    # can then create an instance and use functions to access yields

######################################################################

class Yield(object):
    """container for a yield and err"""
    def __init__(self, val, err):
        self.v = float(val)
        self.e = float(err)
        try:
            self.fe = float(err/val)
        except ZeroDivisionError:
            self.fe = 0.
    def __str__(self):
        return "Yield: %.3f +/- %.3f" % (self.v, self.e)

######################################################################

class CatYield(object):
    """object to hold a bunch of yields, recursively"""
    def __init__(self, cats = []):
        self._cats = cats if cats else []


    def AddCat(self, cat = "", val = None):
        # print cat, val, self._cats
        if cat in self._cats:
            print "%s already exists." % cat
        setattr(self, cat, val)
        self._cats.append(cat)

    def __str__(self):
        out = "\n-CatYield object-\n"
        # out = ""
        out += "Cats: " + ", ".join(self._cats) + "\n"
        
        for cat in self._cats:
            try:
                out += "%s: %s\n" % (cat, getattr(self, cat))
            except AttributeError:
                pass    
        # out += "+++"
        
        return out

######################################################################

def bins(key = ""):
    try:
        return {"nj": ["le3j", "ge4j", "ge2j"],
                "nb": ["eq0b", "eq1b", "eq2b", "eq3b", "ge0b"],
                "htbins": ["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"]}[key]
    except:
        return None

######################################################################

def fpath():
    return "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/QCDKiller_GOLDEN/QCDFiles/25March_withBeamHalo_newCC_v0/"

######################################################################

def get_yields(selec = "", data = True):

    if data:
        files = ["Had_Data"]
    else:
        files = ["Had_TTbar", "Had_SingleTop", "Had_WJets", "Had_DY", "Had_Zinv", "Had_DiBoson"]

    d = dict.fromkeys(["lt0p3", "gt0p3"])
    for dphi in ["lt0p3", "gt0p3"]:
        d[dphi] = dict.fromkeys(bins("nj"))
        for j in bins("nj"):
            d[dphi][j] = dict.fromkeys(bins("nb"))
            for b in bins("nb"):
                d[dphi][j][b] = dict.fromkeys(bins("htbins"))
                for ht in bins("htbins"):
                    htotal = None
                    for fname in files:
                        hist = grabr.grab_plots(f_path = "%s/%s/%s.root" % (fpath(), dphi, fname),
                                                sele = "QCD", h_title = "AlphaT_Signal", njet = j,
                                                btag = b, quiet = True, ht_bins = ht)
                        if not htotal:
                            htotal = hist.Clone()
                        else:
                            htotal.Add(hist)
                    err = r.Double(0.)
                    val = htotal.IntegralAndError(1, htotal.GetNbinsX()+1, err)
                    d[dphi][j][b][ht] = Yield(val, err)

    return d

######################################################################

if __name__ == "__main__":
    
    had_data = get_yields("QCD")
    had_mc = get_yields("QCD", data = False)
    dict_printer(had_data)

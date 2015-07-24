import ROOT as r
import math as ma
import plot_grabber as grabr
from sys import exit
from copy import deepcopy
from alphat_excess import dict_printer
from itertools import product

######################################################################
"""
TO-DO
2. Add an additional alphaT dimension
3. Verify yield from grabr are correct!
4. Correct the erorr handling of the Yield addition/subtraction
"""
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
    def __add__(self, other):
        totv = self.v + other.v
        tote = ma.sqrt( ma.pow(self.e, 2) + ma.pow(other.e, 2) )
        return Yield(totv, tote)
    def __sub__(self, other):
        totv = self.v - other.v
        tote = ma.sqrt( ma.pow(self.e, 2) + ma.pow(other.e, 2) )
        return Yield(totv, tote)

######################################################################

def exclusiveCats(dim = ""):
    try:
        return {"nj": bins("nj"),
                "nb": bins("nb"),
                "ht": bins("ht"),
                "at": ["all"],
                "dphi": ["lt0p3", "gt0p3"]}[dim]
    except KeyError:
        return []

######################################################################

class AnalysisYields(object):
    def __init__(self, selec = "", fpath = "", bins = {}, data = True, zeroes = False):
        print "> Creating AnalysisYields object for %s selection in %s" % (selec,
            "data" if data else "MC")

        self._defaultArgs = ["ht", "nj", "nb", "dphi"]
        self._fpath = fpath
        self._selec = selec
        self._data = data
        self._zeroes = zeroes
        self._bins = bins
        self.ValidateBins()
        self.HarvestYields()

    def ValidateBins(self):
        for arg in self._defaultArgs:
            assert arg in self._bins.keys(), "Default bin argument %s missing." % arg

    def HarvestYields(self):
        if self._data:
            files = ["Had_Data"]
        else:
            files = ["Had_TTbar", "Had_SingleTop", "Had_WJets", "Had_DY", "Had_Zinv", "Had_DiBoson"]

        self._dict = dict.fromkeys(self._bins["dphi"])
        for dphi in ["lt0p3", "gt0p3"]:
            self._dict[dphi] = dict.fromkeys(self._bins["nj"])
            for j in self._bins["nj"]:
                self._dict[dphi][j] = dict.fromkeys(self._bins["nb"])
                for b in self._bins["nb"]:
                    self._dict[dphi][j][b] = dict.fromkeys(self._bins["ht"])
                    for ht in self._bins["ht"]:
                        if self._zeroes:
                            self._dict[dphi][j][b][ht] = Yield(0., 0.)
                            continue
                        htotal = None
                        for fname in files:
                            hist = grabr.grab_plots(f_path = "%s/%s/%s.root" % (self._fpath, dphi, fname),
                                                    sele = self._selec, h_title = "AlphaT_Signal", njet = j,
                                                    btag = b, quiet = True, ht_bins = ht)
                            if not htotal:
                                htotal = hist.Clone()
                            else:
                                htotal.Add(hist)
                        err = r.Double(0.)
                        val = htotal.IntegralAndError(1, htotal.GetNbinsX()+1, err)
                        self._dict[dphi][j][b][ht] = Yield(val, err)
                    # make inclusive ht cat
                    self._dict[dphi][j][b]['inc'] = self.MakeInclusiveHTYield(self._dict[dphi][j][b], "ht")
        # make inclusive dphi cat
        self._dict['inc'] = dict_sum(self._dict['lt0p3'], self._dict['gt0p3'])


    def MakeInclusiveHTYield(self, dic = {}, dim = ""):
        exclCats = exclusiveCats(dim)

        assert "inc" not in dic.keys(), "This shouldn't happen!"

        if isinstance(dic[exclCats[0]], Yield):
            inclYield = Yield(0., 0.)
            for cat in exclCats:
                inclYield = inclYield + dic[cat]
            return inclYield

    def GetYield(self, **cats):
        
        for dflt in self._defaultArgs:
            assert cats[dflt], "%s val missing" % dflt

        if all(isinstance(cats[arg], str) for arg in self._defaultArgs):
            # asking for a specific value, as all args are strings
            return self._dict[cats["dphi"]][cats["nj"]][cats["nb"]][cats["ht"]]
        
        # get here if one or more arguments are lists (i.e. want multiple yields to be returned)
        listArgs = []
        out = {}
        for arg in self._defaultArgs:
            assert type(cats[arg]) in [str, list], "Argument for %s must be either str or list." % a
            if type(cats[arg]) is str:
                cats[arg] = [cats[arg]]

        for h, j, b, d in product(*[cats[arg] for arg in self._defaultArgs]): # messy!
            key = "%s_%s_%s_%s" % (h, j, b, d)
            out[key] = self._dict[d][j][b][h]

        return out

    def __str__(self):
        dict_printer(self._dict)
        return ""

######################################################################

def dict_sum(d1, d2):
    if d1 is None: return d2
    if d2 is None: return d1
    try:
        return d1 + d2
    except TypeError:
      # could assume they're both dicts, but lets be sure.  
      assert type(d1) is dict
      assert type(d2) is dict
      # assume d1 and d2 are dictionaries
      keys = set(d1.iterkeys()) | set(d2.iterkeys())
      return dict((key, dict_sum(d1.get(key), d2.get(key))) for key in keys)

######################################################################

def bins(key = ""):
    d = {   "nj":   ["le3j", "ge4j", "ge2j"],
            "nb":   ["eq0b", "eq1b", "eq2b", "eq3b", "ge0b"],
            "dphi": ["lt0p3", "gt0p3"],
            "ht":   ["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"]}
    
    if not key:
        return d
    try:
        return d[key]
    except:
        return None

######################################################################

def fpath():
    return "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/QCDKiller_GOLDEN/QCDFiles/25March_withBeamHalo_newCC_v0/"

######################################################################

if __name__ == "__main__":

    had_data = AnalysisYields(selec ="HadQCD",
                                bins = bins(),
                                fpath = fpath(),
                                zeroes = True)
    print had_data
    # had_mc  = AnalysisYields(selec ="HadQCD",
    #                             bins = bins(),
    #                             fpath = fpath(),
    #                             data = False)

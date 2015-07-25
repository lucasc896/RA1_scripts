import pytils
import ROOT as r
import math as ma
import plot_grabber as grabr
from sys import exit
from copy import deepcopy
from itertools import product

#---------------------------------------------------------------------#
"""
TO-DO
2. Add an additional alphaT dimension
3. Verify yields from grabr are correct!
4. Correct the erorr handling of the Yield addition/subtraction
5. Fix bin variables when overwriting an entire dict in object instance
6. New files will have two seperate histos to ><0.3, instead of dirs
"""
#---------------------------------------------------------------------#

class Yield(object):
    """container for a yield and it's error"""
    # 1. Need to update error handling options
    def __init__(self, val, err):
        self.v = float(val)
        self.e = float(err)
        self.fe = pytils.safe_divide(err, val)
    def __str__(self):
        return "Yield: %.3f +/- %.3f" % (self.v, self.e)
    def __add__(self, other):
        newv = self.v + other.v
        newe = ma.sqrt( ma.pow(self.e, 2) + ma.pow(other.e, 2) )
        return Yield(newv, newe)
    def __sub__(self, other):
        newv = self.v - other.v
        newe = ma.sqrt( ma.pow(self.e, 2) + ma.pow(other.e, 2) )
        return Yield(newv, newe)
    def __mul__(self, other):
        newv = self.v * other.v
        newe = newv * ma.sqrt( ma.pow(pytils.safe_divide(self.e, self.v), 2) + ma.pow(pytils.safe_divide(other.e, other.v), 2) )
        return Yield(newv, newe)
    def __div__(self, other):
        newv = pytils.safe_divide(self.v, other.v)
        newe = newv * ma.sqrt( ma.pow(pytils.safe_divide(self.e, self.v), 2) + ma.pow(pytils.safe_divide(other.e, other.v), 2) )
        return Yield(newv, newe)

#---------------------------------------------------------------------#

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

    def ReplaceYields(self, newDict = {}):
        # do some checking to make sure binning all agrees, otherwise get an unstable object
        self._dict = newDict

    def ValidateBins(self):
        for arg in self._defaultArgs:
            assert arg in self._bins.keys(), "Default bin argument %s missing." % arg
            assert self._bins[arg], "%s argument is empty" % arg

    def HarvestYields(self):
        if self._data:
            files = ["Had_Data"]
        else:
            files = ["Had_TTbar", "Had_SingleTop", "Had_WJets", "Had_DY", "Had_Zinv", "Had_DiBoson"]

        self._dict = dict.fromkeys(self._bins["dphi"])
        for dphi in self._bins["dphi"]:
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
                        # print htotal.GetEntries(), htotal.Integral()
                        self._dict[dphi][j][b][ht] = Yield(val, err)
                    # make inclusive ht cat
                    self._dict[dphi][j][b]['inc'] = self.MakeInclusiveHTYield(self._dict[dphi][j][b], "ht")
        # make inclusive dphi cat
        if len(self._bins["dphi"]) > 1:
            self._dict['inc'] = pytils.dict_add(self._dict['lt0p3'], self._dict['gt0p3'])
        else:
            self._dict['inc'] = deepcopy(self._dict[self._bins["dphi"][0]])



    def MakeInclusiveHTYield(self, dic = {}, dim = ""):

        assert "inc" not in dic.keys(), "This shouldn't happen!"

        if isinstance(dic[self._bins["ht"][0]], Yield):
            inclYield = Yield(0., 0.)
            for cat in self._bins["ht"]:
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

    def __add__(self, other):
        new = deepcopy(self)
        new.ReplaceYields( pytils.dict_add(self._dict, other._dict) )
        return new

    def __sub__(self, other):
        new = deepcopy(self)
        new.ReplaceYields( pytils.dict_sub(self._dict, other._dict) )
        return new

    def __mul__(self, other):
        new = deepcopy(self)
        new.ReplaceYields( pytils.dict_mul(self._dict, other._dict) )
        return new

    def __div__(self, other):
        new = deepcopy(self)
        new.ReplaceYields( pytils.dict_div(self._dict, other._dict) )
        return new

    def __str__(self):
        pytils.dict_printer(self._dict)
        return ""

#---------------------------------------------------------------------#

if __name__ == "__main__":

    testBins = {"nj": ["le3j", "ge4j"],
                "nb": ["eq0b", "eq1b"],
                "ht": ["200_275", "275_325", "325_375"],
                "dphi":["lt0p3", "gt0p3"]}

    had_data = AnalysisYields(selec ="HadQCD",
                                bins = testBins,
                                fpath = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/QCDKiller_GOLDEN/QCDFiles/25March_withBeamHalo_newCC_v0/",)
    print had_data
    # had_mc  = AnalysisYields(selec ="HadQCD",
    #                             bins = bins(),
    #                             fpath = fpath(),
    #                             data = False)

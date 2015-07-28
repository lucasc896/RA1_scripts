import pytils
import ROOT as r
import math as ma
import plot_grabber as grabr
from sys import exit
from copy import deepcopy
from itertools import product

r.gROOT.SetBatch(1)

#---------------------------------------------------------------------#
"""
TO-DO
1. 
2. 
3. Verify yields from grabr are correct!
4. Correct the erorr handling of the Yield addition/subtraction
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
    def __init__(self, selec = "", fpath = "", bins = {}, data = True, zeroes = False, legacy = False):
        print "> Creating AnalysisYields object for %s selection in %s" % (selec,
            "data" if data else "MC")

        self._defaultArgs = ["dphi", "nj", "nb", "ht", "at"]
        self._fpath = fpath
        self._selec = selec
        self._data = data
        self._zeroes = zeroes
        self._legacy = legacy
        self._bins = bins
        self.ValidateBins()
        self.HarvestYields()

    def ReplaceBinsFromDict(self, d = {}, iter = 0):
        self._bins[self._defaultArgs[iter]] = d.keys()
        # cheeky...
        firstVal = d[d.keys()[0]]
        if isinstance(firstVal, dict):
            iter += 1
            self.ReplaceBinsFromDict(firstVal, iter)

    def ReplaceYields(self, newDict = {}):
        # do some checking to make sure binning all agrees, otherwise get an unstable object
        self._dict = newDict
        self.ReplaceBinsFromDict(newDict)


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
                        self._dict[dphi][j][b][ht] = {} # create empty dict for alphaT
                        htotal = None
                        if self._legacy:
                            filepath = "%s/%s" % (self._fpath, dphi)
                            histname = "AlphaT_Signal"
                        else:
                            filepath = self._fpath
                            histname = "AlphaT_Signal" if dphi == "gt0p3" else "AlphaT_Sideband"
                        for fname in files:
                            hist = grabr.grab_plots(f_path = "%s/%s.root" % (filepath, fname),
                                                    sele = self._selec, h_title = histname, njet = j,
                                                    btag = b, quiet = True, ht_bins = ht)
                            if not htotal:
                                htotal = hist.Clone()
                            else:
                                htotal.Add(hist)

                        # now dice the total distribution into alphat bins
                        self._dict[dphi][j][b][ht]['inc'] = Yield(0., 0.)
                        for atlo, athi in zip(self._bins["at"], self._bins["at"][1:] + [None]):
                            atstr = "%"
                            atlobin = htotal.FindBin(float(atlo))
                            athibin = htotal.FindBin(float(athi)) if athi != None else htotal.GetNbinsX()+1 #inclusive final bin
                            # if atlobin == athibin: print atlo, atlobin, athi, athibin
                            err = r.Double(0.)
                            val = htotal.IntegralAndError(atlobin, athibin, err)
                            if self._zeroes:
                                val = 0.
                                err = 0.
                            self._dict[dphi][j][b][ht][atlo] = Yield(val, err)
                        err = r.Double(0.)
                        val = htotal.IntegralAndError(1, htotal.GetNbinsX()+1, err)
                        self._dict[dphi][j][b][ht]['inc'] = Yield(val, err)
                    
                    # make inclusive ht cat
                    self._dict[dphi][j][b]['inc'] = self.MakeInclusiveHTYield(self._dict[dphi][j][b])
        
        # make inclusive dphi cat
        if len(self._bins["dphi"]) > 1:
            self._dict['inc'] = pytils.dict_add(self._dict['lt0p3'], self._dict['gt0p3'])
        else:
            self._dict['inc'] = deepcopy(self._dict[self._bins["dphi"][0]])
        self._bins['dphi'].append("inc")



    def MakeInclusiveHTYield(self, dic = {}):

        assert "inc" not in dic.keys(), "This shouldn't happen!"
        
        new = dict.fromkeys(dic[self._bins['ht'][0]])
        for ht in self._bins["ht"]:
            new = pytils.dict_add(new, dic[ht])
        
        return new

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
        for p in product(*[cats[arg] for arg in self._defaultArgs]):
            key = "%s_%s_%s_%s_%s" % (p[0], p[1], p[2], p[3], p[4])
            out[key] = self._dict[p[0]][p[1]][p[2]][p[3]][p[4]]

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

def dict_sub_thresh(d1, d2, thresh = 0.):
    if d1 is None: return d2
    if d2 is None: return d1
    try:
        sub = d1 - d2
        # if the d2 is >X% of d1, do the subtraction
        # note: don't use safe divide, as these objects are Yields, not numbers
        if d2/d1 > thresh:
            return sub 
        else:
            # otherwise don't do the subtraction
            return d1
    except TypeError:
        # could assume they're both dicts, but lets be sure.  
        assert type(d1) is dict
        assert type(d2) is dict
        # assume d1 and d2 are dictionaries
        keys = set(d1.iterkeys()) | set(d2.iterkeys())
        return dict((key, dict_sub_thresh(d1.get(key), d2.get(key), thresh)) for key in keys)

#---------------------------------------------------------------------#

if __name__ == "__main__":

    testBins = {"nj": ["le3j", "ge4j"],
                "nb": ["eq0b", "eq1b"],
                "ht": ["200_275", "275_325", "325_375"],
                "dphi":["lt0p3", "gt0p3"],
                "at": ["0.00", "0.50", "10.00"]}

    # had_data_leg = AnalysisYields(selec ="HadQCD",
    #                             bins = testBins,
    #                             fpath = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/QCDKiller_GOLDEN/QCDFiles/25March_withBeamHalo_newCC_v0",
    #                             legacy = True)
    # print had_data_leg

    had_data = AnalysisYields(selec ="HadQCD",
                                bins = testBins,
                                fpath = "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/QCDKiller_GOLDEN/QCDFiles/25Jul_fullParked_noDPhi_MHTMETCut_v0",)

    print had_data.GetYield(nj = "le3j", nb = "eq0b", ht = "200_275", dphi = "lt0p3", at = testBins['at']+['inc'])

    # had_mc  = AnalysisYields(selec ="HadQCD",
    #                             bins = bins(),
    #                             fpath = fpath(),
    #                             data = False)

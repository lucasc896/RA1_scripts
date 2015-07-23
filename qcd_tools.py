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
1. Setup automatic inclusive maker with 'inc' keyword
2. Add an additional alphaT dimension
3. Verify yield from grabr are correct!
4. Correct the erorr handling of the Yield addition/subtraction
5. Add other inclusive categories - should recursively use inclusive maker
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

# class CatYield(object):
#     """object to hold a bunch of yields, recursively"""
#     def __init__(self, cats = []):
#         self._cats = cats if cats else []


#     def AddCat(self, cat = "", val = None):
#         # print cat, val, self._cats
#         if cat in self._cats:
#             print "%s already exists." % cat
#         setattr(self, cat, val)
#         self._cats.append(cat)

#     def __str__(self):
#         out = "\n-CatYield object-\n"
#         out += "Cats: " + ", ".join(self._cats) + "\n"
        
#         for cat in self._cats:
#             try:
#                 out += "%s: %s\n" % (cat, getattr(self, cat))
#             except AttributeError:
#                 pass
#         return out

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
    def __init__(self, selec = "", data = True):
        print "> Creating AnalysisYields object for %s selection in %s" % (selec,
            "data" if data else "MC")
        self._selec = selec
        self._data = data
        self.HarvestYields()

    def HarvestYields(self):
        if self._data:
            files = ["Had_Data"]
        else:
            files = ["Had_TTbar", "Had_SingleTop", "Had_WJets", "Had_DY", "Had_Zinv", "Had_DiBoson"]

        self._dict = dict.fromkeys(["lt0p3", "gt0p3"])
        for dphi in ["lt0p3", "gt0p3"]:
            self._dict[dphi] = dict.fromkeys(bins("nj"))
            for j in bins("nj"):
                self._dict[dphi][j] = dict.fromkeys(bins("nb"))
                for b in bins("nb"):
                    self._dict[dphi][j][b] = dict.fromkeys(bins("ht"))
                    for ht in bins("ht"):
                        htotal = None
                        for fname in files:
                            hist = grabr.grab_plots(f_path = "%s/%s/%s.root" % (fpath(), dphi, fname),
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
                    self._dict[dphi][j][b]['inc'] = self.MakeInclusiveYield(self._dict[dphi][j][b], "ht")
                # make inclusive nb cat
                self._dict[dphi][j]['inc'] = self.MakeInclusiveYield(self._dict[dphi][j], "nb")
            # make inclusive nj cat
            self._dict[dphi]['inc'] = self.MakeInclusiveYield(self._dict[dphi], "nj")
        # make inclusive dphi cat
        pass


    def MakeInclusiveYield(self, dic = {}, dim = ""):
        exclCats = exclusiveCats(dim)

        assert "inc" not in dic.keys(), "This shouldn't happen!"

        # check that we're at the individual Yield level
        if type(dic[exclCats[0]]) is Yield:
            inclYield = Yield(0., 0.)
            for cat in exclCats:
                inclYield = inclYield + dic[cat]
            return inclYield
        elif type(dic[exclCats[0]]) is dict:
            # dict_printer(dic)
            return self.dictSummer(dic)

    def dictSummer(self, dic = {}):
        """this is the wrong way to do it...change!"""
        keys = dic.keys()

        if type(dic[keys[0]]) is dict:
            subKeys = dic[keys[0]].keys()
            # print type(dic[keys[0]][subKeys[0]])
            if type(dic[keys[0]][subKeys[0]]) is Yield:
                inclDict = dict.fromkeys(subKeys)
                for skey in subKeys:
                    inclDict[skey] = Yield(0., 0.)
                    for key in keys:
                        inclDict[skey] = inclDict[skey] + dic[key][skey]
                return inclDict
            elif type(dic[keys[0]][subKeys[0]]) is dict:
                for key in keys:
                    summed = self.dictSummer(dic[key])
                    print key, summed


    def GetYield(self, **cats):
        
        defaultArgs = ["ht", "nj", "nb", "dphi"]
        
        for dflt in defaultArgs:
            assert cats[dflt], "%s val missing" % dflt

        if all(type(cats[arg]) is str for arg in defaultArgs):
            # asking for a specific value, as all args are strings
            return self._dict[cats["dphi"]][cats["nj"]][cats["nb"]][cats["ht"]]
        
        # get here if one or more arguements are lists (i.e. want multiple yields to be returned)
        listArgs = []
        out = {}
        for arg in defaultArgs:
            assert type(cats[arg]) in [str, list], "Arguement for %s must be either str or list." % a
            if type(cats[arg]) is str:
                cats[arg] = [cats[arg]]

        for h, j, b, d in product(*[cats[arg] for arg in defaultArgs]): # messy!
            key = "%s_%s_%s_%s" % (h, j, b, d)
            out[key] = self._dict[d][j][b][h]

        return out

    def __str__(self):
        dict_printer(self._dict)
        return ""

######################################################################

def bins(key = ""):
    try:
        return {"nj": ["le3j", "ge4j"],
                "nb": ["eq0b", "eq1b", "eq2b", "eq3b"][:2],
                "ht": ["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"][:1]}[key]
    except:
        return None

######################################################################

def fpath():
    return "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/QCDKiller_GOLDEN/QCDFiles/25March_withBeamHalo_newCC_v0/"

######################################################################

if __name__ == "__main__":

    had_data = AnalysisYields("HadQCD")
    print had_data
    # had_mc = AnalysisYields("HadQCD", data = False)
    # print had_mc
    d = {
    "ht": bins("ht")[0:2],
    "nj": bins("nj"),
    "nb": "eq0b",
    "dphi": "lt0p3",
    }

    # y = had_data.GetYield(**d)
    # for k in y:
    #     print k, y[k]



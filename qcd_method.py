#!/usr/bin/env python
import pytils
from qcd_tools import AnalysisYields as AnaY
from qcd_tools import Yield
from copy import deepcopy

#---------------------------------------------------------------------#
"""
TO-DO
2. Work out way to present results
    - table
    - plot
3. validate threshold subtraction validity
"""
#---------------------------------------------------------------------#

def bins(key = ""):
    d = {   "nj":   ["le3j", "ge4j", "ge2j"][:1],
            "nb":   ["eq0b", "eq1b", "eq2b", "eq3b", "ge0b"][:1],
            "dphi": ["lt0p3", "gt0p3"],
            "ht":   ["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"][:3]}
    
    if not key:
        return d
    try:
        return d[key]
    except:
        return None

#---------------------------------------------------------------------#

def fpath():
    return "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/QCDKiller_GOLDEN/QCDFiles/25March_withBeamHalo_newCC_v0/"

#---------------------------------------------------------------------#

def getAllSelections():
    """create all objects for each of the four ana selections"""
    had_data    = AnaY(selec = "HadQCD",
                        bins = bins(),
                        fpath = fpath())
    had_mc      = AnaY(selec = "HadQCD",
                        bins = bins(),
                        fpath = fpath(),
                        data = False)
    mu_data     = AnaY(selec = "OneMuonQCD",
                        bins = bins(),
                        fpath = fpath())
    mu_mc       = AnaY(selec = "OneMuonQCD",
                        bins = bins(),
                        fpath = fpath(),
                        data = False)
    return had_data, had_mc, mu_data, mu_mc

#---------------------------------------------------------------------#

def makePrediction(hmc = None, md = None, mmc = None):
    """make the ewk prediction for inclusive and split control sample"""

    # make empty object to fill with preds for non split control region
    had_ewk_pred = AnaY(selec = "HadQCD",
                        bins = bins(),
                        fpath = fpath(),
                        zeroes = True)
    # for each dphi region (and 'inc'), calc pred with dphi-inclusive mu
    for dphi in bins("dphi")+["inc"]:
        tmp = pytils.dict_mul(md._dict['inc'], hmc._dict[dphi])
        tmp = pytils.dict_div(tmp, mmc._dict['inc'])
        had_ewk_pred._dict[dphi] = pytils.dict_add(had_ewk_pred._dict[dphi], tmp)

    # now create version with fully split backgrounds
    had_ewk_pred_splitMu = md * hmc
    had_ewk_pred_splitMu = had_ewk_pred_splitMu / mmc

    return had_ewk_pred, had_ewk_pred_splitMu

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

def ewkSubtraction(hd = None, hpred = None, thresh = 0.):
    newObj = deepcopy(hd)
    newDict = dict_sub_thresh(hd._dict, hpred._dict, thresh)
    print newObj._bins
    newObj._dict['edballs'] = 1.
    newObj.ReplaceYields(newDict)
    print newObj._bins
    return newObj

#---------------------------------------------------------------------#

def main():

    had_data, had_mc, mu_data, mu_mc = getAllSelections()

    had_ewk_pred, had_ewk_pred_splitMu = makePrediction(had_mc, mu_data, mu_mc)

    # print had_data-had_ewk_pred
    print ewkSubtraction(had_data, had_ewk_pred)



if __name__ == "__main__":
    main()
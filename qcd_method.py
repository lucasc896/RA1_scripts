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
"""
#---------------------------------------------------------------------#

def bins(key = ""):
    d = {   "nj":   ["le3j", "ge4j", "ge2j"][:1],
            "nb":   ["eq0b", "eq1b", "eq2b", "eq3b", "ge0b"][:1],
            "dphi": ["lt0p3", "gt0p3"],
            "ht":   ["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"][:1]}
    
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

def main():

    had_data, had_mc, mu_data, mu_mc = getAllSelections()

    had_ewk_pred, had_ewk_pred_splitMu = makePrediction(had_mc, mu_data, mu_mc)

    print had_ewk_pred-had_ewk_pred_splitMu



if __name__ == "__main__":
    main()
#!/usr/bin/env python
import pytils
from qcd_tools import AnalysisYields as AnaY
from qcd_tools import Yield
from copy import deepcopy

#---------------------------------------------------------------------#
"""
TO-DO
1. Decide on way to split the mu bkg pred
2. Work out way to present results
    - table
    - plot
"""
#---------------------------------------------------------------------#

def bins(key = ""):
    d = {   "nj":   ["le3j", "ge4j", "ge2j"],
            "nb":   ["eq0b", "eq1b", "eq2b", "eq3b", "ge0b"][:2],
            "dphi": ["lt0p3", "gt0p3"],
            "ht":   ["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"][:5]}
    
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
    had_ewk_pred = had_mc / mu_mc
    had_ewk_pred = had_ewk_pred * mu_data
    had_qcd_est  = had_data - had_ewk_pred
    return had_data, had_mc, mu_data, mu_mc, had_ewk_pred, had_qcd_est

#---------------------------------------------------------------------#

def main():

    had_data, had_mc, mu_data, mu_mc, had_ewk_pred, had_qcd_est = getAllSelections()

    print had_qcd_est





if __name__ == "__main__":
    main()
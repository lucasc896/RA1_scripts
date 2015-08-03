#!/usr/bin/env python
import pytils
import ROOT as r
import qcd_output as qout
from qcd_tools import AnalysisYields as AnaY
from qcd_tools import Yield, dict_sub_thresh
from copy import deepcopy

r.gROOT.SetBatch(1)

#---------------------------------------------------------------------#
"""
TO-DO
2. Work out way to present results
    - table
3. validate threshold subtraction validity
"""
#---------------------------------------------------------------------#

def bins(key = ""):
    """define the binning to be used"""
    d = {   "nj":   ["le3j", "ge4j", "ge2j"],
            # "nb":   ["eq0b", "eq1b", "eq2b", "eq3b", "ge0b"],
            "nb":   ["eq0b", "eq1b", "eq2b", "ge0b"],
            "dphi": ["lt0p3", "gt0p3"],
            "ht":   ["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"],
            # "at":   [i*0.025 for i in range(40)]}# + [0.5+0.01*i for i in range(20)] + [0.7 + 0.1*i for i in range(4)]}
            # "at":   [0.5 + i*0.001 for i in range(100)],
            # "at":   [0.5 + i*0.002 for i in range(15)] + [0.53+i*0.005 for i in range(14)],
            "at":   [0.5 + i*0.005 for i in range(100)],
            }
    
    # convert alphaT float values into strings
    d['at'] = ["%.3f" % at for at in d['at']]

    # d['at'] = ["0.00", "100.0"]

    if not key:
        return d
    try:
        return d[key]
    except:
        return None

#---------------------------------------------------------------------#

def fpath():
    return "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/QCDKiller_GOLDEN/QCDFiles/28Jul_fullParked_noDPhi_withMHTMETCut_v0/"
    # return "/Users/chrislucas/SUSY/AnalysisCode/rootfiles/QCDKiller_GOLDEN/QCDFiles/29Jul_fullParked_noDPhi_MHTMETCutRemoved_v0/"

#---------------------------------------------------------------------#

def getAllSelections():
    """create all objects for each of the four ana selections"""
    leg = [False, True][0]
    had_data    = AnaY(legacy = leg,
                        selec = "HadQCD",
                        bins = bins(),
                        fpath = fpath())
    had_mc      = AnaY(legacy = leg,
                        selec = "HadQCD",
                        bins = bins(),
                        fpath = fpath(),
                        data = False)
    mu_data     = AnaY(legacy = leg,
                        selec = "OneMuonQCD",
                        bins = bins(),
                        fpath = fpath())
    mu_mc       = AnaY(legacy = leg,
                        selec = "OneMuonQCD",
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

def ewkSubtraction(hd = None, hpred = None, thresh = 0.):
    """dedicated function for Data - EWKPred"""
    newObj = deepcopy(hd)
    newDict = dict_sub_thresh(hd._dict, hpred._dict, thresh)
    newObj.ReplaceYields(newDict)
    return newObj

#---------------------------------------------------------------------#

def main():

    had_data, had_mc, mu_data, mu_mc = getAllSelections()

    had_ewk_pred, had_ewk_pred_splitMu = makePrediction(had_mc, mu_data, mu_mc)

    had_qcd_pred = ewkSubtraction(had_data, had_ewk_pred)
    had_qcd_pred_splitMu = ewkSubtraction(had_data, had_ewk_pred_splitMu)

    qout.GenericPlotter(had_data, "had_data")
    qout.GenericPlotter(had_mc, "had_mc")
    qout.GenericPlotter(mu_data, "mu_data")
    qout.GenericPlotter(mu_mc, "mu_mc")
    qout.GenericPlotter(had_qcd_pred, "had_qcd_pred")
    qout.GenericPlotter(had_qcd_pred_splitMu, "had_qcd_pred_splitMu")
    qout.GenericPlotter(had_ewk_pred_splitMu, "had_ewk_pred_splitMu")

    # qout.printTable(had_data._dict['lt0p3']['ge2j']['ge0b']['inc'])

if __name__ == "__main__":
    main()

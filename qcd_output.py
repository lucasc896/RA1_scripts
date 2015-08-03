import pytils
import os
import ROOT as r
import numpy as np
import math as ma
from itertools import product

r.gROOT.SetBatch(1)
r.gStyle.SetOptStat(0)
if int(r.gROOT.GetVersion()[0])>5:
    r.gStyle.SetPalette(r.kBird) #set to kBird palette colour (only works for ROOT6)
else:
    r.gStyle.SetPalette(51)

#---------------------------------------------------------------------#
"""
TO-DO
1. Add plot details (title, axes label etc)
"""
#---------------------------------------------------------------------#

def alphatGraph(d = {}):
    gr = r.TGraphErrors(len(d))
    for n, at in enumerate(d):
        if at == 'inc': continue
        # skip points with nan vals or errs
        if np.nan in [d[at].v, d[at].e]: continue
        gr.SetPoint(n, float(at), d[at].v)
        gr.SetPointError(n, 0., d[at].e)
    gr.SetMarkerStyle(20)
    gr.SetMarkerSize(1)
    gr.SetLineWidth(2)
    return gr

#---------------------------------------------------------------------#

def alphatHist(d = {}):

    avals = d.keys()
    nvals = len(avals) if 'inc' not in avals else len(avals)-1
    h = r.TH1D("at", "at", nvals, 0., 1.)
    for at in avals:
        if at == 'inc': continue
        if np.nan in [d[at].v, d[at].e]: continue
        abin = h.FindBin(float(at))
        h.SetBinContent(abin, d[at].v)
        h.SetBinError(abin, d[at].e)
    return h

#---------------------------------------------------------------------#

def mkDir(path = ""):
    if not os.path.exists(path):
        os.makedirs(path)

#---------------------------------------------------------------------#

def pdeets(title = "", xtitle = "", ytitle = "", xrange = [], xrebin = None):
    return {"title": title,
            "xtitle": xtitle,
            "ytitle": ytitle,
            "xrange": xrange,
            "xrebin": xrebin}

#---------------------------------------------------------------------#

def plotDetails(plot = ""):
    return # COMPLETE ME!
    return {"dphiComparison": pdeets(),
            }

#---------------------------------------------------------------------#

def binSorter(unsorted = [], dim = ""):
    protoBins = {   "nj":   ["le3j", "ge4j", "ge2j"],
                    "nb":   ["eq0b", "eq1b", "eq2b", "eq3b", "ge0b"],
                    "dphi": ["lt0p3", "gt0p3"],
                    "ht":   ["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"],
                }
    out = []
    for bin in protoBins[dim]:
        if bin in unsorted:
            out.append(bin)

    return out

#---------------------------------------------------------------------#

class GenericPlotter(object):
    """generic plotter class which plots all analysis cats available"""
    def __init__(self, yields, label = "", allHT = False):
        self._yields = yields._dict
        self._outpath = os.path.join(os.getcwd(), "out", label)
        mkDir(self._outpath)
        self._cpd = self._outpath # 'current plotting directory'
        self._allHT = False # optional flag to only plot inclusive HT
        self._logy = False
        self.getBins()
        self.runPlotter()

    def getBins(self):
        """get the bins from _yields object"""
        # nice and ugly

        dphi = binSorter(self._yields.keys(), 'dphi')
        nj = binSorter(self._yields[dphi[0]].keys(), 'nj')
        nb = binSorter(self._yields[dphi[0]][nj[0]].keys(), 'nb')
        htfull = binSorter(self._yields[dphi[0]][nj[0]][nb[0]].keys(), 'ht')
        at = self._yields[dphi[0]][nj[0]][nb[0]][htfull[0]].keys()
        ht = htfull if self._allHT else ['inc'] 

        # sort the arrays!

        self._bins = {'dphi': dphi, 'nj': nj, 'nb': nb, 'ht': ht, 'htfull': htfull, 'at':at}

    def binString(self, *args):
        return "_".join(args)

    def runPlotter(self):
        # can pick and choose which generic plots to make here
        
        self.makeDPhiComparison()
        # self.makeDPhiComparison(plotRatio = True)
        # self.makeAlphaTDistro(mode = "diff")
        # self.makeAlphaTDistro(mode = "cumu")
        self.alphaTThresholdFrenchFlag()

    def makeAlphaTDistro(self, mode = "diff"):

        # for nj in self._bins['nj']:
        #     for nb in self._bins['nb']:
        #         for ht in self._bins['ht']:
        pass

    def makeDPhiComparison(self, plotRatio = False):

        self._cpd = self._outpath + "/" + "dphiComparison"
        mkDir(self._cpd)
        try:
            lt = self._yields['lt0p3']
            gt = self._yields['gt0p3']
        except KeyError:
            # can only make comparison if both dicts are present
            return

        self._logy = True

        # megacanv = r.TCanvas("mega", "mega", 1600, 1200)
        # megacanv.Divide(4, 3, 0.01, 0.01)
        # should set all the pads here too
        # index = 1
        for nj in self._bins['nj']:
            for nb in self._bins['nb']:
                # megacanv.cd(index)
                # if index > 3: continue
                for ht in self._bins['ht']:
                    grlt = alphatGraph(lt[nj][nb][ht])
                    grlt.SetName("#Delta#phi_{min}* < 0.3")
                    grgt = alphatGraph(gt[nj][nb][ht])
                    grgt.SetName("#Delta#phi_{min}* > 0.3")
                    if plotRatio:
                        grrt = alphatGraph(pytils.dict_div(gt[nj][nb][ht], lt[nj][nb][ht]))
                        self._logy = False
                        self.singleGraph(grrt, self.binString(nj, nb, ht)+"_ratio")
                    else:
                        self.comparisonGraph(grlt, grgt, self.binString(nj, nb, ht))
                        # lg = r.TLegend(0.74, 0.80, 0.89, 0.89)

                        # grlt.Draw("AP")
                        # grlt.SetLineColor(r.kRed)
                        # grlt.SetMarkerColor(r.kRed)
                        # grlt.SetTitle(self.binString(nj, nb, ht))
                        # grlt.SetMinimum(0.001)
                        # grlt.SetMaximum(100000)
                        # grlt.GetXaxis().SetRangeUser(0.5, 0.6)
                        # lg.AddEntry(grlt, grlt.GetName(), "L")

                        # grgt.Draw("PSAME")
                        # grgt.SetLineColor(r.kBlue)
                        # grgt.SetMarkerColor(r.kBlue)
                        # lg.AddEntry(grgt, grgt.GetName(), "L")

                        # r.gPad.SetLogy(self._logy)

                        # lg.SetLineColor(0)
                        # lg.SetFillColor(0)
                        # lg.Draw()
                    
                # index += 1
        # megacanv.cd()
        # megacanv.Print(self._cpd + "/" + "all.pdf")

        self._logy = False # flick switch back to off

    def makeEmptyFrenchHist(self):
        
        nht = len(self._bins['htfull'])
        ncat = len(self._bins['nj']) * len(self._bins['nb'])
        hist = r.TH2D("french", "french",
                nht, 0., nht,
                ncat, 0., ncat,
                )
        for n, ht in enumerate(self._bins['htfull']):
            hist.GetXaxis().SetBinLabel(n+1, ht)
        for n, cat in enumerate(product(self._bins['nb'], self._bins['nj'])):
            hist.GetYaxis().SetBinLabel(n+1, ", ".join(cat))
        hist.SetContour(100)
        return hist

    def alphaTThresholdFrenchFlag(self):

        self._cpd = self._outpath + "/" + "frenchDPhiRatio"
        mkDir(self._cpd)
        try:
            lt = self._yields['lt0p3']
            gt = self._yields['gt0p3']
        except KeyError:
            # can only make comparison if both dicts are present
            return

        french = self.makeEmptyFrenchHist()
        french.GetZaxis().SetTitle("N(#Delta#phi_{min}* < 0.3)/N(#Delta#phi_{min}* > 0.3)")
        french.SetTitle("#Delta#phi_{min}* ratio over #alpha_{T} threshold")

        canv = r.TCanvas()
        canv.SetRightMargin(0.13)
        canv.SetBottomMargin(0.05)

        for ncat, cat in enumerate(product(self._bins['nb'], self._bins['nj'])):
            nb = cat[0]
            nj = cat[1]
            if 'inc' in [nb, nj]: continue
            # print ncat, cat,
            for nht, ht in enumerate(self._bins['htfull']):
                # print nht, ht, 
                if ht in ['200_275', '275_325']:
                    thresh = 0.65
                elif ht in ['325_375']:
                    thresh = 0.6
                else:
                    thresh = 0.55
                histlt = alphatHist(lt[nj][nb][ht])
                histgt = alphatHist(gt[nj][nb][ht])

                # find the point corresponding to the alphaT threshold
                atbin = histlt.FindBin(thresh)
                # print thresh, atbin

                vallt = histlt.Integral(atbin, histlt.GetNbinsX()+1)
                valgt = histgt.Integral(atbin, histgt.GetNbinsX()+1)
                ratio = pytils.safe_divide(vallt, valgt)
                print vallt, valgt, ratio, "(%s, %s, %s)" % (nb, nj, ht)
                french.SetBinContent(nht+1, ncat+1, ratio)

        french.Draw("colztext")
        canv.Print(os.path.join(self._cpd, "dPhiRatioFF.pdf"))



    def comparisonGraph(self, gr1 = None, gr2 = None, label = ""):
        canv = r.TCanvas()

        lg = r.TLegend(0.74, 0.80, 0.89, 0.89)

        gr1.Draw("AP")
        gr1.SetLineColor(r.kRed)
        gr1.SetMarkerColor(r.kRed)
        gr1.SetTitle(label)
        gr1.SetMinimum(0.001)
        gr1.SetMaximum(100000)
        gr1.GetXaxis().SetRangeUser(0.5, 1.)

        gr2.Draw("PSAME")
        gr2.SetLineColor(r.kBlue)
        gr2.SetMarkerColor(r.kBlue)

        canv.SetLogy(self._logy)

        for ent in [gr1, gr2]:
            lg.AddEntry(ent, ent.GetName(), "L")
        lg.SetLineColor(0)
        lg.SetFillColor(0)
        lg.Draw()

        canv.Print(self._cpd+"/"+label+".pdf")

        return canv

    def singleGraph(self, gr, label):
        canv = r.TCanvas()
        gr.Draw("AP")
        gr.SetLineColor(r.kGreen+1)
        gr.SetMarkerColor(r.kGreen+1)

        gr.SetTitle(label)

        gr.SetMinimum(0.)

        canv.SetLogy(self._logy)

        canv.Print(self._cpd+"/"+label+".pdf")

#---------------------------------------------------------------------#

def printTable(d = {}):
    # vertical printing
    for key in sorted(d.keys()):
        if key == 'inc': continue
        print repr(round(float(key),3)).ljust(10),
        print repr(d[key].v).rjust(8), repr(round(d[key].e, 3)).rjust(8)


#---------------------------------------------------------------------#

if __name__ == "__main__":
    GenericPlotter({}, 'label1')

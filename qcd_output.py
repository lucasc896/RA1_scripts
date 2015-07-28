import pytils
import os
import ROOT as r
import numpy as np
from itertools import product

r.gROOT.SetBatch(1)

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

        dphi = self._yields.keys()
        nj = self._yields[dphi[0]].keys()
        nb = self._yields[dphi[0]][nj[0]].keys()
        ht = self._yields[dphi[0]][nj[0]][nb[0]].keys() if self._allHT else ["inc"]
        at = self._yields[dphi[0]][nj[0]][nb[0]][ht[0]].keys()

        self._bins = {'dphi': dphi, 'nj': nj, 'nb': nb, 'ht': ht, 'at':at}

    def binString(self, *args):
        return "_".join(args)

    def runPlotter(self):
        # can pick and choose which generic plots to make here
        
        self.makeDPhiComparison()
        # self.makeDPhiComparison(plotRatio = True)
        # self.makeAlphaTDistro(mode = "diff")
        # self.makeAlphaTDistro(mode = "cumu")

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

    def comparisonGraph(self, gr1 = None, gr2 = None, label = ""):
        canv = r.TCanvas()

        lg = r.TLegend(0.74, 0.80, 0.89, 0.89)

        gr1.Draw("AP")
        gr1.SetLineColor(r.kRed)
        gr1.SetMarkerColor(r.kRed)
        gr1.SetTitle(label)
        gr1.SetMinimum(0.001)
        gr1.SetMaximum(100000)
        gr1.GetXaxis().SetRangeUser(0.5, 0.6)

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

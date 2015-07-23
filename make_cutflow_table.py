from sys import exit, argv
import json as js

class cut(object):
    """container for class info"""
    def __init__(self, name = "", n = -1, eff = -1):
        self.name = name
        self.n = n
        self.eff = eff
    def __str__(self):
        out = ""
        out += "------ Cut ------\n"
        out += " Name: '%s'\n" % self.name
        out += " Passed: %.2f\n" %self.n
        out += " Cut Eff: %.2f\n" % self.eff
        return out

def check_cuts(cuts = []):
    last = 100000000000000000000
    for c in cuts:
        if last < c.n:
            print "Yield higher than previous."
            print last, c.n
            return False
        if c.eff > 1:
            print "Eff > 1"
            print c.eff
            return False
        last = c.n
    return True

def process_keys(inlist = []):
    for key in inlist:
        if key not in ['T', 'eT', 'F', 'eF', 'efficiency']:
            return key

def clean_cut_name(name = ""):
    clean = {
        "CountOp (count_total) ": "Event Counter",
        "HT 375 GeV ": "\\HT > 375 \\gev",
        "MultiTrigger:   HLT_HT350_AlphaT0p52_v*": "Trigger",
        "Dummy filter set to 'pass'": "Dummy filters",
        "JSON Filter: ": "Good Event JSON Filter",
        "JSON Output: ": "Dummy JSON output",
        "NumComJets Operation (num unsigned int >= 2)": "$\\nj \geq 2$",
        "Check if an event failed noise filtering criteria": "HBHE Noise Filter",
        "Check if an event failed 2012 8TeV MET Filters": "MET Filters",
        "Check if an event failed Good event selection": "Vertex Noise Filter",
        "Maximum EMF of all jets <  0.1 ": "$\\text{EMF}_{max}$ for all jets > 0.1",
        " first Jet Eta < 2.5 rad): ": "Leading jet $\\eta$ < 2.5",
        "First jet Pt > 100 GeV: ": "Leading jet \\Pt > 100 \gev",
        "Second jet Pt > 100 GeV: ": "Sub-Leading jet \\Pt > 100 \gev",
        "Check if a jet failed loose quality criteria": "$n_{j, fail} = 0$",
        "Bad muon in a Jet": "$\\Delta R(\\mu^i_{fail}, jet^j) < 0.5$",
        "Check if a electron failed loose quality criteria": "$n_{e, fail} = 0$",
        "Check if a photon failed loose quality criteria": "$n_{\\gamma, fail} = 0$",
        "NumComElectrons Operation (num unsigned int <= 0)": "$n_{e} = 0$",
        "Number of Common Photons unsigned int <= 0)": "$n_{\\gamma} = 0$",
        "NumComMuons Operation (num unsigned int <= 0)": "$n_{\\mu} = 0$",
        "CommonMinBiasDPhi >  0.3 ": "\\mindphistar > 0.3",
        "Checking that  sum Vertex Pt / HT is  > 0.1 ": "$(\\sum_{}^{n_{vertices}}{\\Pt}$) / \\HT",
        "Veto Events with sum of cleaned rechits above 30 GeV ": "recHitCut",
        "IsoTrackVeto: ": "$n_{SIT} = 0$",
        "Dead ECAL cut 0.3 ": "DeadECAL Filter",
        "Alpha_t  > 0.55 GeV): ": "\\alphat > 0.55",
        "Passing MHT over MET cut of: 1.25 ": "\\mhtmet < 1.25",
    }

    try:
        return clean[name]
    except KeyError:
        return name + " (Raw)"

def make_latex_table(cuts = []):

    out = "\\begin{table}[ht!]\n  \\caption{A cutflow table.}\n  \\label{tab:a_cutflow_table}\n  \\centering\n  \\footnotesize\n  \\begin{tabular}{ lcc }\n    \\hline\n    \\hline\n    Cut Name    & Eff (\\%) & N \\\\\n    \\hline\n"

    out = out.replace("table.", "table for logfile \\verb!%s!." % argv[1].split("/")[-1])

    for n, cut in enumerate(cuts):
        out += "\t%s\t& %.2f  & %.2f \\\\\n" % (clean_cut_name(cut.name), cut.eff*100., cut.n)
        # print cut.name
    out += "    \\hline\n    \\hline\n  \\end{tabular}\n\\end{table}"
    print out

def main():
    # indir = "in/LogFiles"
    # infile = "AK5Calo_Had_Prompt_100_100_50_WJetsToLNu_HT_400ToInf_8TeV_madgraph_v2_Summer12_DR53X_PU_S10_START53_V7A_v1_V18_1_taus_0_zmengJob40_EOS_1059.log"

    if len(argv) < 2:
        print ">> Suppy more options:"
        print "   python make_cutflow_table.py <in-json-file>"
        exit()

    with open(argv[1]) as in_json:
        in_data = js.load(in_json)
        cut_flow = in_data['Cut Flow']
        this_cut = cut_flow.keys()[1]
        cuts_list = []
        last  = False
        this_eff = None
        while True:
            if len(cut_flow) > 6:
                last = True
                break
            else:
                cut_flow = cut_flow[this_cut]

            if not last:
                next_cut = process_keys(cut_flow.keys())
                if not next_cut: break
                this_yield = cut_flow['T']
                if this_eff:
                    this_eff = float(this_yield)/float(last_yield)
                else:
                    this_eff = 1.
                cut_obj = cut(this_cut, this_yield, this_eff)
                cuts_list.append( cut_obj )
                last_yield = this_yield
                this_cut = next_cut
                if last:
                    break
        
        # check cuts have descending yields and effs<1.
        if not check_cuts(cuts_list):
            exit("Problem with cuts_list. Exiting.")

        make_latex_table(cuts_list)

if __name__ == "__main__":
    main()
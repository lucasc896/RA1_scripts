from sys import exit
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
            return False
        if c.eff > 1:
            return False
        last = c.n
    return True

def process_keys(inlist = []):
    for key in inlist:
        if key not in ['T', 'eT', 'F', 'eF', 'efficiency']:
            return key

def main():
    indir = "in/LogFiles"
    infile = "AK5Calo_Had_Prompt_100_100_50_WJetsToLNu_HT_400ToInf_8TeV_madgraph_v2_Summer12_DR53X_PU_S10_START53_V7A_v1_V18_1_taus_0_zmengJob40_EOS_1059.log"

    with open("/".join([indir, infile])) as in_json:
        in_data = js.load(in_json)
        cut_flow = in_data['Cut Flow']
        this_cut = cut_flow.keys()[1]
        cuts_list = []
        last  = False
        while True:
            if len(cut_flow) > 6:
                last = True
                break
            else:
                cut_flow = cut_flow[this_cut]

            if not last:
                next_cut = process_keys(cut_flow.keys())
                cut_obj = cut(this_cut, cut_flow['T'], cut_flow['efficiency'])
                cuts_list.append( cut_obj )
                this_cut = next_cut
                if last:
                    break
        
        # check cuts have descending yields and effs<1.
        if not check_cuts(cuts_list):
            exit("Problem with cuts_list. Exiting.")

        # process

if __name__ == "__main__":
    main()
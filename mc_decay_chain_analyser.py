#!/usr/bin/env python
import sys
from pdgIdStore import pdgIdDict

def pdgIdLookup(pdgid = ""):

    anti = True if pdgid[0] == "-" else False

    try:
        if anti:
            return "%s%s" %("-", pdgIdDict[pdgid[1:]])
        else:
            return pdgIdDict[pdgid]
    except KeyError:
        return pdgid

def parseFile(file = None):

    chains = []
    tmp = []
    for line in file:
        if "New Event" in line:
            if tmp:
                chains.append(tmp)
                tmp = []
            else:
                tmp = []
        else:
            tmp.append( parseLine(line) )
    chains.append(tmp)

    return chains

def parseLine(line = ""):

    return_line = []
    info_line = False
    line = line.strip() #remove crap at either end
    
    if len(line) == 0:
        return []

    if line[0] in ["*", ">"]:
        info_line = True
        line = line.split(" ")
    else:
        line = line.split("\t") #split by tabs
    
    for n, ent in enumerate(line): #loop, cutting off the final status number
        if ent: # if it has a value
            if info_line:
                return_line.append(ent)
                continue

            if n == len(line)-1:
                continue

            if n>0:
                # if a particle, then convert to particle string name
                return_line.append( pdgIdLookup(ent) )
            else:
                # keep index as a number
                return_line.append(ent)
    
    return return_line

def printChains(chains = []):

    outTxt = ""

    for n, chain in enumerate(chains):
        outTxt += "\n\n>>> Event %d\n" % (n+1)

        for ent in chain:
            if not ent: continue
            if len(ent) == 3 and ent[0][0] not in ["*", ">"]: # is a decay line
                # suff = "*" if "Nu" in ent[1] else ""
                outTxt += "\n%s:\t%-12s -> %-s" % (ent[0], ent[2], ent[1])
            elif ent[0][0] == ">":
                outTxt += "\t" + " ".join(ent)
            else:
                outTxt += " " + " ".join(ent) + "\n"
    print outTxt

def main():

    if len(sys.argv) < 2:
        exit(">>> Error: pass a decay chain file.")

    try:
        infile = open(sys.argv[1])
    except IOError:
        exit(">>> FileError: File doesn't exist.")

    chains_list = parseFile(infile)
    infile.close()

    printChains(chains_list)

    pass

if __name__ == "__main__":
    main()
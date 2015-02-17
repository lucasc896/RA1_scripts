#!/usr/bin/env python
import sys

def pdgIdLookup(pdgid = ""):

    pref = "-" if pdgid[0] == "-" else ""

    pdgIdDict = {
        2212: "p"
    }

    try:
        return "pref" + pdgIdDict[pdgid]
    except KeyError:
        return "null"

def parseFile(file = None):

    chains = []
    tmp = []
    for line in file:
        if "New Event" in line:
            print "new event line"
            if tmp:
                print "tmp has content, appending to chains"
                chains.append(tmp)
                tmp = []
            else:
                print "tmp is empty"
                tmp = []
        else:
            tmp.append( parseLine(line) )
    chains.append(tmp)

    return chains

def parseLine(line = ""):

    line = line.strip() #remove crap at either end
    line = line.split(" ") #split by whitespace
    return_line = []
    for ent in line:
        if ent:
            return_line.append(ent)

    return line


def main():

    if len(sys.argv) < 2:
        exit(">>> Error: pass a decay chain file.")

    try:
        infile = open(sys.argv[1])
    except IOError:
        exit(">>> FileError: File doesn't exist.")

    chains_list = parseFile(infile)
    infile.close()





    pass

if __name__ == "__main__":
    main()
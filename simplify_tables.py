#!/usr/bin/env python
from sys import argv
import os
import fnmatch

def output_file():
    return [False, True][1]

def harvest_values(line = "", val = [], err = []):

    for bin in line[1:]:
        if bin == "-":
            val.append("-")
            err.append("-")
            continue
        

        bin_split = bin.split("  $\\pm$  ")

        if "\\\\ \n" in bin_split[-1]:
            bin_split[-1] = bin_split[-1].rstrip("\\\\ \n")
            bin_split[-1] = bin_split[-1].rstrip(" ")
        val.append(bin_split[0])
        if len(bin_split)>1:
            err.append(bin_split[1])

def remove_whitespace(line = ""):
    outline = []
    for part in line:
        part = part.rstrip(" ")
        part = part.strip(" ")
        outline.append(part)        
    return outline

def simplify(f_name = ""):
    print "> Simplifying file: %s" % f_name
    f = open(f_name, 'r')
    
    ht_bins = ["237.5", "300", "350", "425", "525", "625", "725", "825", "925", "1025", "1075"]
    data = []
    pred = []
    pred_err = []

    for n, line in enumerate(f.readlines()):
        if n>50: # skip lines beyond first table 
            break
        line_split = line.split("&")
        line_split = remove_whitespace(line_split)
        if line_split[0] == "Total SM prediction":
            harvest_values(line_split, pred, pred_err)
        elif line_split[0] == "Hadronic yield from data":
            harvest_values(line_split, data)
    f.close()

    output_string = ""
    template = "{0:8}{1:10}{2:10}{3:10}"
    output_string += template.format("HT", "Data", "Pred", "Pred err") + "\n"
    
    for ht, d, pr, pre in zip(ht_bins, data, pred, pred_err):
        output_string += template.format(ht, d, pr, pre) + "\n"
    
    if output_file():
        out_file_name = f_name.replace(".tex", ".txt")
        print "> Output to: %s" % out_file_name
        out_file = open(out_file_name, 'w')
        out_file.write(output_string)
        out_file.close()
    else:
        print output_string

def main():

    if len(argv) < 2:
        exit("> ./simplify_tables.py <TexFile_directory>")

    for root,dirs,files in os.walk(argv[1]):
        for filename in fnmatch.filter(files,'RA1*.tex'):
            simplify(f_name = root+"/"+filename)
            
if __name__ == "__main__":
    main()
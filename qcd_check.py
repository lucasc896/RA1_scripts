file = open("chains_genMet50.out")

for line in file:
    if line[0] == "*": continue
    if line[0] == "\n": continue
    if float(line.split(" ")[-1]) < 1000. and float(line.split(" ")[-1]) > 500.:
    # if float(line.split(" ")[-1]) > 1000.:
        print line.split(" ")[0], line.split(" ")[1]
IDX = 12

filenames = []

for i in xrange(0, IDX):
    filenames.append(str(i) + ".out")

with open("./data/merge.out", "w") as outfile:
    for filename in filenames:
        with open(filename) as infile:
            for line in infile:
                outfile.write(line)

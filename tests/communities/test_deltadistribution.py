from communities import build_graph
from communities import generate_graph
from generateStrat import getCorrStatList
from generateStrat import updateProfileCluster
import sys

tracefile = sys.argv[1]
deltas = []
with open(tracefile, "r") as inf:
    for l in inf.readlines():
        words = l.split()
        ts = float(words[2])
        if first:
            first=False
            pts = ts
            continue
        d = ts - pts
        deltas.append(d)
        pts =ts
#readJsonProfileFile = sys.argv[2]
#updateProfileCluster(readJsonProfileFile)
#corr = getCorrStatList()
#(ge, gn) = build_graph(tracefile, corr)
#deltas=[x/1000. for x in range(1000,3000,1)]
#for d in deltas:
#    print(d)
#    generate_graph(ge, gn, d,1)
#

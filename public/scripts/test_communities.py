from communities import build_graph
from communities import generate_graph
import sys

tracefile = sys.argv[1]
(ge, gn) = build_graph(tracefile)
generate_graph(ge, gn, 50)

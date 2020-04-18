import networkx as nx
from networkx.algorithms import community
import itertools
from generateStrat import getVerbose

## get verbose level from generateStrat.py
verbose = getVerbose()
##TODO: class Communities

def build_graph(tracefile, maxWindowSize, staticCorr=None):
    """ Return graph edges. Each node is either a static call site or a full backtrace "dynamic" call.
        TODO: Should graph_nodes be a set or a dictionnary?
    """
    graph_edges = {}
    graph_nodes = set()
    def getVertex(words):
        cur_timestamp = float(words[CSV["index"]])
        if staticCorr:##static approach
            cur_vertix = staticCorr[int(words[CSV["callSite"]])]
        else:##dynamic approach
            cur_vertix = int(words[CSV["callSite"]])
        return (cur_timestamp,cur_vertix)
    ##Defined in Profile.cpp:283
    ##index timeStamp argument doubleP singleP absErr relErr spBoolean callSite
    CSV = {"index":0, "timeStamp":1, "argument":2, "doubleP":3, "singleP":4, "absErr":5, "relErr":6, "spBoolean":7, "callSite":8}
    with open(tracefile, 'r') as trace_file:
        # get rid of the first line
        line = trace_file.readline()
        # run the loop once
        line = trace_file.readline()
        words = line.split()
        (cur_timestamp,cur_vertix) = getVertex(words)
        last_timestamp = cur_timestamp
        last_vertix = cur_vertix
        window = [(cur_timestamp, cur_vertix)]
        insideWindow = 1
        graph_nodes.add(cur_vertix)
        graph_edges[(cur_vertix, cur_vertix)] = [0]
        line = trace_file.readline()
        while line:
            words = line.split()
            (cur_timestamp,cur_vertix) = getVertex(words)
            assert len(window) <  maxWindowSize+1
            window.append((cur_timestamp, cur_vertix))
            assert len(window) <= maxWindowSize+1
            startWindow = 0
            ## For all element inside window, check if they violate
            ## the window range.
            ## startWindow is the index of the first element inside
            ## window NOT violating the range constraint
            for i,x in enumerate(window[:-1]):
                startWindow = i
                if  DeltaWindow > (cur_timestamp - x[0]):
                    break
            ## Update window accordingly: TODO possible bug
            window = window[max(startWindow,len(window)-maxWindowSize):]
            assert len(window) <  maxWindowSize+1
            for i,x in enumerate(window[:-1]):
                delta = cur_timestamp - x[0]
                if (x[1], cur_vertix) in graph_edges:
                    graph_edges[(x[1], cur_vertix)].append(delta)
                else:
                    graph_edges[(x[1], cur_vertix)] = [delta]
            #if (last_vertix, cur_vertix) in graph_edges:
            #    graph_edges[(last_vertix, cur_vertix)].append(cur_timestamp - last_timestamp)
            #else:
            #    graph_edges[(last_vertix, cur_vertix)] = [cur_timestamp - last_timestamp]
            graph_nodes.add(cur_vertix)
            #last_timestamp = cur_timestamp
            #last_vertix = cur_vertix
            line = trace_file.readline()
    return (graph_edges,graph_nodes)

def clustering_algorithm(graph_edges, graph_nodes, threshold, max_depth):
    """ graph_node is a set
        graph_edges is a dictionnary: key is edge, value is list of deltas.
    """
    edges_count = {}
    G = nx.DiGraph()
    G.add_nodes_from(list(graph_nodes))
    for edge, deltas in graph_edges.items():
        count = sum(map(lambda delta: delta < float(threshold), deltas))
        edges_count[edge] = count
        if count > 0:
            G.add_edge(edge[0], edge[1], count=count)
    communities_generator = community.girvan_newman(G)
    depth=0
    hierarchy = []
    for communities in itertools.islice(communities_generator, max_depth):
        com = tuple(sorted(c) for c in communities)
        hierarchy.append(com)
        if verbose > 1:
            print(f"Delta: {threshold}, Girvan Newman hierarchy depth: {depth} ->",com)
        depth += 1
    return hierarchy

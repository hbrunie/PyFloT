import networkx as nx
from networkx.algorithms import community
import itertools
import pdb

## get verbose level from generateStrat.py
verbose = 0
##TODO: class Communities

def build_graph_simplest(searchSet, tracefile, DeltaWindow, maxWindowSize, corrBtSLOC=None):
    CSV = {"index":0, "timeStamp":1, "argument":2, "doubleP":3, "singleP":4, "absErr":5, "relErr":6, "spBoolean":7, "callSite":8}
    def getVertex(words):
        btCallSiteId = int(words[CSV["callSite"]])
        if btCallSiteId not in searchSet:
            return None
        cur_timestamp = float(words[CSV["timeStamp"]])
        if corrBtSLOC:##static approach
            cur_vertix = corrBtSLOC[btCallSiteId]
        else:##dynamic approach
            cur_vertix = btCallSiteId
        return (cur_timestamp,cur_vertix)
    graph_edges = {}
    graph_nodes = set()
    with open(tracefile, 'r') as trace_file:
        # run the loop once
        line = trace_file.readline()
        # get rid of the first line
        if "index" in line:
            line = trace_file.readline()
        words = line.split()
        #pdb.set_trace()
        v = getVertex(words)
        ## ignore nodes which are not in search space
        while line and not v:
            line = trace_file.readline()
            words = line.split()
            v = getVertex(words)
        (cur_timestamp,cur_vertix) = v
        last_timestamp = cur_timestamp
        last_vertix = cur_vertix
        graph_nodes.add(cur_vertix)
        graph_edges[(cur_vertix, cur_vertix)] = [0]
        line = trace_file.readline()
        counter=0
        while line:
            words = line.split()
            v = getVertex(words)
            ## ignore nodes which are not in search space
            while line and not v:
                line = trace_file.readline()
                words = line.split()
                v = getVertex(words)
            (cur_timestamp,cur_vertix) = v
            if last_vertix != cur_vertix:
                graph_nodes.add(cur_vertix)
                if (last_vertix, cur_vertix) in graph_edges:
                    graph_edges[(last_vertix, cur_vertix)].append(cur_timestamp - last_timestamp)
                else:
                    graph_edges[(last_vertix, cur_vertix)] = [cur_timestamp - last_timestamp]
            else:
                if (cur_vertix, cur_vertix) not in graph_edges:
                    graph_edges[(cur_vertix, cur_vertix)] = [cur_timestamp - last_timestamp]
                    graph_nodes.add(cur_vertix)
            last_timestamp = cur_timestamp
            last_vertix = cur_vertix
            line = trace_file.readline()
    return (graph_edges,graph_nodes)

def build_graph(searchSet, tracefile, DeltaWindow, maxWindowSize, corrBtSLOC=None):
    """ Return graph edges. Each node is either a static call site or a full backtrace "dynamic" call.
        TODO: Should graph_nodes be a set or a dictionnary?
    """
    CSV = {"index":0, "timeStamp":1, "argument":2, "doubleP":3, "singleP":4, "absErr":5, "relErr":6, "spBoolean":7, "callSite":8}
    def getVertex(words):
        btCallSiteId = int(words[CSV["callSite"]])
        if corrBtSLOC:##static approach
            cur_vertix = corrBtSLOC[btCallSiteId]
        else:##dynamic approach
            cur_vertix = btCallSiteId
        if cur_vertix not in searchSet:
            return None
        cur_timestamp = float(words[CSV["timeStamp"]])
        return (cur_timestamp,cur_vertix)
    ##Defined in Profile.cpp:283
    ##index timeStamp argument doubleP singleP absErr relErr spBoolean callSite
    graph_edges = {}
    graph_nodes = set()
    with open(tracefile, 'r') as trace_file:
        # run the loop once
        line = trace_file.readline()
        # get rid of the first line
        if "index" in line:
            line = trace_file.readline()
        words = line.split()
        #pdb.set_trace()
        v = getVertex(words)
        ## ignore nodes which are not in search space
        while line and not v:
            line = trace_file.readline()
            words = line.split()
            v = getVertex(words)
        (cur_timestamp,cur_vertix) = v
        last_timestamp = cur_timestamp
        last_vertix = cur_vertix
        window = [(cur_timestamp, cur_vertix)]
        insideWindow = 1
        graph_nodes.add(cur_vertix)
        graph_edges[(cur_vertix, cur_vertix)] = [0]
        line = trace_file.readline()
        while line:
            words = line.split()
            v = getVertex(words)
            ## ignore nodes which are not in search space
            while line and not v:
                line = trace_file.readline()
                words = line.split()
                if len(words) < 1:
                    return (graph_edges,graph_nodes)
                v = getVertex(words)
            (cur_timestamp,cur_vertix) = v
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
            graph_nodes.add(cur_vertix)
            line = trace_file.readline()
    return (graph_edges,graph_nodes)

def community_algorithm_mockup(graph_nodes):
    n = list(graph_nodes)
    n.sort(reverse=True)
    s = len(n)
    n1 = n[:s//4]
    n2 = n[s//4:4*s//5]
    n3 = n[4*s//5:]
    n1 = n[:1]
    n2 = n[1:]
    return [[x] for x in n]
    #print(n,n1,n2,n3)
    #return [n1,n2]
def community_algorithm(graph_edges, graph_nodes, threshold, max_depth, verbose):
    """ if call by SLOC, fill corrSLOC2Bt
        graph_node is a set
        graph_edges is a dictionnary: key is edge, value is list of deltas.
        returns generator of communities in hierarchical order
    """
    edges_count = {}
    G = nx.DiGraph()
    G.add_nodes_from(list(graph_nodes))
    for edge, deltas in graph_edges.items():
        #count = sum(map(lambda delta: delta < float(threshold), deltas))
        count = sum(map(lambda delta: delta < float(threshold), deltas))
        edges_count[edge] = count
        if count > 0:
            G.add_edge(edge[0], edge[1], count=count)
    communities_generator = community.girvan_newman(G)
    try:
        com = next(communities_generator)
        if verbose>3:
            print("Number communities:",len(com))
            print("Communities:",com)
    except StopIteration:
        if verbose>3:
            print("No Community found: number nodes {}.".format(len(graph_nodes)))
        return None
    return com
    #for depth,communities in enumerate(itertools.islice(communities_generator, max_depth)):
    #    if verbose > 1:
    #        print(f"Delta: {threshold}, Girvan Newman hierarchy depth: {depth} ->",com)
    #    yield com

import networkx as nx


def _accumulate_dijkstra_paths(P, start, dest):
    i = dest
    outp_common = [i]
    outp = []
    while(P[i]):
        if(len(P[i]) > 1):
            for j in P[i]:
                variants = _accumulate_dijkstra_paths(P, start, j) 
                outp2 = []
                for m in variants:
                    outp2.append(m + outp_common)
                outp.extend(outp2)
            i = start #done here
        else:
            outp_common = [P[i][0]] + outp_common
            i = P[i][0]
    if(len(outp) == 0):
        return [outp_common]
    return outp

def _collect_all_shortest_paths(G):
    outp = {}
    for a in G:
        S, P, sigma = nx.betweenness._single_source_dijkstra_path_basic(G, a, 'weight')
        # external function taken from taken from https://networkx.github.io/documentation/latest/_modules/networkx/algorithms/centrality/betweenness.html
        outp[a] = {}
        # P now includes all paths starting from node a
        for b in G:
            if(a < b):
                outp[a][b] = _accumulate_dijkstra_paths(P, a, b)
    return outp

def effective_load(G, Verbose=False):
    pathSets = _collect_all_shortest_paths(G) 

    # Prepare all available pairs of nodes that can communicate.
    # Problem is simplified to undirected graphs only!
    allPairs = []
    for v in G:
        for w in G:
            if v < w:
                allPairs.append((v, w))
    number_pairs = len(allPairs)

    # calculate the load on each edge, given that all node pairs are
    # communicating via their shortest paths (100% load)
    outp = {}
    for u in G.edges():
        count = 0
        for comPair in allPairs: # n*(n-1)/2 iterations
            for path in pathSets[comPair[0]][comPair[1]]:
                if u[0] in path and u[1] in path and abs(path.index(u[1]) - path.index(u[0])) == 1 :
                    count += 1
        if Verbose: 
            print(u, 'absolute:',count,'/',number_pairs, "relative: {0:.2f}".format(count / number_pairs))
        outp[u] = count / number_pairs
    return outp



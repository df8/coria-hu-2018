'''
Created on Jan 18, 2018

@author: Natalie

based on NetworkX 1.0 connectivity.cuts using (s,t)-minimum cut [1] or METIS for Python [2]
[1] is not fulfilling the required algorithm by [3], [2] needs prior installation of several tools, compilers and packages
please follow the documentation
    
references 
[1]Abdol-Hossein Esfahanian. Connectivty Algorithms. http://www.cse.msu.edu/~cse835/Papers/Graph_connectivity_revised.pdf
[2]https://metis.readthedocs.io/en/latest/
[3]Oehlers, Milena and Fabian, Benjamin: Graph Metrics for Internet Robustness: A Survey. Submitted for review in March 2018.
'''

import networkx as nx
import matplotlib.pyplot as plt
import random
#import metis 


def plot_graph(Graph):
    options = {
    'node_color': 'yellow',
    'font_weight': 'bold',
    'node_size': 800,
    'with_labels': True,
    'width': 3
    }
    
    # plot graph 
    nx.draw(Graph, **options)
    plt.show()
    
def print_basics(Graph, Graph_name):
    print("Name of the Graph: {0}".format(Graph_name))
    print("Number of nodes: {0}".format(len(Graph)))
    print("Number of edges: {0}".format(Graph.number_of_edges()))
    print("\n")

def linear_graph():
    L = nx.Graph()   
    L.add_nodes_from([0,1,2,3], weight = 1)
    L.add_edges_from([(0,1),(1,2),(2,3)])
    #plot_graph(L)
    print_basics(L, "Linear Graph") 
    return(L)    
    
def local_resilience(G, h, i):
    #Local resilience    
    if (h < 0) or (type(h) is not int):
        raise ValueError("h-hop environment radius is not a natural number")
    
    if G.has_node(i):
        return len(nx.minimum_node_cut(nx.ego_graph(G, i, h)))  
        #return len(metis.part_graph(nx.ego_graph(G, i, h)))  
    else:
        raise ValueError("{0} is not in given Graph".format(i))


def global_resilience(G):
    #Global resilience
    #Calculate the size of the reachable nodes set for each node in the graph G    
    h_max = len(G)
    
    # for each node n in Graph G calculate the h-hop environment h_ball, then number of nodes n_cnt in h_ball, and the local Resilience Rih  
    # declare lists for the average number of nodes n_global and average resilience R_global in each h-hop environment
    n_global = list()
    R_global = list()       
    for h in range(h_max):
        n_sum = 0
        Rnh_sum = 0
        
        for n in G:
            h_ball = nx.ego_graph(G,n,h)
            n_count = len(h_ball)
            Rih = len(nx.minimum_node_cut(h_ball))
            #Rih = len(metis.part_graph(h_ball))
            n_sum += n_count
            Rnh_sum += Rih
        
        # calculate average resilience for h-hop environment h
        n_global.append(n_sum/h_max) 
        R_global.append(Rnh_sum/h_max)
        
    return n_global, R_global

def targeted_attack(graph, centrality_metric):
    #graph = graph.copy()
    ranks = centrality_metric(graph)
    nodes = sorted(graph.nodes(), key=lambda n: ranks[n])
    
    return nodes

def random_attack(graph):
    #graph = graph.copy()
    node_rank = random.choice(list(graph.nodes))
    return node_rank

def plot_global_resilience(x, y):
    plt.xlabel('Average node size')
    plt.ylabel('Average Resilience')
    plt.title('Global Resilience')
    plt.plot(x, y)
    plt.show()
 
# check whether a Graph is simple or directed and computes whether the graph is connected or not accordingly
# for simple and directed graph the computation of a connected graph differ
# therefore different methods have to be applied      
def check_connection(Graph):
    if nx.is_directed(Graph):
        return nx.is_weakly_connected(Graph)
    else:
        return nx.is_connected(Graph)

print("------ Start program -------\n")

# import Internet graph from file as-22july06.gml
#I06 = nx.read_gml("as-22july06.gml")
#print_basics(I06, "Internetgraph 2006")

# compute different graph types
L = linear_graph()
T = nx.balanced_tree(3, 2)
R = nx.dense_gnm_random_graph(4, 16, 123)
R = nx.gnm_random_graph(4, 14, 123, True)
G = nx.icosahedral_graph()

node = 3
h_hop = 2
print(str(local_resilience(R,node,h_hop)) + " is the local Resilience of the graph {0} for node {1} in the h-hop environment {2}.\n".format(R, node, h_hop ))
R_global = global_resilience(G)
plot_global_resilience(R_global[0], R_global[1])


print("Starting attacks ... \n")
node = 3
h_hop = 2
plot_graph(R)
n_rank = targeted_attack(R, nx.betweenness_centrality)
    
while check_connection(R):
    print(str(local_resilience(R,3,2)) + " is the local Resilience of the graph {0} for node {1} in the h-hop environment {2}.\n".format(R, node, h_hop ))
    
    R.remove_node(n_rank.pop())
    plot_graph(R)

print("------ Terminate program  -------\n")

# Resilience.py

'''
Created on March 26, 2018

@author: Natalie

'''
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from scipy.integrate import quad
import random

def plot_graph(Graph):
    options = {
    'node_color': 'yellow',
    'font_weight': 'bold',
    'node_size': 800,
    'with_labels': True,
    'width': 3
    }

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

def capacity_b(Graph):
    return np.array(np.repeat(1,len(Graph)))

def routing_matrix(Graph):
    # calculate routing matrix and fill with standard shortest path
    # TODO: skip first path
    Rm = np.array(np.repeat(0, len(Graph)))
    for n in Graph:
        all_path = nx.single_source_dijkstra_path(Graph, n)
        for path in all_path:
            tmp = np.array(np.repeat(0, len(Graph)))
            for path_element in all_path[path]:
                for link in Graph:       
                    if(path_element == link):
                        tmp[link] = 1
                        break            
                Rm = np.vstack([Rm, tmp])       
    return Rm

def targeted_attack(graph, centrality_metric):
    #graph = graph.copy()
    ranks = centrality_metric(graph)
    nodes = sorted(graph.nodes(), key=lambda n: ranks[n])
    
    return nodes

def random_attack(graph):
    #graph = graph.copy()
    node_rank = random.choice(list(graph.nodes))
    return node_rank

def integrand(n, a, r, x_vec):  
    return (1/a)*r*n*1

def plot_elasticity(x, y):
    x.append(0)
    y.append(0)
    plt.plot(x, y)
    plt.gca().invert_xaxis()
    plt.xlabel('%n in Graph')
    plt.ylabel('T(n) Traffic matrix')
    plt.title('Elasticity')
    plt.show()

print("------ Start program -------\n")
# import Internet graph from file as-22july06.gml
#I06 = nx.read_gml("as-22july06.gml")
#print_basics(I06, "Internetgraph 2006")

# compute different graph types
L_original = linear_graph()
T = nx.balanced_tree(3, 2)
R = nx.dense_gnm_random_graph(4, 16, 123)
R = nx.gnm_random_graph(4, 14, 123, True)

print("Compute Elasticity ... \n")
L = L_original.copy()
N_SIZE = len(L_original)
a_integral = 1
b_integral = 1
x_points = list()
y_points = list()
I_list = list()

print("Starting attacks ... \n")
n_rank = targeted_attack(L_original, nx.betweenness_centrality)

while nx.is_connected(L):
    plot_graph(L)
    # check no loops, no parallel links in graph
    try: 
        nx.find_cycle(L, 'original') 
    except:
        pass
    
    b = capacity_b(L)    
    R_fl = routing_matrix(L)                   
    R_lf = np.transpose(R_fl)
    x = np.array(np.repeat(1, len(R_fl)))  
    Rx = np.dot(R_lf,x)
    roh = 2
    
    alpha = roh*len(R_fl)
    n_fraction = len(L)/len(L_original)
    b_integral = a_integral - n_fraction
    
    I = quad(integrand, b_integral, a_integral, args=(alpha, roh, x))
    print(I)
    print(I[0])
    I_list.append(I[0])
    x_points.append(n_fraction)
    y_points.append(50)

    a_integral = b_integral
    L.remove_node(n_rank.pop())
    plot_graph(L)

plot_elasticity(x_points, y_points)

print("The elasticity after the attack is {0}\n".format(sum(I_list)))

print("------ Terminate program  -------")
# Elasticity.py

'''
Created on March 26, 2018

@author: Natalie

'''
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from scipy.integrate import quad
import random
from _overlapped import NULL

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
    Linear = nx.Graph()   
    Linear.add_nodes_from([0,1,2,3], weight = 1)
    Linear.add_edges_from([(0,1),(1,2),(2,3)])
    return(Linear)

def capacity_b(Graph):
    return np.array(np.repeat(1,len(Graph)))

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

# calculate routing matrix and fill with standard shortest path
def fill_routing_matrix(route_graph):
    print_basics(route_graph, "Routed graph")
    #plot_graph(route_graph)
    '''
    if len(route_graph) <= 1:
        return np.array(np.repeat(0, len(route_graph)))
    '''
    routing_matrix = np.array(np.repeat(0, len(route_graph)))
    # for each node in the graph calculate their standard shortest path routing with dijkstra
    for n in route_graph:
        all_path = nx.single_source_dijkstra_path(route_graph, n)
        print("Standard shortest path calculated for node {0}".format(n))
        
        # for each shortest path for one node in the graph define an array with n elements
        # the element in the array is 1 when the shortest path flows through the node
        # otherwise 0
        for path in all_path:
            tmp = np.array(np.repeat(0, len(route_graph)))
            for path_element in all_path[path]:
                
                node_idx = 0
                for link in route_graph:       
                    if(path_element == link):
                        tmp[node_idx] = 1
                        continue 
                    node_idx += 1 
                    
            # add each shortest path transformed into an array tmp to the routing matrix 
            if len(tmp) == len(route_graph):         
                routing_matrix = np.vstack([routing_matrix, tmp])  
            else:
                print("Error: array with shortest path does not have one entry for each node")
                routing_matrix = np.vstack([routing_matrix, np.array(np.repeat(0, len(route_graph)))])
            tmp = NULL
                     
    return routing_matrix
    
# check whether a Graph is simple or directed and computes whether the graph is connected or not accordingly
# for simple and directed graph the computation of a connected graph differ
# therefore different methods have to be applied    
def check_connection(Graph):
    if nx.is_directed(Graph):
        try:
            is_connected = nx.is_weakly_connected(Graph)
        except (ValueError, RuntimeError, TypeError, NameError):
            pass        
    else:
        try:
            is_connected = nx.is_connected(Graph)
        except (ValueError, RuntimeError, TypeError, NameError):
            pass
        
    return is_connected

def check_loops(graph):
    # check no loops, no parallel links in graph
    try:
        loops = nx.find_cycle(graph)
    except (ValueError, RuntimeError, TypeError, NameError):
        pass
        
    if loops != []:
        return True
    else:
        return False
    
def calculate_elasticity(graph):
    print("Compute Elasticity ... \n")
    exit_result = ([0],[0],[0])
    if graph.number_of_nodes() <= 1 | graph.number_of_edges() <= 0:
        print("Empty graph")
        return exit_result
    
    graph = graph.copy()
    n_size = len(graph)
    a_integral = 1.0
    b_integral = 1.0
    x_points = list()
    y_points = list()
    I_list = list()

    print("Starting attacks ... \n")
    n_rank = targeted_attack(graph, nx.betweenness_centrality)
    print("Removal rank of nodes: {0}".format(n_rank))
    while check_connection(graph):
        '''
        if check_loops(graph) == True:
            print("The graph contains self loops. Elasticity can't be computed.\n")
            return exit_result
        '''
                
        print("Next round under attack...")
        print_basics(graph, "Graph under attack")
        #plot_graph(graph)
        # calculate the metric Elasticity according to (Oehlers and Fabian 2018, p. 21)
        b = capacity_b(graph)    
        R_fl = fill_routing_matrix(graph) 
        print("Routing matrix filled")                  
        R_lf = np.transpose(R_fl)
        x = np.array(np.repeat(1, len(R_fl)))  
        Rx = np.dot(R_lf,x)
        rho = 1
        
        if(a_integral == b_integral):
            alpha = rho*len(R_fl)
            
        traffic_g = (1/alpha)*rho*sum(x)
        print("Traffic calculated")
        # calculate area under the curve %node vs traffic matrix in the interval 
        #    a_integral, the lower limit of integration, and 
        #    b_integral, the upper limit of integration
        n_fraction = graph.number_of_nodes()/n_size 
        if n_fraction > 1:
            print("Error: fraction of nodes is bigger than 100%, Nodes were added to the graph")
            return exit_result
        
        if (n_fraction < 1.0 and n_fraction >= 0.0):
            a_integral = n_fraction
        
        I = quad(integrand, a_integral, b_integral, args=(alpha, rho, x))
        print("Integral calculated")
        I_list.append(I[0])
        x_points.append(n_fraction)
        y_points.append(traffic_g) 
        print("New points added to result")
    
        b_integral = a_integral
        print("New integral borders defined")
        graph.remove_node(n_rank.pop())
        print("Node removed")
        
        if graph.number_of_edges() == 0:
            result = (x_points, y_points, I_list) 
            return result
    
    print("Ending attack ...")
    result = (x_points, y_points, I_list) 
    print("Result-arrays saved in one list")   
    return result

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
L = linear_graph()
T = nx.balanced_tree(3, 2)
R = nx.dense_gnm_random_graph(4, 16, 123)
R = nx.gnm_random_graph(4, 14, 123, True)
G = nx.icosahedral_graph()

Test = nx.Graph()   
Test.add_nodes_from([0,1,2,3], weight = 1)
Test.add_edges_from([(0,1),(1,2),(2,3),(3,0),(0,2)])

elasticity = calculate_elasticity(G)
print(elasticity[2])
print("The elasticity of the graph after the attack is {0}\n".format(round(sum(elasticity[2]), 4)))
plot_elasticity(elasticity[0], elasticity[1])

print("------ Terminate program  -------")
# Elasticity.py

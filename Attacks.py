'''
Created on 30.03.2018

@author: https://stackoverflow.com/questions/17338146/how-to-simulate-the-random-and-targeted-attacks-in-complex-network-and-python
'''

import random
import networkx as nx
#from ComplexNetworkSim import NetworkSimulation, AnimationCreator, PlotCreator

def attack(graph, centrality_metric):
    graph = graph.copy()
    steps = 0
    ranks = centrality_metric(graph)
    nodes = sorted(graph.nodes(), key=lambda n: ranks[n])
    while nx.is_connected(graph):
        graph.remove_node(nodes.pop())
        steps += 1
    else:
        return steps
    


def random_attack(graph):
    graph = graph.copy()
    steps = 0

    while nx.is_connected(graph):
        node = random.choice(list(graph.nodes))
        graph.remove_node(node)
        steps += 1
    else:
        return steps

NETWORK_SIZE = 1000
print("Creating powerlaw cluster with {0} Nodes.".format(NETWORK_SIZE))
K = 4
P = 0.1
HK = nx.powerlaw_cluster_graph(NETWORK_SIZE, K, 0.1)

print("Starting attacks...")
print("Network with  Scale-free Model broke after {0} steps with random attack.".format(random_attack(HK)))
print("Network with Scale-free Model broke after {0} steps with Targeted Attacks.".format(attack(HK, nx.betweenness_centrality)))
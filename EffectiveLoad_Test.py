import unittest
import networkx as nx
import EffectiveLoad


class Test_EffectiveLoad_Test(unittest.TestCase):
    def setUp(self):
        G = nx.Graph()
        G.add_nodes_from(list(range(0, 9)))
        names = ['S', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'Z']
        for v in G.nodes():    
            G.node[v]['name'] = names[v]

        # creating some edges
        edges = [(0, 1, 3), (0, 2, 2), (0, 7, 4), (1, 2, 1), (1, 3, 3), (2, 3, 8), (3, 4, 4), 
                 (3, 5, 6), (4, 5, 2), (4, 6, 8), (4, 7, 10), (5, 8, 7), (6, 8, 11)]

        G.add_weighted_edges_from(edges)
        self.G = G
        return super().setUp()

    def test_A(self):
        # Run
        results = EffectiveLoad.effective_load(self.G) #returns an associative array with one entry for each communicating pair
        self.assertEqual(results[(1,3)] * 36, 30)
        self.assertEqual(results[(5,8)] * 36, 13)

if __name__ == '__main__':
    unittest.main()

import unittest
import networkx as nx
from multilevel_graphs import MultilevelGraph, DecGraph


class MultilevelGraphTest(unittest.TestCase):
    def test_natural_transformation_1(self):
        dec_graph = MultilevelGraph.natural_transformation(nx.DiGraph([(1, 2, {'weight': 3})]))
        self.assertTrue(isinstance(dec_graph, DecGraph))

    if __name__ == '__main__':
        unittest.main()

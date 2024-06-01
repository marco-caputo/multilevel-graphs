import unittest
import networkx as nx
from multilevel_graphs import MultilevelGraph, DecGraph


class MultilevelGraphTest(unittest.TestCase):
    def test_natural_transformation_1(self):
        dec_graph = MultilevelGraph.natural_transformation(nx.DiGraph([(1, 2, {'weight': 3})]))
        self.assertTrue(isinstance(dec_graph, DecGraph))
        self.assertEqual(dec_graph.nodes_keys(), {1, 2})
        self.assertEqual(dec_graph.edges_keys(), {(1, 2)})
        self.assertEqual(dec_graph.E[(1, 2)].attr, {'weight': 3})
        self.assertFalse(dec_graph.E[(1, 2)].dec)

    def test_natural_transformation_2(self):
        nx_graph = nx.DiGraph()
        nx_graph.add_node(1, weight=1)
        nx_graph.add_node(2, weight=2)
        nx_graph.add_node(3, weight=3)
        nx_graph.add_edges_from([(1, 2, {'weight': 3}), (1, 3, {'weight': 4})])

        dec_graph = MultilevelGraph.natural_transformation(nx_graph)
        self.assertTrue(isinstance(dec_graph, DecGraph))
        self.assertEqual(dec_graph.nodes_keys(), {1, 2, 3})
        self.assertEqual(dec_graph.edges_keys(), {(1, 2), (1, 3)})
        self.assertEqual(dec_graph.V[1].attr, {'weight': 1})
        self.assertTrue(not dec_graph.V[2].dec.nodes())

    def test_build_0_height_ml_graph(self):
        graph = nx.DiGraph()
        graph.add_node(1, weight=20)
        graph.add_node(2, weight=10)
        graph.add_node(3, weight=30)
        graph.add_edges_from([(1, 2, {'weight': 25}), (1, 3, {'weight': 35})])

        ml_graph = MultilevelGraph(graph)

        self.assertEqual({1, 2, 3}, ml_graph.get_graph(0).nodes_keys())
        self.assertEqual({(1, 2), (1, 3)}, ml_graph.get_graph(0).edges_keys())
        self.assertEqual(MultilevelGraph.natural_transformation(graph), ml_graph.get_graph(0))

        self.assertEqual(0, ml_graph.height())
        self.assertEqual((ml_graph[0], 0), ml_graph._highest_valid_graph())


if '__main__' == __name__:
    unittest.main()

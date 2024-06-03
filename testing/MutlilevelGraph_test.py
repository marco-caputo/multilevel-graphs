import unittest
import networkx as nx
from multilevel_graphs import MultilevelGraph, DecGraph, SCCsContractionScheme, CliquesContractionScheme, \
    CyclesContractionScheme


class MultilevelGraphTest(unittest.TestCase):
    def test_natural_transformation_1(self):
        dec_graph = MultilevelGraph.natural_transformation(nx.DiGraph([(1, 2, {'weight': 3})]))
        self.assertTrue(isinstance(dec_graph, DecGraph))
        self.assertEqual(dec_graph.nodes_keys(), {1, 2})
        self.assertEqual(dec_graph.edges_keys(), {(1, 2)})
        self.assertEqual(dec_graph.E[(1, 2)].attr, {'weight': 3})
        self.assertFalse(dec_graph.E[(1, 2)].dec)

    def test_natural_transformation_2(self):
        dec_graph = MultilevelGraph.natural_transformation(self.get_sample_graph_1())
        self.assertTrue(isinstance(dec_graph, DecGraph))
        self.assertEqual(dec_graph.nodes_keys(), {1, 2, 3})
        self.assertEqual(dec_graph.edges_keys(), {(1, 2), (2, 1), (1, 3)})
        self.assertEqual(dec_graph.V[1].attr, {'weight': 20})
        self.assertTrue(not dec_graph.V[2].dec.nodes())

    def test_build_0_height_ml_graph(self):
        ml_graph = MultilevelGraph(self.get_sample_graph_1())

        self.assertEqual({1, 2, 3}, ml_graph.get_graph(0).nodes_keys())
        self.assertEqual({(1, 2), (2, 1), (1, 3)}, ml_graph.get_graph(0).edges_keys())
        self.assertEqual(MultilevelGraph.natural_transformation(self.get_sample_graph_1()), ml_graph.get_graph(0))

        self.assertEqual(0, ml_graph.height())
        self.assertEqual((ml_graph[0], 0), ml_graph._highest_valid_graph())

    def test_build_1_height_ml_graph(self):
        ml_graph = MultilevelGraph(self.get_sample_graph_1(), [SCCsContractionScheme()])

        self.assertEqual(1, ml_graph.height())
        self.assertEqual({1, 2, 3}, ml_graph.get_graph(0).nodes_keys())
        self.assertTrue(all(n.supernode is None for n in ml_graph.get_graph(0).nodes()))
        self.assertEqual((ml_graph[0], 0), ml_graph._highest_valid_graph())

        self.assertTrue(all(n.level == 1 for n in ml_graph.get_graph(1).nodes()))
        self.assertEqual(2, len(ml_graph.get_graph(1)))
        self.assertEqual((ml_graph[1], 1), ml_graph._highest_valid_graph())

    def test_build_2_height_ml_graph(self):
        ml_graph = MultilevelGraph(self.get_sample_graph_1(), [SCCsContractionScheme(),
                                                               CliquesContractionScheme(reciprocal=False)])

        self.assertEqual(2, ml_graph.height())
        self.assertEqual({1, 2, 3}, ml_graph.get_graph(0).nodes_keys())
        self.assertEqual((ml_graph[0], 0), ml_graph._highest_valid_graph())

        self.assertEqual(2, len(ml_graph.get_graph(1)))
        self.assertTrue(all(n.supernode is None for n in ml_graph.get_graph(1).nodes()))
        self.assertEqual((ml_graph[1], 1), ml_graph._highest_valid_graph())

        self.assertEqual(1, len(ml_graph.get_graph(2)))
        self.assertTrue(all(n.level == 2 for n in ml_graph.get_graph(2).nodes()))
        self.assertEqual((ml_graph[2], 2), ml_graph._highest_valid_graph())

        self.assertEqual(ml_graph.get_graph(0), ml_graph.get_graph(1).complete_decontraction())
        self.assertEqual(ml_graph.get_graph(1), ml_graph.get_graph(2).complete_decontraction())

    def test_build_contraction_schemes(self):
        ml_graph = MultilevelGraph(self.get_sample_graph_1(), [SCCsContractionScheme(),
                                                               CliquesContractionScheme(reciprocal=False)])

        ml_graph.build_contraction_schemes()
        self.assertEqual(2, ml_graph._highest_valid_graph()[1])

    def test_build_contraction_schemes_2(self):
        ml_graph = MultilevelGraph(self.get_sample_graph_1(), [SCCsContractionScheme(),
                                                               CliquesContractionScheme(reciprocal=False)])

        ml_graph.build_contraction_schemes(upper_level=1)
        self.assertEqual(1, ml_graph._highest_valid_graph()[1])

    def test_append_contraction_scheme_1(self):
        ml_graph = MultilevelGraph(self.get_sample_graph_1(), [SCCsContractionScheme()])
        self.assertEqual(1, ml_graph.height())
        ml_graph.get_graph(1)

        ml_graph.append_contraction_scheme(CliquesContractionScheme(reciprocal=False))
        self.assertEqual(2, ml_graph.height())
        self.assertEqual(1, ml_graph._highest_valid_graph()[1])

        ml_graph.get_graph(2)
        self.assertEqual(2, ml_graph._highest_valid_graph()[1])

    def test_append_contraction_scheme_2(self):
        ml_graph = MultilevelGraph(self.get_sample_graph_1())
        self.assertEqual(0, ml_graph.height())

        ml_graph.append_contraction_scheme(SCCsContractionScheme())
        self.assertEqual(1, ml_graph.height())
        self.assertEqual(0, ml_graph._highest_valid_graph()[1])

        ml_graph.append_contraction_scheme(CliquesContractionScheme(reciprocal=False))
        self.assertEqual(2, ml_graph.height())
        self.assertEqual(0, ml_graph._highest_valid_graph()[1])

        ml_graph.get_graph(2)
        self.assertEqual(2, ml_graph._highest_valid_graph()[1])

    def test_add_node_1(self):
        ml_graph = MultilevelGraph(self.get_sample_graph_1())
        self.assertEqual(0, ml_graph.height())
        self.assertEqual({1, 2, 3}, ml_graph.get_graph(0).nodes_keys())

        ml_graph.add_node(4, weight=40)
        self.assertEqual(0, ml_graph.height())
        self.assertEqual({1, 2, 3, 4}, ml_graph.get_graph(0).nodes_keys())
        self.assertEqual(40, ml_graph.get_graph(0).V[4].attr['weight'])

    def test_add_node_2(self):
        ml_graph = MultilevelGraph(self.get_sample_graph_1(), [SCCsContractionScheme()])
        self.assertEqual(1, ml_graph.height())
        self.assertEqual({1, 2, 3}, ml_graph.get_graph(0).nodes_keys())
        self.assertEqual(2, len(ml_graph.get_graph(1)))

        ml_graph.add_node(4, weight=40)
        self.assertEqual({1, 2, 3, 4}, ml_graph.get_graph(0).nodes_keys())
        self.assertEqual(0, ml_graph._highest_valid_graph()[1])
        self.assertEqual(3, len(ml_graph.get_graph(1)))
        self.assertEqual(1, ml_graph._highest_valid_graph()[1])

    def test_add_node_3(self):
        ml_graph = MultilevelGraph(self.get_sample_graph_1(), [SCCsContractionScheme(),
                                                               CliquesContractionScheme(reciprocal=False)])
        self.assertEqual(2, len(ml_graph.get_graph(1)))
        ml_graph.build_contraction_schemes(1)

        ml_graph.add_node(4, weight=40)
        self.assertEqual(0, ml_graph._highest_valid_graph()[1])
        self.assertEqual(3, len(ml_graph.get_graph(1)))
        self.assertEqual(1, ml_graph._highest_valid_graph()[1])
        self.assertEqual(2, len(ml_graph.get_graph(2)))
        self.assertEqual(2, ml_graph._highest_valid_graph()[1])

    def test_add_edge_1(self):
        ml_graph = MultilevelGraph(self.get_sample_graph_1())
        self.assertEqual(0, ml_graph.height())
        self.assertEqual({1, 2, 3}, ml_graph.get_graph(0).nodes_keys())
        self.assertEqual({(1, 2), (2, 1), (1, 3)}, ml_graph.get_graph(0).edges_keys())

        ml_graph.add_edge(2, 3, weight=25)
        self.assertEqual(0, ml_graph.height())
        self.assertEqual({1, 2, 3}, ml_graph.get_graph(0).nodes_keys())
        self.assertEqual({(1, 2), (2, 1), (1, 3), (2, 3)}, ml_graph.get_graph(0).edges_keys())
        self.assertEqual(25, ml_graph.get_graph(0).E[(2, 3)].attr['weight'])

    def test_add_edge_2(self):
        ml_graph = MultilevelGraph(self.get_sample_graph_1(),
                                   [CliquesContractionScheme(reciprocal=True)])

        self.assertEqual(2, len(ml_graph.get_graph(1)))

        ml_graph.add_edge(3, 1, weight=25)
        self.assertEqual({(1, 2), (2, 1), (1, 3), (3, 1)}, ml_graph.get_graph(0).edges_keys())
        self.assertEqual(0, ml_graph._highest_valid_graph()[1])
        self.assertEqual(3, len(ml_graph.get_graph(1)))
        self.assertEqual(1, ml_graph._highest_valid_graph()[1])

    def test_add_edge_3(self):
        graph = self.get_sample_graph_1()
        graph.add_node(4, weight=40)

        ml_graph = MultilevelGraph(graph, [CliquesContractionScheme(reciprocal=True),
                                           CyclesContractionScheme(maximal=True)])

        self.assertEqual(3, len(ml_graph.get_graph(1)))
        self.assertEqual(3, len(ml_graph.get_graph(2)))

        ml_graph.add_edge(4, 2, weight=45)
        ml_graph.add_edge(3, 4, weight=55)
        self.assertEqual(0, ml_graph._highest_valid_graph()[1])
        self.assertEqual(3, len(ml_graph.get_graph(1)))
        self.assertEqual(1, ml_graph._highest_valid_graph()[1])
        self.assertEqual(1, len(ml_graph.get_graph(2)))

    def test_add_edge_4(self):
        graph = self.get_sample_graph_1()
        graph.add_node(4, weight=40)

        ml_graph = MultilevelGraph(graph, [CliquesContractionScheme(reciprocal=True),
                                           CyclesContractionScheme(maximal=True)])

        ml_graph.add_edge(4, 2, weight=45)
        ml_graph.add_edge(3, 4, weight=55)
        self.assertEqual(1, len(ml_graph.get_graph(2)))
        self.assertEqual(3, len(next(iter(ml_graph.get_graph(2).nodes()))))

    def test_merge_graph(self):
        ml_graph = MultilevelGraph(self.get_sample_graph_1(), [CliquesContractionScheme(reciprocal=True),
                                                               CyclesContractionScheme(maximal=True)])
        ml_graph.build_contraction_schemes(2)

        graph_to_merge = nx.DiGraph()
        graph_to_merge.add_edges_from([(3, 4, {'weight': 3}), (4, 2, {'weight': 4})])
        ml_graph.merge_graph(graph_to_merge)

        self.assertEqual(0, ml_graph._highest_valid_graph()[1])
        self.assertEqual(3, len(ml_graph.get_graph(1)))
        self.assertEqual(1, ml_graph._highest_valid_graph()[1])
        self.assertEqual(1, len(ml_graph.get_graph(2)))

    def test_merge_graph_2(self):
        ml_graph = MultilevelGraph(self.get_sample_graph_2(), [CliquesContractionScheme(reciprocal=True),
                                                               CyclesContractionScheme(maximal=True)])
        ml_graph.build_contraction_schemes(2)
        self.assertTrue(all(len(n.component_sets) == 1 for n in ml_graph.get_graph(1).nodes()))
        self.assertTrue(all(len(c_set) == 1 for c_set in ml_graph.get_component_sets(1)))

        ml_graph.merge_graph(self.get_sample_graph_1())

        self.assertEqual(5, len(ml_graph.get_graph(1)))
        self.assertEqual(2, len(ml_graph.get_graph(0).V[1].supernode.component_sets))
        self.assertEqual(3, len(ml_graph.get_graph(2)))

    def test_remove_node_1(self):
        graph = self.get_sample_graph_1()
        graph.add_node(4, weight=40)

        ml_graph = MultilevelGraph(graph)
        self.assertEqual(4, len(ml_graph.get_graph(0)))

        ml_graph.remove_node(4)
        self.assertEqual(3, len(ml_graph.get_graph(0)))
        self.assertTrue(4 not in ml_graph.get_graph(0).nodes_keys())

    def test_remove_node_2(self):
        graph = self.get_sample_graph_2()
        graph.add_node(6, weight=60)

        ml_graph = MultilevelGraph(graph, [CyclesContractionScheme(maximal=True),
                                           SCCsContractionScheme()])
        ml_graph.build_contraction_schemes(2)
        self.assertEqual(4, len(ml_graph.get_graph(1)))
        self.assertEqual(2, len(ml_graph.get_graph(2)))

        ml_graph.remove_node(6)
        self.assertEqual(5, len(ml_graph.get_graph(0)))
        self.assertEqual(3, len(ml_graph.get_graph(1)))
        self.assertEqual(1, len(ml_graph.get_graph(2)))

    def test_remove_edge_1(self):
        graph = self.get_sample_graph_1()

        ml_graph = MultilevelGraph(graph)

        ml_graph.remove_edge(1, 2)
        self.assertEqual(3, len(ml_graph.get_graph(0)))
        self.assertEqual(2, len(ml_graph.get_graph(0).edges()))
        self.assertTrue((1, 2) not in ml_graph.get_graph(0).edges_keys())

    def test_remove_edge_2(self):
        graph = self.get_sample_graph_2()

        ml_graph = MultilevelGraph(graph, [CyclesContractionScheme(maximal=True),
                                           SCCsContractionScheme()])
        self.assertEqual(3, len(ml_graph.get_graph(1)))
        self.assertEqual(1, len(ml_graph.get_graph(2)))

        ml_graph.remove_edge(1, 2)
        self.assertEqual(5, len(ml_graph.get_graph(0)))
        self.assertEqual(6, len(ml_graph.get_graph(0).edges()))
        self.assertEqual(3, len(ml_graph.get_graph(1)))
        self.assertEqual(2, len(ml_graph.get_graph(1).edges()))
        self.assertEqual(3, len(ml_graph.get_graph(2)))
        self.assertEqual(2, len(ml_graph.get_graph(2).edges()))

    def test_remove_node_and_edge(self):
        graph = self.get_sample_graph_2()

        ml_graph = MultilevelGraph(graph, [CyclesContractionScheme(maximal=True),
                                           SCCsContractionScheme()])

        ml_graph.remove_node(2)
        self.assertEqual(4, len(ml_graph.get_graph(0)))
        self.assertEqual(4, len(ml_graph.get_graph(0).edges()))
        self.assertEqual(2, len(ml_graph.get_graph(1)))
        self.assertEqual(1, len(ml_graph.get_graph(1).edges()))
        self.assertEqual(2, len(ml_graph.get_graph(2)))
        self.assertEqual(1, len(ml_graph.get_graph(2).edges()))

        self.assertTrue(2 not in ml_graph.get_graph(0).nodes_keys())
        self.assertTrue(1, len(ml_graph.get_graph(0).V[1].supernode.supernode.component_sets))
        self.assertTrue(1, len(next(iter(ml_graph.get_graph(0).V[1].supernode.supernode.component_sets))))

    def get_sample_graph_1(self):
        graph = nx.DiGraph()
        graph.add_node(1, weight=20)
        graph.add_node(2, weight=10)
        graph.add_node(3, weight=30)
        graph.add_edges_from([(1, 2, {'weight': 25}), (2, 1, {'weight': 15}), (1, 3, {'weight': 35})])
        return graph

    def get_sample_graph_2(self):
        graph = nx.DiGraph()
        graph.add_node(1, weight=20)
        graph.add_node(2, weight=10)
        graph.add_node(3, weight=30)
        graph.add_node(4, weight=40)
        graph.add_node(5, weight=50)
        graph.add_edges_from([(1, 2, {'weight': 25}), (2, 3, {'weight': 15}), (3, 1, {'weight': 35}),
                              (2, 4, {'weight': 45}), (4, 3, {'weight': 55}), (3, 5, {'weight': 65}),
                              (5, 4, {'weight': 75})])
        return graph

if '__main__' == __name__:
    unittest.main()

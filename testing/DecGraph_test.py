import unittest
from multilevel_graphs import DecGraph, Supernode, Superedge


class DecGraphTest(unittest.TestCase):

    def setUp(self):
        self.test_supernodes_0 = [Supernode(i, 0) for i in range(8)]
        self.test_superedges_0 = \
            [Superedge(self.test_supernodes_0[0], self.test_supernodes_0[i], 0) for i in range(1, 8)]

        self.test_supernodes_1 = [Supernode(i, 1) for i in range(3)]
        self.test_superedges_1 = \
            [Superedge(self.test_supernodes_1[0], self.test_supernodes_1[i], 1) for i in range(1, 3)]

        self.test_supernodes_2 = [Supernode(i, 2) for i in range(2)]
        self.test_superedges_2 = \
            [Superedge(self.test_supernodes_2[0], self.test_supernodes_2[1])]

    def test_add_node_to_supernode(self):
        for i in range(4):
            self.test_supernodes_1[0].add_node(self.test_supernodes_0[i])

        self.assertEqual(0, len(self.test_supernodes_0[0].dec.nodes()))
        self.assertEqual(4, len(self.test_supernodes_1[0].dec.nodes()))
        self.assertEqual(set(self.test_supernodes_0[0:4]), self.test_supernodes_1[0].dec.nodes())

    def test_add_node_to_supernode_error(self):
        self.assertRaises(ValueError, self.test_supernodes_0[0].add_node, self.test_supernodes_1[0])

    def test_add_edge_to_supernode(self):
        for i in range(8):
            self.test_supernodes_1[0].add_node(self.test_supernodes_0[i])

        for i in range(7):
            self.test_supernodes_1[0].add_edge(self.test_superedges_0[i])

        self.assertEqual(8, len(self.test_supernodes_1[0].dec.nodes()))
        self.assertEqual(7, len(self.test_supernodes_1[0].dec.edges()))
        self.assertEqual(set(self.test_superedges_0[0:7]), self.test_supernodes_1[0].dec.edges())

    def test_remove_node_from_supernode(self):
        for i in range(4):
            self.test_supernodes_1[0].add_node(self.test_supernodes_0[i])

        self.test_supernodes_1[0].remove_node(self.test_supernodes_0[0])
        self.assertEqual(3, len(self.test_supernodes_1[0].dec.nodes()))
        self.assertEqual(set(self.test_supernodes_0[1:4]), self.test_supernodes_1[0].dec.nodes())

    def test_remove_edge_from_supernode(self):
        for i in range(8):
            self.test_supernodes_1[0].add_node(self.test_supernodes_0[i])

        for i in range(7):
            self.test_supernodes_1[0].add_edge(self.test_superedges_0[i])

        self.test_supernodes_1[0].remove_edge(self.test_superedges_0[0])
        self.test_supernodes_1[0].remove_edge(self.test_superedges_0[1])
        self.assertEqual(5, len(self.test_supernodes_1[0].dec.edges()))
        self.assertEqual(set(self.test_superedges_0[2:7]), self.test_supernodes_1[0].dec.edges())

    def test_supernode_height(self):
        self.assertEqual(0, self.test_supernodes_0[0].height())
        self.assertEqual(0, self.test_supernodes_1[0].height())

        self.test_supernodes_1[0].add_node(self.test_supernodes_0[0])
        self.assertEqual(1, self.test_supernodes_1[0].height())

    def test_add_edge_to_superedge(self):
        for i in range(4):
            self.test_supernodes_1[0].add_node(self.test_supernodes_0[i])

        for i in range(4, 7):
            self.test_supernodes_1[1].add_node(self.test_supernodes_0[i])

        for i in range(3, 6):
            self.test_superedges_1[0].add_edge(self.test_superedges_0[i])

        self.assertEqual(3, len(self.test_superedges_1[0].dec))
        self.assertEqual(set(self.test_superedges_0[3:6]), self.test_superedges_1[0].dec)

    def test_add_edge_to_superedge_error(self):
        for i in range(4):
            self.test_supernodes_1[0].add_node(self.test_supernodes_0[i])

        for i in range(4, 6):
            self.test_supernodes_1[1].add_node(self.test_supernodes_0[i])

        for i in range(3, 5):
            self.test_superedges_1[0].add_edge(self.test_superedges_0[i])

        self.assertRaises(ValueError, self.test_superedges_1[0].add_edge, self.test_superedges_0[0])
        self.assertRaises(ValueError, self.test_superedges_1[0].add_edge, self.test_superedges_0[6])

    def test_remove_edge_from_superedge(self):
        for i in range(4):
            self.test_supernodes_1[0].add_node(self.test_supernodes_0[i])

        for i in range(4, 7):
            self.test_supernodes_1[1].add_node(self.test_supernodes_0[i])

        for i in range(3, 6):
            self.test_superedges_1[0].add_edge(self.test_superedges_0[i])

        self.test_superedges_1[0].remove_edge(self.test_superedges_0[3])
        self.assertEqual(2, len(self.test_superedges_1[0].dec))
        self.assertEqual(set(self.test_superedges_0[4:6]), self.test_superedges_1[0].dec)

    def test_superedge_height(self):
        self.assertEqual(0, self.test_superedges_0[0].height())
        self.assertEqual(0, self.test_superedges_1[0].height())

        self.test_supernodes_1[0].add_node(self.test_supernodes_0[0])
        self.test_supernodes_1[1].add_node(self.test_supernodes_0[1])
        self.test_superedges_1[0].add_edge(self.test_superedges_0[0])

        self.assertEqual(0, self.test_superedges_0[0].height())
        self.assertEqual(1, self.test_superedges_1[0].height())

    def test_add_edge_to_dec_graph(self):
        dec_graph = DecGraph()
        dec_graph.add_node(self.test_supernodes_0[0])
        dec_graph.add_node(self.test_supernodes_0[1])
        dec_graph.add_edge(self.test_superedges_0[0])

        self.assertEqual(1, len(dec_graph.edges()))
        self.assertEqual(set(self.test_superedges_0[0:1]), dec_graph.edges())

    def test_add_edge_to_dec_graph_error(self):
        dec_graph = DecGraph()
        dec_graph.add_node(self.test_supernodes_0[0])
        dec_graph.add_node(self.test_supernodes_0[1])
        dec_graph.add_edge(self.test_superedges_0[0])

        self.assertRaises(ValueError, dec_graph.add_edge, self.test_superedges_0[1])

    def test_graph(self):
        dec_graph = DecGraph()
        dec_graph.add_node(self.test_supernodes_0[0])
        dec_graph.add_node(self.test_supernodes_0[1])
        dec_graph.add_edge(self.test_superedges_0[0])

        nx_graph = dec_graph.graph()
        self.assertEqual(2, nx_graph.number_of_nodes())
        self.assertEqual([0, 1], [n for n in nx_graph.nodes()])
        self.assertEqual(1, nx_graph.number_of_edges())
        self.assertEqual([(0, 1)], [e for e in nx_graph.edges()])

    def test_graph_with_attr(self):
        dec_graph = DecGraph()
        dec_graph.add_node(self.test_supernodes_0[0])
        dec_graph.add_node(self.test_supernodes_0[1])
        dec_graph.add_edge(self.test_superedges_0[0])

        self.test_supernodes_0[0]['label'] = "label0"
        self.test_supernodes_0[1]['label'] = "label1"
        self.test_superedges_0[0]['label'] = "label0"

        nx_graph = dec_graph.graph(attr=True)

        self.assertEqual("label0", nx_graph.nodes[0]['label'])
        self.assertEqual("label1", nx_graph.nodes[1]['label'])
        self.assertEqual("label0", nx_graph.edges[(0, 1)]['label'])

    def test_induced_subgraph_1(self):
        dec_graph = DecGraph()
        dec_graph.add_node(self.test_supernodes_0[0])
        dec_graph.add_node(self.test_supernodes_0[1])
        dec_graph.add_node(self.test_supernodes_0[2])
        dec_graph.add_edge(self.test_superedges_0[0])
        dec_graph.add_edge(self.test_superedges_0[1])

        induced_subgraph = dec_graph.induced_subgraph(self.test_supernodes_0[0:2])
        self.assertEqual(2, len(induced_subgraph.nodes()))
        self.assertEqual(set(self.test_supernodes_0[0:2]), induced_subgraph.nodes())
        self.assertEqual(1, len(induced_subgraph.edges()))
        self.assertEqual({self.test_superedges_0[0]}, induced_subgraph.edges())

    def test_induced_subgraph_2(self):
        dec_graph = DecGraph()
        dec_graph.add_node(self.test_supernodes_0[0])
        dec_graph.add_node(self.test_supernodes_0[1])
        dec_graph.add_node(self.test_supernodes_0[2])
        dec_graph.add_edge(self.test_superedges_0[0])
        dec_graph.add_edge(self.test_superedges_0[1])

        induced_subgraph = dec_graph.induced_subgraph(self.test_supernodes_0[1:5])
        self.assertEqual(2, len(induced_subgraph.nodes()))
        self.assertEqual(set(self.test_supernodes_0[1:3]), induced_subgraph.nodes())
        self.assertEqual(0, len(induced_subgraph.edges()))

    def test_dec_graph_with_height_2(self):
        dec_graph = self._build_test_graph_1()
        self.assertEqual(2, dec_graph.height())

    def test_complete_decontraction(self):
        dec_graph = self._build_test_graph_1()
        dec_graph_decontraction = dec_graph.complete_decontraction()
        self.assertEqual(3, len(dec_graph_decontraction.nodes()))
        self.assertEqual(1, len(dec_graph_decontraction.edges()))

        expected_decontraction = DecGraph()
        for i in range(3):
            expected_decontraction.add_node(self.test_supernodes_1[i])
        expected_decontraction.add_edge(self.test_superedges_1[0])

        self.assertTrue(expected_decontraction == dec_graph_decontraction)

    def test_deepcopy(self):
        dec_graph = self._build_test_graph_1()
        dec_graph_copy = dec_graph.deepcopy()
        self.assertEqual(dec_graph, dec_graph_copy)
        self.assertNotEqual(id(dec_graph), id(dec_graph_copy))
        self.assertNotEqual(id(dec_graph.V), id(dec_graph_copy.V))
        self.assertNotEqual(id(dec_graph.E), id(dec_graph_copy.E))
        self.assertEqual(dec_graph.V[0], dec_graph_copy.V[0])
        self.assertNotEqual(id(dec_graph.V[0]), id(dec_graph_copy.V[0]))
        self.assertEqual(dec_graph.E[(0, 1)], dec_graph_copy.E[(0, 1)])
        self.assertNotEqual(id(dec_graph.E[(0, 1)]), id(dec_graph_copy.E[(0, 1)]))

    def test_in_edges(self):
        dec_graph = self._build_test_graph_1()
        self.assertEqual(0, len(dec_graph.in_edges(self.test_supernodes_2[0])))
        self.assertEqual(1, len(dec_graph.in_edges(self.test_supernodes_2[1])))
        self.assertEqual({self.test_superedges_2[0]}, dec_graph.in_edges(self.test_supernodes_2[1]))

    def test_out_edges(self):
        dec_graph = self._build_test_graph_1()
        self.assertEqual(1, len(dec_graph.out_edges(self.test_supernodes_2[0])))
        self.assertEqual(0, len(dec_graph.out_edges(self.test_supernodes_2[1])))
        self.assertEqual({self.test_superedges_2[0]}, dec_graph.out_edges(self.test_supernodes_2[0]))

    def _build_test_graph_1(self) -> DecGraph:
        for i in range(3):
            self.test_supernodes_1[i].add_node(self.test_supernodes_0[2 * i])
            self.test_supernodes_1[i].add_node(self.test_supernodes_0[2 * i + 1])

        self.test_supernodes_2[0].add_node(self.test_supernodes_1[0])
        self.test_supernodes_2[1].add_node(self.test_supernodes_1[1])
        self.test_supernodes_2[1].add_node(self.test_supernodes_1[2])

        self.test_superedges_1[0].add_edge(self.test_superedges_0[1])
        self.test_superedges_1[0].add_edge(self.test_superedges_0[2])
        self.test_superedges_2[0].add_edge(self.test_superedges_1[0])

        dec_graph = DecGraph()
        for i in range(2):
            dec_graph.add_node(self.test_supernodes_2[i])
        dec_graph.add_edge(self.test_superedges_2[0])

        return dec_graph

    # TODO: Testare in_edges e out_edges


if __name__ == '__main__':
    unittest.main()

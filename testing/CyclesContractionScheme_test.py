import unittest

from multilevel_graphs import DecGraph, Supernode, Superedge, CyclesContractionScheme


class CycleContractionSchemeTest(unittest.TestCase):

    @staticmethod
    def _sample_dec_graph() -> DecGraph:
        graph = DecGraph()
        graph.add_node(Supernode(1, level=0, weight=30))
        graph.add_node(Supernode(2, level=0, weight=20))
        graph.add_node(Supernode(3, level=0, weight=10))
        graph.add_node(Supernode(4, level=0, weight=15))
        graph.add_node(Supernode(5, level=0, weight=15))
        graph.add_edge(Superedge(graph.V[1], graph.V[2], weight=5))
        graph.add_edge(Superedge(graph.V[2], graph.V[3], weight=10))
        graph.add_edge(Superedge(graph.V[3], graph.V[1], weight=20))
        graph.add_edge(Superedge(graph.V[2], graph.V[4], weight=10))
        graph.add_edge(Superedge(graph.V[4], graph.V[3], weight=5))
        graph.add_edge(Superedge(graph.V[3], graph.V[5], weight=10))
        graph.add_edge(Superedge(graph.V[5], graph.V[4], weight=10))
        return graph

    def test_contract(self):
        sample_graph = self._sample_dec_graph()
        contracted_graph = CyclesContractionScheme(maximal=False).contract(sample_graph)

        self.assertEqual(4, len(contracted_graph.V))
        self.assertEqual(6, len(contracted_graph.E))
        self.assertEqual(2, len(sample_graph.V[1].supernode.dec.nodes()))
        self.assertEqual(sample_graph.V[1].supernode, sample_graph.V[2].supernode)
        self.assertEqual(1, len(sample_graph.V[3].supernode.dec.nodes()))
        self.assertEqual(3, len(sample_graph.V[3].supernode.component_sets))
        self.assertEqual(2, len(sample_graph.V[4].supernode.component_sets))
        self.assertEqual(1, len(sample_graph.V[5].supernode.component_sets))
        self.assertEqual(sample_graph, contracted_graph.complete_decontraction())


if __name__ == '__main__':
    unittest.main()

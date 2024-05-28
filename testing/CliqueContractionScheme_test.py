import unittest

from multilevel_graphs import DecGraph, Supernode, Superedge, SccsContractionScheme

class CliqueContractionSchemeTest(unittest.TestCase):
    
    def test_contract(self):
        dec_graph = self._sample_dec_graph()
        contracted_graph = SccsContractionScheme().contract(dec_graph)
        self.assertEqual(len(dec_graph.V), 
                            len(contracted_graph.nodes()))
        self.assertEqual(len(dec_graph.E),
                            len(contracted_graph.edges()))
        self.assertEqual(dec_graph, contracted_graph.complete_decontraction())
        
        
        pass

    @staticmethod
    def _sample_dec_graph() -> DecGraph:
        graph = DecGraph()

        graph.add_node(Supernode(1, level=0, weight=30))
        graph.add_node(Supernode(2, level=0, weight=20))
        graph.add_node(Supernode(3, level=0, weight=10))
        graph.add_node(Supernode(4, level=0, weight=15))
        graph.add_node(Supernode(5, level=0, weight=15))
        graph.add_node(Supernode(6, level=0, weight=15))
        graph.add_node(Supernode(7, level=0, weight=15))
        graph.add_node(Supernode(8, level=0, weight=15))
        graph.add_node(Supernode(9, level=0, weight=15))

        graph.add_edge(Superedge(graph.V[1], graph.V[2], weight=5))
        graph.add_edge(Superedge(graph.V[2], graph.V[1], weight=5))
        graph.add_edge(Superedge(graph.V[2], graph.V[3], weight=5))
        graph.add_edge(Superedge(graph.V[3], graph.V[2], weight=10))
        graph.add_edge(Superedge(graph.V[2], graph.V[5], weight=5))
        graph.add_edge(Superedge(graph.V[5], graph.V[2], weight=5))
        graph.add_edge(Superedge(graph.V[2], graph.V[6], weight=5))
        graph.add_edge(Superedge(graph.V[6], graph.V[2], weight=5))
        graph.add_edge(Superedge(graph.V[3], graph.V[4], weight=5))
        graph.add_edge(Superedge(graph.V[4], graph.V[3], weight=5))
        graph.add_edge(Superedge(graph.V[4], graph.V[5], weight=5))

        graph.add_edge(Superedge(graph.V[1], graph.V[3], weight=5))
        graph.add_edge(Superedge(graph.V[3], graph.V[1], weight=5))
        graph.add_edge(Superedge(graph.V[4], graph.V[6], weight=5))
        graph.add_edge(Superedge(graph.V[6], graph.V[4], weight=5))
        graph.add_edge(Superedge(graph.V[3], graph.V[5], weight=5))
        graph.add_edge(Superedge(graph.V[5], graph.V[3], weight=5))
        graph.add_edge(Superedge(graph.V[5], graph.V[6], weight=5))
        graph.add_edge(Superedge(graph.V[6], graph.V[5], weight=5))


        return graph
import unittest

from multilevelgraphs import DecGraph, Supernode, Superedge, StarsContractionScheme
from multilevelgraphs.contraction_schemes import UpdateQuadruple


class StarsContractionSchemeTest(unittest.TestCase):

    @staticmethod
    def _sample_dec_graph() -> DecGraph:
        graph = DecGraph()
        graph.add_node(Supernode(1, level=0, weight=30))
        graph.add_node(Supernode(2, level=0, weight=20))
        graph.add_node(Supernode(3, level=0, weight=10))
        graph.add_node(Supernode(4, level=0, weight=15))
        graph.add_node(Supernode(5, level=0, weight=15))
        graph.add_node(Supernode(6, level=0, weight=25))
        graph.add_node(Supernode(7, level=0, weight=15))
        graph.add_node(Supernode(8, level=0, weight=10))
        graph.add_node(Supernode(9, level=0, weight=15))
        graph.add_edge(Superedge(graph.V[1], graph.V[3], weight=5))
        graph.add_edge(Superedge(graph.V[2], graph.V[1], weight=10))
        graph.add_edge(Superedge(graph.V[3], graph.V[2], weight=20))
        graph.add_edge(Superedge(graph.V[3], graph.V[4], weight=10))
        graph.add_edge(Superedge(graph.V[3], graph.V[5], weight=5))
        graph.add_edge(Superedge(graph.V[5], graph.V[6], weight=10))
        graph.add_edge(Superedge(graph.V[5], graph.V[7], weight=10))
        graph.add_edge(Superedge(graph.V[7], graph.V[5], weight=10))
        graph.add_edge(Superedge(graph.V[8], graph.V[9], weight=10))
        return graph

    def test_contract(self):
        sample_graph = self._sample_dec_graph()
        contracted_graph = StarsContractionScheme().contract(sample_graph)

        self.assertEqual(5, len(contracted_graph.nodes()))
        self.assertEqual(4, len(contracted_graph.edges()))
        self.assertEqual(self._sample_dec_graph(), contracted_graph.complete_decontraction())

        self.assertEqual(sample_graph.V[3].supernode, sample_graph.V[4].supernode)
        self.assertEqual(sample_graph.V[5].supernode, sample_graph.V[7].supernode)
        self.assertEqual(sample_graph.V[8].supernode, sample_graph.V[9].supernode)
        self.assertNotEqual(sample_graph.V[1].supernode, sample_graph.V[2].supernode)
        self.assertNotEqual(sample_graph.V[1].supernode, sample_graph.V[3].supernode)
        self.assertEqual(1, len(sample_graph.V[3].supernode.dec.edges()))
        self.assertEqual(3, len(sample_graph.V[5].supernode.dec.edges()))
        self.assertEqual(1, len(contracted_graph.E[(sample_graph.V[3].supernode.key, sample_graph.V[5].supernode.key)].dec))

    def test_contract_with_supernode_attr_function(self):
        def supernode_attr_function(supernode: Supernode):
            return {"weight": sum([node['weight'] for node in supernode.dec.nodes()]) + 1}

        sample_graph = self._sample_dec_graph()
        contracted_graph = StarsContractionScheme(supernode_attr_function).contract(sample_graph)

        self.assertEqual(self._sample_dec_graph(), contracted_graph.complete_decontraction())
        self.assertEqual(31, sample_graph.V[1].supernode['weight'])
        self.assertEqual(26, sample_graph.V[4].supernode['weight'])
        self.assertEqual(56, sample_graph.V[6].supernode['weight'])

    def test_contract_with_superedge_attr_function(self):
        def supernode_attr_function(supernode: Supernode):
            return {"weight": sum([node['weight'] for node in supernode.dec.nodes()])}

        def superedge_attr_function(superedge: Superedge):
            return {"weight": superedge.tail['weight'] + superedge.head['weight']
                              + sum([edge['weight'] for edge in superedge.dec])}

        sample_graph = self._sample_dec_graph()
        contracted_graph = StarsContractionScheme(supernode_attr_function, superedge_attr_function).contract(sample_graph)

        self.assertEqual(self._sample_dec_graph(), contracted_graph.complete_decontraction())
        self.assertEqual(55, sample_graph.V[5].supernode['weight'])
        self.assertEqual(85, contracted_graph.E[(sample_graph.V[3].supernode.key, sample_graph.V[5].supernode.key)]['weight'])

    def test_contract_with_c_set_attr_function(self):
        def supernode_attr_function(supernode: Supernode):
            return {"weight": sum([node['weight'] for node in supernode.dec.nodes()])}

        def c_set_attr_function(c_set):
            return {"weight": sum([node['weight']+1 for node in c_set])}

        sample_graph = self._sample_dec_graph()
        contracted_graph = StarsContractionScheme(supernode_attr_function=supernode_attr_function,
                                                  c_set_attr_function=c_set_attr_function).contract(sample_graph)

        self.assertEqual(self._sample_dec_graph(), contracted_graph.complete_decontraction())
        self.assertEqual(31, list(sample_graph.V[1].supernode.component_sets)[0]['weight'])
        self.assertEqual(27, list(sample_graph.V[8].supernode.component_sets)[0]['weight'])
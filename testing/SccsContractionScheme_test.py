import unittest

from multilevel_graphs import DecGraph, Supernode, Superedge, SccsContractionScheme
from multilevel_graphs.contraction_schemes import UpdateQuadruple


class MyTestCase(unittest.TestCase):

    def test_contract(self):
        sample_graph = self._sample_dec_graph()
        contracted_graph = SccsContractionScheme().contract(sample_graph)

        self.assertEqual(2, len(contracted_graph.nodes()))
        self.assertEqual(1, len(contracted_graph.edges()))
        self.assertEqual(self._sample_dec_graph(), contracted_graph.complete_decontraction())

        self.assertEqual(sample_graph.V[1].supernode, sample_graph.V[2].supernode)
        self.assertEqual(sample_graph.V[1].supernode, sample_graph.V[3].supernode)
        self.assertEqual(sample_graph.V[4].supernode, sample_graph.V[5].supernode)
        self.assertEqual(3, len(sample_graph.V[1].supernode.dec.edges()))
        self.assertEqual(2, len(sample_graph.V[4].supernode.dec.edges()))
        self.assertEqual(1, len(contracted_graph.E[(sample_graph.V[1].supernode.key, sample_graph.V[4].supernode.key)].dec))

    def test_contract_with_supernode_attr_function(self):
        def supernode_attr_function(supernode: Supernode):
            return {"weight": sum([node['weight'] for node in supernode.dec.nodes()]) + 1}

        sample_graph = self._sample_dec_graph()
        contracted_graph = SccsContractionScheme(supernode_attr_function).contract(sample_graph)

        self.assertEqual(self._sample_dec_graph(), contracted_graph.complete_decontraction())
        self.assertEqual(61, sample_graph.V[1].supernode['weight'])
        self.assertEqual(31, sample_graph.V[4].supernode['weight'])

    def test_contract_with_superedge_attr_function(self):
        def supernode_attr_function(supernode: Supernode):
            return {"weight": sum([node['weight'] for node in supernode.dec.nodes()])}

        def superedge_attr_function(superedge: Superedge):
            return {"weight": superedge.tail['weight'] + superedge.head['weight']
                              + sum([edge['weight'] for edge in superedge.dec])}

        sample_graph = self._sample_dec_graph()
        contracted_graph = SccsContractionScheme(supernode_attr_function, superedge_attr_function).contract(sample_graph)

        self.assertEqual(self._sample_dec_graph(), contracted_graph.complete_decontraction())
        self.assertEqual(60, sample_graph.V[1].supernode['weight'])
        self.assertEqual(100, contracted_graph.E[(sample_graph.V[1].supernode.key, sample_graph.V[4].supernode.key)]['weight'])

    def test_contract_with_c_set_attr_function(self):
        def supernode_attr_function(supernode: Supernode):
            return {"weight": sum([node['weight'] for node in supernode.dec.nodes()])}

        def c_set_attr_function(c_set):
            return {"weight": sum([node['weight']+1 for node in c_set])}

        sample_graph = self._sample_dec_graph()
        contracted_graph = SccsContractionScheme(supernode_attr_function=supernode_attr_function,
                                                 c_set_attr_function=c_set_attr_function).contract(sample_graph)

        self.assertEqual(self._sample_dec_graph(), contracted_graph.complete_decontraction())
        self.assertEqual(63, list(sample_graph.V[1].supernode.component_sets)[0]['weight'])
        self.assertEqual(32, list(sample_graph.V[4].supernode.component_sets)[0]['weight'])

    def test_update_added_node(self):
        sample_graph = self._sample_dec_graph()
        scheme = SccsContractionScheme()
        scheme.contract(sample_graph)

        new_node = Supernode(6, level=0, weight=10)
        sample_graph.add_node(new_node)
        quadruple = UpdateQuadruple(v_plus={new_node}, v_minus=set(), e_plus=set(), e_minus=set())
        scheme.update(quadruple)

        self.assertEqual(3, len(scheme.dec_graph.V))
        self.assertEqual(1, len(scheme.dec_graph.E))
        self.assertEqual(1, len(sample_graph.V[6].supernode.dec.nodes()))
        self.assertEqual(0, len(sample_graph.V[6].supernode.dec.edges()))
        self.assertEqual(0, len(scheme.dec_graph.in_edges(sample_graph.V[6].supernode)))
        self.assertEqual(0, len(scheme.dec_graph.out_edges(sample_graph.V[6].supernode)))

    def test_update_added_edge_1(self):
        sample_graph = self._sample_dec_graph()
        scheme = SccsContractionScheme()
        scheme.contract(sample_graph)

        new_edge = Superedge(sample_graph.V[1], sample_graph.V[5], weight=5)
        sample_graph.add_edge(new_edge)
        quadruple = UpdateQuadruple(v_plus=set(), v_minus=set(), e_plus={new_edge}, e_minus=set())
        scheme.update(quadruple)

        self.assertEqual(2, len(scheme.dec_graph.V))
        self.assertEqual(1, len(scheme.dec_graph.E))
        self.assertEqual(3, len(sample_graph.V[1].supernode.dec.edges()))
        self.assertEqual(2, len(sample_graph.V[4].supernode.dec.edges()))

        superedge_between_scc = scheme.dec_graph.E[(sample_graph.V[1].supernode.key, sample_graph.V[4].supernode.key)]
        self.assertEqual(2, len(superedge_between_scc.dec))
        self.assertEqual({sample_graph.E[(1, 4)], sample_graph.E[(1, 5)]}, superedge_between_scc.dec)

    def test_update_added_edge_2(self):
        sample_graph = self._sample_dec_graph()
        scheme = SccsContractionScheme()
        scheme.contract(sample_graph)

        new_edge = Superedge(sample_graph.V[5], sample_graph.V[2], weight=10)
        sample_graph.add_edge(new_edge)
        quadruple = UpdateQuadruple(v_plus=set(), v_minus=set(), e_plus={new_edge}, e_minus=set())
        scheme.update(quadruple)

        self.assertEqual(1, len(scheme.dec_graph.V))
        self.assertEqual(0, len(scheme.dec_graph.E))

        self.assertEqual(sample_graph, scheme.dec_graph.complete_decontraction())
        self.assertEqual(7, len(sample_graph.V[5].supernode.dec.edges()))
        self.assertEqual(sample_graph, sample_graph.V[5].supernode.dec)

    def test_update_added_node_and_edge(self):
        sample_graph = self._sample_dec_graph()
        scheme = SccsContractionScheme()
        scheme.contract(sample_graph)

        new_node_1 = Supernode(6, level=0, weight=10)
        sample_graph.add_node(new_node_1)
        new_node_2 = Supernode(7, level=0, weight=10)
        sample_graph.add_node(new_node_2)
        new_edge_1 = Superedge(sample_graph.V[1], sample_graph.V[5], weight=5)
        sample_graph.add_edge(new_edge_1)
        new_edge_2 = Superedge(sample_graph.V[3], sample_graph.V[6], weight=5)
        sample_graph.add_edge(new_edge_2)
        new_edge_3 = Superedge(sample_graph.V[6], sample_graph.V[7], weight=5)
        sample_graph.add_edge(new_edge_3)
        quadruple = UpdateQuadruple(v_plus={new_node_1, new_node_2}, v_minus=set(),
                                    e_plus={new_edge_1, new_edge_2, new_edge_3}, e_minus=set())
        scheme.update(quadruple)

        self.assertEqual(4, len(scheme.dec_graph.V))
        self.assertEqual(3, len(scheme.dec_graph.E))
        self.assertEqual(1, len(sample_graph.V[6].supernode.dec.nodes()))
        self.assertEqual(1, len(sample_graph.V[7].supernode.dec.nodes()))
        self.assertEqual(sample_graph, scheme.dec_graph.complete_decontraction())

        self.assertEqual({(sample_graph.V[6].supernode.key, sample_graph.V[7].supernode.key),
                          (sample_graph.V[1].supernode.key, sample_graph.V[5].supernode.key),
                          (sample_graph.V[3].supernode.key, sample_graph.V[6].supernode.key)},
                         set(scheme.dec_graph.E.keys()))
        self.assertEqual(1, len(scheme.dec_graph.E[(sample_graph.V[3].supernode.key, sample_graph.V[6].supernode.key)].dec))
        self.assertEqual(2, len(scheme.dec_graph.E[(sample_graph.V[1].supernode.key, sample_graph.V[5].supernode.key)].dec))
        self.assertEqual(1, len(scheme.dec_graph.E[(sample_graph.V[6].supernode.key, sample_graph.V[7].supernode.key)].dec))

    def test_update_removed_node(self):
        sample_graph = self._sample_dec_graph()
        sample_graph.add_node(Supernode(6, level=0, weight=10))
        scheme = SccsContractionScheme()
        scheme.contract(sample_graph)

        removed_node = sample_graph.V[6]
        sample_graph.remove_node(removed_node)
        quadruple = UpdateQuadruple(v_plus=set(), v_minus={removed_node}, e_plus=set(), e_minus=set())

        scheme.update(quadruple)

        self.assertEqual(2, len(scheme.dec_graph.V))
        self.assertEqual(1, len(scheme.dec_graph.E))
        self.assertEqual(sample_graph.V[1].supernode, sample_graph.V[2].supernode)
        self.assertEqual(sample_graph.V[1].supernode, sample_graph.V[3].supernode)
        self.assertEqual(sample_graph.V[4].supernode, sample_graph.V[5].supernode)
        self.assertEqual(3, len(sample_graph.V[1].supernode.dec.edges()))
        self.assertEqual(2, len(sample_graph.V[4].supernode.dec.edges()))
        self.assertEqual(1, len(scheme.dec_graph.E[(sample_graph.V[1].supernode.key, sample_graph.V[4].supernode.key)].dec))

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
        graph.add_edge(Superedge(graph.V[1], graph.V[4], weight=10))
        graph.add_edge(Superedge(graph.V[4], graph.V[5], weight=5))
        graph.add_edge(Superedge(graph.V[5], graph.V[4], weight=10))
        return graph


if __name__ == '__main__':
    unittest.main()

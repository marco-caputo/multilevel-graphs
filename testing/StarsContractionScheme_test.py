import unittest

from multilevelgraphs import DecGraph, Supernode, Superedge, StarsContractionScheme
from src.multilevelgraphs.contraction_schemes import UpdateQuadruple


class StarsContractionSchemeTest(unittest.TestCase):

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

    def test_update_added_node(self):
        sample_graph = self._sample_dec_graph()
        scheme = StarsContractionScheme(reciprocal=False)
        scheme.contract(sample_graph)

        new_node = Supernode(10, level=0, weight=10)
        sample_graph.add_node(new_node)
        quadruple = UpdateQuadruple(v_plus={new_node}, v_minus=set(), e_plus=set(), e_minus=set())
        scheme.update(quadruple)

        self.assertEqual(6, len(scheme.dec_graph.V))
        self.assertEqual(4, len(scheme.dec_graph.E))
        self.assertEqual(sample_graph, scheme.dec_graph.complete_decontraction())
        self.assertEqual(1, len(sample_graph.V[10].supernode.dec.nodes()))
        self.assertEqual(set(), set.union(scheme.dec_graph.in_edges(sample_graph.V[10].supernode)),
                         scheme.dec_graph.out_edges(sample_graph.V[10].supernode))

    def test_update_added_edge(self):
        sample_graph = self._sample_dec_graph()
        scheme = StarsContractionScheme(reciprocal=False)
        scheme.contract(sample_graph)

        new_edge = Superedge(sample_graph.V[4], sample_graph.V[5], weight=10)
        sample_graph.add_edge(new_edge)
        quadruple = UpdateQuadruple(v_plus=set(), v_minus=set(), e_plus={new_edge}, e_minus=set())
        scheme.update(quadruple)

        self.assertEqual(6, len(scheme.dec_graph.V))
        self.assertEqual(6, len(scheme.dec_graph.E))
        self.assertEqual(3, len(sample_graph.V[5].supernode.dec.nodes()))
        self.assertEqual(3, len(sample_graph.V[7].supernode.dec.edges()))
        self.assertEqual(sample_graph.V[6].supernode, sample_graph.V[5].supernode)
        self.assertNotEqual(sample_graph.V[4].supernode, sample_graph.V[3].supernode)
        for i in range(1,10):
            self.assertEqual(1, len(sample_graph.V[i].supernode.component_sets))
        self.assertEqual(sample_graph, scheme.dec_graph.complete_decontraction())

    def test_update_added_edge_2(self):
        sample_graph = self._sample_dec_graph()
        scheme = StarsContractionScheme(reciprocal=False)
        scheme.contract(sample_graph)

        new_edge = Superedge(sample_graph.V[6], sample_graph.V[8], weight=10)
        sample_graph.add_edge(new_edge)
        quadruple = UpdateQuadruple(v_plus=set(), v_minus=set(), e_plus={new_edge}, e_minus=set())
        scheme.update(quadruple)

        self.assertEqual(6, len(scheme.dec_graph.V))
        self.assertEqual(6, len(scheme.dec_graph.E))
        self.assertEqual(2, len(sample_graph.V[8].supernode.dec.nodes()))
        self.assertEqual(1, len(sample_graph.V[8].supernode.dec.edges()))
        self.assertEqual(1, len(sample_graph.V[6].supernode.dec.nodes()))
        self.assertEqual(sample_graph.V[9].supernode, sample_graph.V[8].supernode)
        self.assertNotEqual(sample_graph.V[6].supernode, sample_graph.V[5].supernode)
        for i in range(1,10):
            self.assertEqual(1, len(sample_graph.V[i].supernode.component_sets))
        self.assertEqual(sample_graph, scheme.dec_graph.complete_decontraction())

    def test_update_added_edge_3(self):
        sample_graph = self._sample_dec_graph()
        sample_graph.add_node(Supernode(10, level=0, weight=10))
        sample_graph.add_node(Supernode(11, level=0, weight=10))
        sample_graph.add_edge(Superedge(sample_graph.V[9], sample_graph.V[10], weight=10))
        scheme = StarsContractionScheme(reciprocal=False)
        scheme.contract(sample_graph)

        self.assertEqual(6, len(scheme.dec_graph.V))
        self.assertEqual(4, len(scheme.dec_graph.E))
        self.assertEqual(3, len(sample_graph.V[8].supernode.dec.nodes()))
        self.assertEqual(1, len(sample_graph.V[11].supernode.dec.nodes()))
        self.assertEqual(sample_graph.V[8].supernode, sample_graph.V[10].supernode)

        new_edge = Superedge(sample_graph.V[10], sample_graph.V[11], weight=10)
        sample_graph.add_edge(new_edge)
        quadruple = UpdateQuadruple(v_plus=set(), v_minus=set(), e_plus={new_edge}, e_minus=set())
        scheme.update(quadruple)

        self.assertEqual(6, len(scheme.dec_graph.V))
        self.assertEqual(5, len(scheme.dec_graph.E))
        self.assertEqual(2, len(sample_graph.V[8].supernode.dec.nodes()))
        self.assertEqual(2, len(sample_graph.V[10].supernode.dec.nodes()))
        self.assertEqual(1, len(sample_graph.V[10].supernode.dec.edges()))
        self.assertEqual(sample_graph.V[8].supernode, sample_graph.V[9].supernode)
        self.assertNotEqual(sample_graph.V[9].supernode, sample_graph.V[10].supernode)
        for i in range(1,10):
            self.assertEqual(1, len(sample_graph.V[i].supernode.component_sets))
        self.assertEqual(sample_graph, scheme.dec_graph.complete_decontraction())

    def test_update_added_node_and_edge(self):
        sample_graph = self._sample_dec_graph()
        scheme = StarsContractionScheme(reciprocal=False)
        scheme.contract(sample_graph)

        new_node = Supernode(10, level=0, weight=10)
        sample_graph.add_node(new_node)
        new_edge_1 = Superedge(sample_graph.V[1], sample_graph.V[10], weight=5)
        sample_graph.add_edge(new_edge_1)
        new_edge_2 = Superedge(sample_graph.V[6], sample_graph.V[7], weight=5)
        sample_graph.add_edge(new_edge_2)
        quadruple = UpdateQuadruple(v_plus={new_node}, v_minus=set(), e_plus={new_edge_1, new_edge_2}, e_minus=set())
        scheme.update(quadruple)

        self.assertEqual(7, len(scheme.dec_graph.V))
        self.assertEqual(8, len(scheme.dec_graph.E))
        self.assertEqual(2, len(sample_graph.V[10].supernode.dec.nodes()))
        self.assertEqual(1, len(sample_graph.V[5].supernode.dec.nodes()))
        self.assertEqual(0, len(sample_graph.V[7].supernode.dec.edges()))
        self.assertEqual(sample_graph.V[1].supernode, sample_graph.V[10].supernode)
        self.assertNotEqual(sample_graph.V[6].supernode, sample_graph.V[7].supernode)
        for i in range(1,10):
            self.assertEqual(1, len(sample_graph.V[i].supernode.component_sets))
        self.assertEqual(sample_graph, scheme.dec_graph.complete_decontraction())


    def test_update_remove_node(self):
        sample_graph = self._sample_dec_graph()
        sample_graph.add_node(Supernode(10, level=0, weight=10))
        scheme = StarsContractionScheme(reciprocal=False)
        scheme.contract(sample_graph)

        removed_node = sample_graph.V[10]
        sample_graph.remove_node(removed_node)
        quadruple = UpdateQuadruple(v_plus=set(), v_minus={removed_node}, e_plus=set(), e_minus=set())
        scheme.update(quadruple)

        self.assertEqual(5, len(scheme.dec_graph.nodes()))
        self.assertEqual(4, len(scheme.dec_graph.edges()))
        self.assertEqual(self._sample_dec_graph(), scheme.dec_graph.complete_decontraction())

        self.assertEqual(sample_graph.V[3].supernode, sample_graph.V[4].supernode)
        self.assertEqual(sample_graph.V[5].supernode, sample_graph.V[7].supernode)
        self.assertEqual(sample_graph.V[8].supernode, sample_graph.V[9].supernode)
        self.assertNotEqual(sample_graph.V[1].supernode, sample_graph.V[2].supernode)
        self.assertNotEqual(sample_graph.V[1].supernode, sample_graph.V[3].supernode)
        self.assertEqual(1, len(sample_graph.V[3].supernode.dec.edges()))
        self.assertEqual(3, len(sample_graph.V[5].supernode.dec.edges()))
        self.assertEqual(1, len(
            scheme.dec_graph.E[(sample_graph.V[3].supernode.key, sample_graph.V[5].supernode.key)].dec))

    def test_update_remove_edge(self):
        sample_graph = self._sample_dec_graph()
        scheme = StarsContractionScheme(reciprocal=False)
        scheme.contract(sample_graph)

        removed_edge = Superedge(sample_graph.V[3], sample_graph.V[5], weight=5)
        sample_graph.remove_edge(removed_edge)
        quadruple = UpdateQuadruple(v_plus=set(), v_minus=set(), e_plus=set(), e_minus={removed_edge})
        scheme.update(quadruple)

        self.assertEqual(5, len(scheme.dec_graph.nodes()))
        self.assertEqual(3, len(scheme.dec_graph.edges()))
        self.assertEqual(sample_graph, scheme.dec_graph.complete_decontraction())

        self.assertEqual(sample_graph.V[3].supernode, sample_graph.V[4].supernode)
        self.assertEqual(sample_graph.V[5].supernode, sample_graph.V[7].supernode)
        self.assertEqual(sample_graph.V[8].supernode, sample_graph.V[9].supernode)
        self.assertNotEqual(sample_graph.V[1].supernode, sample_graph.V[2].supernode)
        self.assertNotEqual(sample_graph.V[3].supernode, sample_graph.V[5].supernode)
        self.assertEqual(1, len(sample_graph.V[3].supernode.dec.edges()))
        self.assertEqual(3, len(sample_graph.V[5].supernode.dec.edges()))
        self.assertRaises(KeyError, lambda:
            scheme.dec_graph.E[(sample_graph.V[3].supernode.key, sample_graph.V[5].supernode.key)].dec)

    def test_update_remove_edge_2(self):
        sample_graph = self._sample_dec_graph()
        scheme = StarsContractionScheme(reciprocal=False)
        scheme.contract(sample_graph)

        removed_edge = Superedge(sample_graph.V[2], sample_graph.V[1], weight=10)
        sample_graph.remove_edge(removed_edge)
        quadruple = UpdateQuadruple(v_plus=set(), v_minus=set(), e_plus=set(), e_minus={removed_edge})
        scheme.update(quadruple)

        self.assertEqual(3, len(scheme.dec_graph.nodes()))
        self.assertEqual(1, len(scheme.dec_graph.edges()))
        self.assertEqual(sample_graph, scheme.dec_graph.complete_decontraction())

        self.assertEqual(sample_graph.V[3].supernode, sample_graph.V[1].supernode)
        self.assertEqual(sample_graph.V[1].supernode, sample_graph.V[2].supernode)
        self.assertEqual(sample_graph.V[1].supernode, sample_graph.V[4].supernode)
        self.assertNotEqual(sample_graph.V[2].supernode, sample_graph.V[5].supernode)
        self.assertEqual(4, len(sample_graph.V[4].supernode.dec.nodes()))
        self.assertEqual(3, len(sample_graph.V[3].supernode.dec.edges()))

    def test_update_remove_edge_3(self):
        sample_graph = self._sample_dec_graph()
        sample_graph.add_node(Supernode(10, level=0, weight=10))
        sample_graph.add_node(Supernode(11, level=0, weight=10))
        sample_graph.add_edge(Superedge(sample_graph.V[9], sample_graph.V[10], weight=10))
        sample_graph.add_edge(Superedge(sample_graph.V[10], sample_graph.V[11], weight=10))
        scheme = StarsContractionScheme(reciprocal=False)
        scheme.contract(sample_graph)

        self.assertEqual(6, len(scheme.dec_graph.V))
        self.assertEqual(5, len(scheme.dec_graph.E))
        self.assertEqual(2, len(sample_graph.V[8].supernode.dec.nodes()))
        self.assertEqual(2, len(sample_graph.V[11].supernode.dec.nodes()))
        self.assertNotEqual(sample_graph.V[8].supernode, sample_graph.V[10].supernode)

        removed_edge = Superedge(sample_graph.V[10], sample_graph.V[11], weight=10)
        sample_graph.remove_edge(removed_edge)
        quadruple = UpdateQuadruple(v_plus=set(), v_minus=set(), e_plus=set(), e_minus={removed_edge})
        scheme.update(quadruple)

        self.assertEqual(6, len(scheme.dec_graph.V))
        self.assertEqual(4, len(scheme.dec_graph.E))
        self.assertEqual(3, len(sample_graph.V[8].supernode.dec.nodes()))
        self.assertEqual(1, len(sample_graph.V[11].supernode.dec.nodes()))
        self.assertEqual(sample_graph.V[8].supernode, sample_graph.V[10].supernode)
        self.assertNotEqual(sample_graph.V[10].supernode, sample_graph.V[11].supernode)
        for i in range(1, 10):
            self.assertEqual(1, len(sample_graph.V[i].supernode.component_sets))
        self.assertEqual(sample_graph, scheme.dec_graph.complete_decontraction())

    def test_update_removed_node_and_edge(self):
        sample_graph = self._sample_dec_graph()
        scheme = StarsContractionScheme(reciprocal=False)
        scheme.contract(sample_graph)

        removed_edge_1 = sample_graph.E[(1, 3)]
        sample_graph.remove_edge(removed_edge_1)
        removed_edge_2 = sample_graph.E[(5, 7)]
        sample_graph.remove_edge(removed_edge_2)
        removed_edge_3 = sample_graph.E[(3, 4)]
        sample_graph.remove_edge(removed_edge_3)
        removed_node = sample_graph.V[4]
        sample_graph.remove_node(removed_node)
        quadruple = UpdateQuadruple(v_plus=set(), v_minus={removed_node}, e_plus=set(),
                                    e_minus={removed_edge_1, removed_edge_2, removed_edge_3})
        scheme.update(quadruple)

        self.assertEqual(4, len(scheme.dec_graph.V))
        self.assertEqual(2, len(scheme.dec_graph.E))
        self.assertEqual(sample_graph.V[1].supernode, sample_graph.V[2].supernode)
        self.assertNotEqual(sample_graph.V[3].supernode, sample_graph.V[2].supernode)
        self.assertNotEqual(sample_graph.V[3].supernode, sample_graph.V[5].supernode)
        self.assertEqual(2, len(sample_graph.V[5].supernode.dec.edges()))
        self.assertEqual(1, len(sample_graph.V[3].supernode.dec.nodes()))
        self.assertEqual(4, len(scheme.component_sets_table.get_all_c_sets()))
        self.assertEqual(sample_graph, scheme.dec_graph.complete_decontraction())

    def test_update_added_and_removed_edge(self):
        sample_graph = self._sample_dec_graph()
        scheme = StarsContractionScheme(reciprocal=False)
        scheme.contract(sample_graph)

        new_edge_1 = Superedge(sample_graph.V[6], sample_graph.V[8], weight=5)
        sample_graph.add_edge(new_edge_1)
        new_edge_2 = Superedge(sample_graph.V[3], sample_graph.V[9], weight=10)
        sample_graph.add_edge(new_edge_2)
        removed_edge_1 = sample_graph.E[(8, 9)]
        sample_graph.remove_edge(removed_edge_1)
        quadruple = UpdateQuadruple(v_plus=set(), v_minus=set(), e_plus={new_edge_1, new_edge_2},
                                    e_minus={removed_edge_1})
        scheme.update(quadruple)

        self.assertEqual(5, len(scheme.dec_graph.V))
        self.assertEqual(5, len(scheme.dec_graph.E))
        self.assertEqual(2, len(sample_graph.V[6].supernode.dec.nodes()))
        self.assertEqual(sample_graph.V[8].supernode, sample_graph.V[6].supernode)
        self.assertEqual(3, len(sample_graph.V[3].supernode.dec.nodes()))
        self.assertEqual(sample_graph.V[3].supernode, sample_graph.V[9].supernode)
        self.assertNotEqual(sample_graph.V[8].supernode, sample_graph.V[9].supernode)
        self.assertNotEqual(sample_graph.V[5].supernode, sample_graph.V[6].supernode)
        for i in range(1, 10):
            self.assertEqual(1, len(sample_graph.V[i].supernode.component_sets))
        self.assertEqual(sample_graph, scheme.dec_graph.complete_decontraction())

    def test_update_attr_after_changes(self):
        def supernode_attr_function(supernode: Supernode):
            return {"weight": sum([node['weight'] for node in supernode.dec.nodes()]) + 1}

        def superedge_attr_function(superedge: Superedge):
            return {"weight": max(0, *(edge['weight'] for edge in superedge.dec))}

        def c_set_attr_function(c_set):
            return {"weight": sum([node['weight'] for node in c_set])}

        sample_graph = self._sample_dec_graph()
        scheme = StarsContractionScheme(supernode_attr_function=supernode_attr_function,
                                        superedge_attr_function=superedge_attr_function,
                                        c_set_attr_function=c_set_attr_function,
                                        reciprocal=False)
        scheme.contract(sample_graph)

        new_edge_1 = Superedge(sample_graph.V[6], sample_graph.V[8], weight=5)
        sample_graph.add_edge(new_edge_1)
        new_edge_2 = Superedge(sample_graph.V[3], sample_graph.V[9], weight=10)
        sample_graph.add_edge(new_edge_2)
        removed_edge_1 = sample_graph.E[(8, 9)]
        sample_graph.remove_edge(removed_edge_1)
        quadruple = UpdateQuadruple(v_plus=set(), v_minus=set(), e_plus={new_edge_1, new_edge_2},
                                    e_minus={removed_edge_1})
        scheme.update(quadruple)

        self.assertEqual(31, sample_graph.V[5].supernode['weight'])
        self.assertEqual(31, sample_graph.V[1].supernode['weight'])
        self.assertEqual(10, scheme.dec_graph.E[(sample_graph.V[5].supernode.key, sample_graph.V[6].supernode.key)][
            'weight'])
        self.assertEqual({40}, {c_set['weight'] for c_set in scheme.component_sets_table[sample_graph.V[9]]})
        self.assertEqual({30}, {c_set['weight'] for c_set in sample_graph.V[1].supernode.component_sets})

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

if __name__ == '__main__':
    unittest.main()

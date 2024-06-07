import unittest

from multilevelgraphs import DecGraph, Supernode, Superedge, CliquesContractionScheme
from multilevelgraphs.contraction_schemes import UpdateQuadruple


class CliqueContractionSchemeTest(unittest.TestCase):

    def test_contract_reciprocal(self):
        sample_graph = self._sample_dec_graph_1()
        scheme = CliquesContractionScheme(reciprocal=True)
        scheme.contract(sample_graph)

        self.assertEqual(8, len(scheme.dec_graph.V))
        self.assertEqual(22, len(scheme.dec_graph.E))
        self.assertEqual(7, len(scheme.component_sets_table.get_all_c_sets()))
        self.assertEqual({frozenset({sample_graph.V[1], sample_graph.V[2], sample_graph.V[3]}),
                          frozenset({sample_graph.V[1], sample_graph.V[3], sample_graph.V[5]}),
                          frozenset({sample_graph.V[3], sample_graph.V[4], sample_graph.V[5]})},
                         {frozenset(c_set) for c_set in scheme.component_sets_table[sample_graph.V[3]]})
        self.assertEqual(1, len(scheme.component_sets_table[sample_graph.V[7]]))
        self.assertEqual({sample_graph.V[7]}, next(iter(scheme.component_sets_table[sample_graph.V[7]])))
        self.assertEqual(1, len(scheme.component_sets_table[sample_graph.V[8]]))
        self.assertEqual({sample_graph.V[8]}, next(iter(scheme.component_sets_table[sample_graph.V[8]])))
        self.assertEqual(sample_graph, scheme.dec_graph.complete_decontraction())

    def test_contract_non_reciprocal(self):
        sample_graph = self._sample_dec_graph_2()
        scheme = CliquesContractionScheme(reciprocal=False)
        scheme.contract(sample_graph)

        self.assertEqual(7, len(scheme.dec_graph.V))
        self.assertEqual(7, len(scheme.dec_graph.E))
        self.assertEqual(6, len(scheme.component_sets_table.get_all_c_sets()))
        self.assertEqual({frozenset({sample_graph.V[3], sample_graph.V[5]}),
                          frozenset({sample_graph.V[1], sample_graph.V[2], sample_graph.V[3]}),
                          frozenset({sample_graph.V[3], sample_graph.V[4], sample_graph.V[6], sample_graph.V[7]})},
                         {frozenset(c_set) for c_set in scheme.component_sets_table[sample_graph.V[3]]})
        self.assertEqual(1, len(scheme.component_sets_table[sample_graph.V[9]]))
        self.assertEqual({sample_graph.V[8], sample_graph.V[9], sample_graph.V[10]},
                         next(iter(scheme.component_sets_table[sample_graph.V[9]])))
        self.assertEqual(1, len(scheme.component_sets_table[sample_graph.V[11]]))
        self.assertEqual({sample_graph.V[11]}, next(iter(scheme.component_sets_table[sample_graph.V[11]])))
        self.assertEqual(sample_graph, scheme.dec_graph.complete_decontraction())

    def test_contract_with_supernodes_attr_function(self):
        def supernode_attr_function(supernode: Supernode):
            return {"weight": sum([node['weight'] for node in supernode.dec.nodes()]) + 1}

        sample_graph = self._sample_dec_graph_2()
        scheme = CliquesContractionScheme(reciprocal=False, supernode_attr_function=supernode_attr_function)
        scheme.contract(sample_graph)

        self.assertEqual(sample_graph, scheme.dec_graph.complete_decontraction())
        self.assertEqual(51, sample_graph.V[9].supernode['weight'])
        self.assertEqual(76, sample_graph.V[4].supernode['weight'])
        self.assertEqual(26, sample_graph.V[5].supernode['weight'])

    def test_contract_with_superedges_attr_function(self):
        def supernode_attr_function(supernode: Supernode):
            return {"weight": sum([node['weight'] for node in supernode.dec.nodes()])}

        def superedge_attr_function(superedge: Superedge):
            return {"weight": max(superedge.tail['weight'], superedge.head['weight'],
                                  *[edge['weight'] for edge in superedge.dec])}

        sample_graph = self._sample_dec_graph_2()
        scheme = CliquesContractionScheme(supernode_attr_function=supernode_attr_function,
                                          superedge_attr_function=superedge_attr_function, reciprocal=False)
        contracted_graph = scheme.contract(sample_graph)

        self.assertEqual(sample_graph, contracted_graph.complete_decontraction())
        self.assertEqual(45, contracted_graph.E[(sample_graph.V[3].supernode.key, sample_graph.V[1].supernode.key)][
            'weight'])
        self.assertEqual(25, contracted_graph.E[(sample_graph.V[3].supernode.key, sample_graph.V[5].supernode.key)][
            'weight'])

    def test_contract_with_c_sets_attr_function(self):
        def supernode_attr_function(supernode: Supernode):
            return {"weight": sum([node['weight'] for node in supernode.dec.nodes()])}

        def c_set_attr_function(c_set):
            return {"weight": sum([node['weight'] for node in c_set])}

        sample_graph = self._sample_dec_graph_2()
        scheme = CliquesContractionScheme(supernode_attr_function=supernode_attr_function,
                                          c_set_attr_function=c_set_attr_function, reciprocal=False)
        contracted_graph = scheme.contract(sample_graph)

        self.assertEqual(sample_graph, contracted_graph.complete_decontraction())
        self.assertEqual(60, next(iter((scheme.component_sets_table[sample_graph.V[9]])))['weight'])
        self.assertEqual({60, 95, 45}, {c_set['weight'] for c_set in sample_graph.V[3].supernode.component_sets})

    def test_update_added_node(self):
        sample_graph = self._sample_dec_graph_2()
        scheme = CliquesContractionScheme(reciprocal=False)
        scheme.contract(sample_graph)

        new_node = Supernode(12, level=0, weight=10)
        sample_graph.add_node(new_node)
        quadruple = UpdateQuadruple(v_plus={new_node}, v_minus=set(), e_plus=set(), e_minus=set())
        scheme.update(quadruple)

        self.assertEqual(8, len(scheme.dec_graph.V))
        self.assertEqual(7, len(scheme.dec_graph.E))
        self.assertEqual(7, len(scheme.component_sets_table.get_all_c_sets()))
        self.assertEqual(sample_graph, scheme.dec_graph.complete_decontraction())
        self.assertEqual(1, len(sample_graph.V[12].supernode.dec.nodes()))
        self.assertEqual(set(), set.union(scheme.dec_graph.in_edges(sample_graph.V[12].supernode)),
                         scheme.dec_graph.out_edges(sample_graph.V[12].supernode))

    def test_update_added_edge(self):
        sample_graph = self._sample_dec_graph_2()
        scheme = CliquesContractionScheme(reciprocal=False)
        scheme.contract(sample_graph)

        new_edge = Superedge(sample_graph.V[5], sample_graph.V[10], weight=5)
        sample_graph.add_edge(new_edge)
        quadruple = UpdateQuadruple(v_plus=set(), v_minus=set(), e_plus={new_edge}, e_minus=set())
        scheme.update(quadruple)

        self.assertEqual(7, len(scheme.dec_graph.V))
        self.assertEqual(8, len(scheme.dec_graph.E))
        self.assertEqual(6, len(scheme.component_sets_table.get_all_c_sets()))
        self.assertEqual(2, len(sample_graph.V[10].supernode.dec.nodes()))
        self.assertEqual(1, len(sample_graph.V[10].supernode.dec.edges()))
        self.assertEqual(sample_graph.V[10].supernode, sample_graph.V[8].supernode)
        self.assertEqual(2, len(scheme.dec_graph.E[(sample_graph.V[5].supernode.key, sample_graph.V[10].supernode.key)]))
        self.assertEqual(2, len(scheme.component_sets_table[sample_graph.V[10]]))
        self.assertEqual({frozenset({sample_graph.V[5], sample_graph.V[8], sample_graph.V[10]}),
                         frozenset({sample_graph.V[8], sample_graph.V[9], sample_graph.V[10]})},
                         {frozenset(c_set) for c_set in scheme.component_sets_table[sample_graph.V[10]]})
        self.assertEqual(1, len(sample_graph.V[9].supernode.component_sets))
        self.assertEqual(2, len(sample_graph.V[5].supernode.component_sets))

    def test_update_added_node_and_edge(self):
        sample_graph = self._sample_dec_graph_1()
        scheme = CliquesContractionScheme(reciprocal=True)
        scheme.contract(sample_graph)

        new_node = Supernode(9, level=0, weight=10)
        sample_graph.add_node(new_node)
        new_edge_1 = Superedge(sample_graph.V[9], sample_graph.V[4], weight=5)
        sample_graph.add_edge(new_edge_1)
        new_edge_2 = Superedge(sample_graph.V[4], sample_graph.V[9], weight=5)
        sample_graph.add_edge(new_edge_2)
        new_edge_3 = Superedge(sample_graph.V[7], sample_graph.V[9], weight=5)
        sample_graph.add_edge(new_edge_3)
        new_edge_4 = Superedge(sample_graph.V[9], sample_graph.V[7], weight=5)
        sample_graph.add_edge(new_edge_4)
        new_edge_5 = Superedge(sample_graph.V[7], sample_graph.V[4], weight=5)
        sample_graph.add_edge(new_edge_5)

        quadruple = UpdateQuadruple(v_plus={new_node}, v_minus=set(),
                                    e_plus={new_edge_1, new_edge_2, new_edge_3, new_edge_4, new_edge_5}, e_minus=set())
        scheme.update(quadruple)

        self.assertEqual(8, len(scheme.dec_graph.V))
        self.assertEqual(23, len(scheme.dec_graph.E))
        self.assertEqual(7, len(scheme.component_sets_table.get_all_c_sets()))
        self.assertEqual(sample_graph, scheme.dec_graph.complete_decontraction())
        self.assertEqual(2, len(sample_graph.V[9].supernode.dec.nodes()))
        self.assertEqual(sample_graph.V[9].supernode, sample_graph.V[7].supernode)
        self.assertEqual({sample_graph.E[(4, 7)], sample_graph.E[(4, 9)]},
                         next(iter(scheme.dec_graph.in_edges(sample_graph.V[9].supernode))).dec)
        self.assertEqual({sample_graph.E[(7, 4)], sample_graph.E[(9, 4)]},
                         scheme.dec_graph.E[(sample_graph.V[9].supernode.key, sample_graph.V[4].supernode.key)].dec)
        self.assertEqual(2, len(sample_graph.V[9].supernode.dec.edges()))
        self.assertEqual(1, len(sample_graph.V[4].supernode.dec.nodes()))
        self.assertEqual(3, len(sample_graph.V[4].supernode.component_sets))
        self.assertEqual({frozenset({sample_graph.V[4], sample_graph.V[9], sample_graph.V[7]})},
                         {frozenset(c_set) for c_set in scheme.component_sets_table[sample_graph.V[7]]})
        self.assertEqual(1, len(sample_graph.V[9].supernode.component_sets))

    def test_update_removed_node(self):
        sample_graph = self._sample_dec_graph_2()
        scheme = CliquesContractionScheme(reciprocal=True)
        scheme.contract(sample_graph)

        removed_node = sample_graph.V[11]
        sample_graph.remove_node(removed_node)
        quadruple = UpdateQuadruple(v_plus=set(), v_minus={removed_node}, e_plus=set(), e_minus=set())
        scheme.update(quadruple)

        self.assertEqual(8, len(scheme.dec_graph.V))
        self.assertEqual(11, len(scheme.dec_graph.E))
        self.assertEqual(2, len(sample_graph.V[1].supernode.dec.nodes()))
        self.assertEqual(2, len(sample_graph.V[1].supernode.dec.edges()))
        self.assertEqual(sample_graph.V[1].supernode, sample_graph.V[2].supernode)
        self.assertEqual(2, len(sample_graph.V[5].supernode.dec.nodes()))
        self.assertEqual(2, len(sample_graph.V[5].supernode.dec.edges()))
        self.assertEqual(sample_graph.V[5].supernode, sample_graph.V[8].supernode)
        for i in [3, 4, 6, 7, 9, 10]:
            self.assertEqual(1, len(sample_graph.V[i].supernode))
        self.assertEqual(sample_graph, scheme.dec_graph.complete_decontraction())

    def test_update_removed_edge(self):
        sample_graph = self._sample_dec_graph_2()
        scheme = CliquesContractionScheme(reciprocal=False)
        scheme.contract(sample_graph)

        removed_edge = sample_graph.E[(4, 6)]
        sample_graph.remove_edge(removed_edge)
        quadruple = UpdateQuadruple(v_plus=set(), v_minus={}, e_plus=set(), e_minus={removed_edge})
        scheme.update(quadruple)

        self.assertEqual(9, len(scheme.dec_graph.V))
        self.assertEqual(10, len(scheme.dec_graph.E))
        self.assertEqual(7, len(scheme.component_sets_table.get_all_c_sets()))
        self.assertEqual({frozenset({sample_graph.V[3], sample_graph.V[5]}),
                          frozenset({sample_graph.V[1], sample_graph.V[2], sample_graph.V[3]}),
                          frozenset({sample_graph.V[3], sample_graph.V[6], sample_graph.V[7]}),
                          frozenset({sample_graph.V[3], sample_graph.V[4], sample_graph.V[7]})},
                         {frozenset(c_set) for c_set in scheme.component_sets_table[sample_graph.V[3]]})
        self.assertEqual(1, len(scheme.component_sets_table[sample_graph.V[6]]))
        self.assertNotEqual(sample_graph.V[6].supernode, sample_graph.V[7].supernode)
        self.assertEqual(sample_graph, scheme.dec_graph.complete_decontraction())

    def test_update_removed_node_and_edge(self):
        sample_graph = self._sample_dec_graph_2()
        scheme = CliquesContractionScheme(reciprocal=False)
        scheme.contract(sample_graph)

        removed_edge_1 = sample_graph.E[(4, 7)]
        sample_graph.remove_edge(removed_edge_1)
        removed_edge_2 = sample_graph.E[(4, 6)]
        sample_graph.remove_edge(removed_edge_2)
        removed_edge_3 = sample_graph.E[(3, 4)]
        sample_graph.remove_edge(removed_edge_3)
        removed_node = sample_graph.V[4]
        sample_graph.remove_node(removed_node)
        quadruple = UpdateQuadruple(v_plus=set(), v_minus={removed_node}, e_plus=set(),
                                    e_minus={removed_edge_1, removed_edge_2, removed_edge_3})
        scheme.update(quadruple)

        self.assertEqual(7, len(scheme.dec_graph.V))
        self.assertEqual(6, len(scheme.dec_graph.E))
        self.assertEqual(6, len(scheme.component_sets_table.get_all_c_sets()))
        self.assertEqual({frozenset({sample_graph.V[3], sample_graph.V[5]}),
                          frozenset({sample_graph.V[1], sample_graph.V[2], sample_graph.V[3]}),
                          frozenset({sample_graph.V[3], sample_graph.V[6], sample_graph.V[7]})},
                         {frozenset(c_set) for c_set in scheme.component_sets_table[sample_graph.V[3]]})
        self.assertEqual(1, len(scheme.component_sets_table[sample_graph.V[6]]))
        self.assertEqual(sample_graph.V[6].supernode, sample_graph.V[7].supernode)
        self.assertEqual(sample_graph, scheme.dec_graph.complete_decontraction())

    def test_added_and_removed_edge(self):
        sample_graph = self._sample_dec_graph_2()
        scheme = CliquesContractionScheme(reciprocal=False)
        scheme.contract(sample_graph)

        new_edge = Superedge(sample_graph.V[5], sample_graph.V[4], weight=5)
        sample_graph.add_edge(new_edge)
        removed_edge = sample_graph.E[(6, 3)]
        sample_graph.remove_edge(removed_edge)
        quadruple = UpdateQuadruple(v_plus=set(), v_minus=set(), e_plus={new_edge}, e_minus={removed_edge})
        scheme.update(quadruple)

        self.assertEqual(9, len(scheme.dec_graph.V))
        self.assertEqual(11, len(scheme.dec_graph.E))
        self.assertEqual(7, len(scheme.component_sets_table.get_all_c_sets()))
        self.assertEqual(1, len(sample_graph.V[6].supernode.dec.nodes()))
        self.assertEqual(1, len(sample_graph.V[7].supernode.dec.nodes()))
        self.assertEqual(0, len(sample_graph.V[7].supernode.dec.edges()))
        self.assertNotEqual(sample_graph.V[6].supernode, sample_graph.V[4].supernode)
        self.assertEqual(1, len(scheme.dec_graph.E[(sample_graph.V[7].supernode.key, sample_graph.V[3].supernode.key)]))
        self.assertEqual(3, len(scheme.component_sets_table[sample_graph.V[4]]))
        self.assertEqual({frozenset({sample_graph.V[3], sample_graph.V[5], sample_graph.V[4]}),
                         frozenset({sample_graph.V[3], sample_graph.V[4], sample_graph.V[7]}),
                          frozenset({sample_graph.V[4], sample_graph.V[6], sample_graph.V[7]})},
                         {frozenset(c_set) for c_set in scheme.component_sets_table[sample_graph.V[4]]})
        self.assertEqual(2, len(sample_graph.V[7].supernode.component_sets))
        self.assertEqual(3, len(sample_graph.V[3].supernode.component_sets))
        self.assertEqual(sample_graph, scheme.dec_graph.complete_decontraction())

    def test_update_attr_after_changes(self):
        def supernode_attr_function(supernode: Supernode):
            return {"weight": sum([node['weight'] for node in supernode.dec.nodes()]) + 1}

        def superedge_attr_function(superedge: Superedge):
            return {"weight": max(0, *(edge['weight'] for edge in superedge.dec))}

        def c_set_attr_function(c_set):
            return {"weight": sum([node['weight'] for node in c_set])}

        sample_graph = self._sample_dec_graph_2()
        scheme = CliquesContractionScheme(supernode_attr_function=supernode_attr_function,
                                          superedge_attr_function=superedge_attr_function,
                                          c_set_attr_function=c_set_attr_function, reciprocal=False)
        scheme.contract(sample_graph)

        new_edge = Superedge(sample_graph.V[5], sample_graph.V[4], weight=5)
        sample_graph.add_edge(new_edge)
        removed_edge = sample_graph.E[(6, 3)]
        sample_graph.remove_edge(removed_edge)
        quadruple = UpdateQuadruple(v_plus=set(), v_minus=set(), e_plus={new_edge}, e_minus={removed_edge})
        scheme.update(quadruple)

        self.assertEqual(26, sample_graph.V[6].supernode['weight'])
        self.assertEqual(26, sample_graph.V[7].supernode['weight'])
        self.assertEqual(5, scheme.dec_graph.E[(sample_graph.V[7].supernode.key, sample_graph.V[3].supernode.key)][
            'weight'])
        self.assertEqual(1, len(scheme.dec_graph.E[(sample_graph.V[7].supernode.key, sample_graph.V[3].supernode.key)]))
        self.assertEqual(3, len(scheme.component_sets_table[sample_graph.V[4]]))
        self.assertEqual({70, 75}, {c_set['weight'] for c_set in scheme.component_sets_table[sample_graph.V[4]]})
        self.assertEqual({60, 70}, {c_set['weight'] for c_set in sample_graph.V[3].supernode.component_sets})
        self.assertEqual(sample_graph, scheme.dec_graph.complete_decontraction())

    @staticmethod
    def _sample_dec_graph_1() -> DecGraph:
        graph = DecGraph()

        graph.add_node(Supernode(1, level=0, weight=10))
        graph.add_node(Supernode(2, level=0, weight=30))
        graph.add_node(Supernode(3, level=0, weight=20))
        graph.add_node(Supernode(4, level=0, weight=25))
        graph.add_node(Supernode(5, level=0, weight=25))
        graph.add_node(Supernode(6, level=0, weight=25))
        graph.add_node(Supernode(7, level=0, weight=25))
        graph.add_node(Supernode(8, level=0, weight=25))

        graph.add_edge(Superedge(graph.V[1], graph.V[2], weight=5))
        graph.add_edge(Superedge(graph.V[2], graph.V[1], weight=5))
        graph.add_edge(Superedge(graph.V[1], graph.V[3], weight=5))
        graph.add_edge(Superedge(graph.V[3], graph.V[1], weight=20))
        graph.add_edge(Superedge(graph.V[1], graph.V[5], weight=5))
        graph.add_edge(Superedge(graph.V[5], graph.V[1], weight=5))
        graph.add_edge(Superedge(graph.V[1], graph.V[6], weight=5))
        graph.add_edge(Superedge(graph.V[6], graph.V[1], weight=5))
        graph.add_edge(Superedge(graph.V[3], graph.V[4], weight=5))
        graph.add_edge(Superedge(graph.V[4], graph.V[3], weight=5))
        graph.add_edge(Superedge(graph.V[4], graph.V[5], weight=5))
        graph.add_edge(Superedge(graph.V[5], graph.V[4], weight=5))
        graph.add_edge(Superedge(graph.V[4], graph.V[6], weight=5))
        graph.add_edge(Superedge(graph.V[6], graph.V[4], weight=5))

        graph.add_edge(Superedge(graph.V[2], graph.V[3], weight=5))
        graph.add_edge(Superedge(graph.V[3], graph.V[2], weight=5))
        graph.add_edge(Superedge(graph.V[3], graph.V[5], weight=5))
        graph.add_edge(Superedge(graph.V[5], graph.V[3], weight=5))
        graph.add_edge(Superedge(graph.V[5], graph.V[6], weight=5))
        graph.add_edge(Superedge(graph.V[6], graph.V[5], weight=5))

        graph.add_edge(Superedge(graph.V[4], graph.V[7], weight=5))
        graph.add_edge(Superedge(graph.V[7], graph.V[6], weight=5))

        return graph

    @staticmethod
    def _sample_dec_graph_2():
        graph = DecGraph()

        graph.add_node(Supernode(1, level=0, weight=10))
        graph.add_node(Supernode(2, level=0, weight=30))
        graph.add_node(Supernode(3, level=0, weight=20))
        graph.add_node(Supernode(4, level=0, weight=25))
        graph.add_node(Supernode(5, level=0, weight=25))
        graph.add_node(Supernode(6, level=0, weight=25))
        graph.add_node(Supernode(7, level=0, weight=25))
        graph.add_node(Supernode(8, level=0, weight=10))
        graph.add_node(Supernode(9, level=0, weight=25))
        graph.add_node(Supernode(10, level=0, weight=25))
        graph.add_node(Supernode(11, level=0, weight=25))

        graph.add_edge(Superedge(graph.V[1], graph.V[2], weight=5))
        graph.add_edge(Superedge(graph.V[2], graph.V[1], weight=5))
        graph.add_edge(Superedge(graph.V[3], graph.V[1], weight=20))
        graph.add_edge(Superedge(graph.V[3], graph.V[2], weight=45))
        graph.add_edge(Superedge(graph.V[3], graph.V[4], weight=5))
        graph.add_edge(Superedge(graph.V[3], graph.V[5], weight=15))
        graph.add_edge(Superedge(graph.V[4], graph.V[6], weight=5))
        graph.add_edge(Superedge(graph.V[4], graph.V[7], weight=50))
        graph.add_edge(Superedge(graph.V[5], graph.V[8], weight=5))
        graph.add_edge(Superedge(graph.V[6], graph.V[7], weight=105))
        graph.add_edge(Superedge(graph.V[6], graph.V[3], weight=5))
        graph.add_edge(Superedge(graph.V[7], graph.V[3], weight=5))
        graph.add_edge(Superedge(graph.V[8], graph.V[5], weight=40))
        graph.add_edge(Superedge(graph.V[8], graph.V[9], weight=80))
        graph.add_edge(Superedge(graph.V[8], graph.V[10], weight=5))
        graph.add_edge(Superedge(graph.V[9], graph.V[10], weight=5))

        return graph

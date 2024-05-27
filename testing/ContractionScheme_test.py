import unittest
from typing import Callable, Dict, Any, Set

from multilevel_graphs import ContractionScheme, DecGraph, Supernode, Superedge
from multilevel_graphs.contraction_schemes import DecTable, ComponentSet


class ContractionSchemeTest(unittest.TestCase):
    def test_contract(self):
        contracted_graph = IdentityContractionScheme().contract(self._sample_dec_graph())

        self.assertEqual(4, len(contracted_graph.nodes()))
        self.assertEqual(3, len(contracted_graph.edges()))
        self.assertEqual(self._sample_dec_graph(), contracted_graph.complete_decontraction())

    def test_contract_with_supernode_attr_function(self):
        def supernode_attr_function(supernode: Supernode) -> Dict[str, Any]:
            return {"weight": sum([node['weight'] for node in supernode.dec.nodes()]) + 1}

        dec_graph = self._sample_dec_graph()
        contracted_graph = IdentityContractionScheme(supernode_attr_function).contract(dec_graph)

        self.assertEqual(self._sample_dec_graph(), contracted_graph.complete_decontraction())
        self.assertEqual(31, dec_graph.V[1].supernode['weight'])

    def test_contract_with_superedge_attr_function(self):
        def supernode_attr_function(supernode: Supernode) -> Dict[str, Any]:
            return {"weight": sum([node['weight'] for node in supernode.dec.nodes()])}

        def superedge_attr_function(superedge: Superedge) -> Dict[str, Any]:
            return {"weight": superedge.tail['weight'] +
                              superedge.head['weight'] +
                              sum([edge['weight'] for edge in superedge.dec])}

        dec_graph = self._sample_dec_graph()
        contracted_graph = IdentityContractionScheme(supernode_attr_function, superedge_attr_function)\
            .contract(dec_graph)

        self.assertEqual(self._sample_dec_graph(), contracted_graph.complete_decontraction())
        self.assertEqual(30, dec_graph.V[1].supernode['weight'])
        self.assertEqual(40, contracted_graph.E[(dec_graph.V[2].supernode.key, dec_graph.V[3].supernode.key)]['weight'])

    def test_contract_with_c_set_attr_function(self):
        def supernode_attr_function(supernode: Supernode) -> Dict[str, Any]:
            return {"weight": sum([node['weight'] for node in supernode.dec.nodes()])}

        def c_set_attr_function(c_set: Set[Supernode]) -> Dict[str, Any]:
            return {"weight": sum([node['weight'] for node in c_set])}

        dec_graph = self._sample_dec_graph()
        contracted_graph = IdentityContractionScheme(supernode_attr_function=supernode_attr_function,
                                                     c_set_attr_function=c_set_attr_function)\
            .contract(dec_graph)

        self.assertEqual(self._sample_dec_graph(), contracted_graph.complete_decontraction())
        self.assertEqual(30, list(dec_graph.V[1].supernode['set_of_c_sets'])[0]['weight'])

    @staticmethod
    def _sample_dec_graph() -> DecGraph:
        graph = DecGraph()
        graph.add_node(Supernode(1, level=0, weight=30))
        graph.add_node(Supernode(2, level=0, weight=20))
        graph.add_node(Supernode(3, level=0, weight=10))
        graph.add_node(Supernode(4, level=0, weight=15))
        graph.add_edge(Superedge(graph.V[1], graph.V[2], weight=5))
        graph.add_edge(Superedge(graph.V[2], graph.V[3], weight=10))
        graph.add_edge(Superedge(graph.V[1], graph.V[4], weight=10))
        return graph


if __name__ == '__main__':
    unittest.main()


class IdentityContractionScheme(ContractionScheme):
    def __init__(self,
                 supernode_attr_function: Callable[[Supernode], Dict[str, Any]] = None,
                 superedge_attr_function: Callable[[Superedge], Dict[str, Any]] = None,
                 c_set_attr_function: Callable[[Set[Supernode]], Dict[str, Any]] = None):
        super().__init__(supernode_attr_function, superedge_attr_function, c_set_attr_function)

    def contraction_name(self) -> str:
        return "identity"

    def clone(self):
        return IdentityContractionScheme(
            self._supernode_attr_function,
            self._superedge_attr_function,
            self._c_set_attr_function
        )

    def contraction_function(self, dec_graph: DecGraph) -> DecTable:
        c_sets = [ComponentSet(key=self._get_component_set_id(),
                               supernodes={node})
                  for node in dec_graph.nodes()]
        return DecTable(c_sets)

    def _update_added_node(self, supernode: Supernode):
        pass

    def _update_removed_node(self, supernode: Supernode):
        pass

    def _update_added_edge(self, supernode: Supernode):
        pass

    def _update_removed_edge(self, supernode: Supernode):
        pass

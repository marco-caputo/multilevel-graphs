from abc import ABC, abstractmethod
from typing import Callable, Dict, Any, Set

from multilevel_graphs.dec_graphs import DecGraph, Supernode, Superedge
from multilevel_graphs.contraction_schemes import ContractionScheme, DecTable, ComponentSet


class EdgeBasedContractionScheme(ContractionScheme, ABC):
    """
    //TODO: Add documentation that explains the properties of edge-based contraction schemes.
    """

    def __init__(self,
                 supernode_attr_function: Callable[[Supernode], Dict[str, Any]] = None,
                 superedge_attr_function: Callable[[Superedge], Dict[str, Any]] = None,
                 c_set_attr_function: Callable[[Set[Supernode]], Dict[str, Any]] = None):
        super().__init__(supernode_attr_function, superedge_attr_function, c_set_attr_function)

    @abstractmethod
    def contraction_name(self) -> str:
        pass

    @abstractmethod
    def clone(self):
        pass

    @abstractmethod
    def contraction_function(self, dec_graph: DecGraph) -> DecTable:
        pass

    def _update_added_node(self, node: Supernode):
        # A new dummy supernode is created for the new node, in order to provide a temporary supernode for the new node
        # during following update procedures before the _update_graph procedure.
        new_c_set = ComponentSet(self._get_component_set_id(), {node}, **(self._c_set_attr_function({node})))
        self.component_sets_table.add_set(new_c_set)
        f_c_set = frozenset(self.component_sets_table[node])
        dummy_supernode = Supernode(self._get_supernode_id(), level=self.level, component_sets=f_c_set)
        dummy_supernode.add_node(node)
        node.supernode = dummy_supernode
        self.update_quadruple.add_v_plus(dummy_supernode)
        self.dec_graph.add_node(dummy_supernode)
        # The supernode is not intentionally added to the supernode_table, as it is a dummy node, and it should not be
        # maintained during the _update_graph procedure.

    def _update_removed_node(self, node: Supernode):
        # We can assume the node has no incident edges in the complete decontraction of this contraction scheme graph.
        # So, since this contraction scheme is edge-based, we can assume the node resides in a single component set,
        # composed only by this node.
        self.component_sets_table.remove_set(next(iter(self.component_sets_table[node])))

    @abstractmethod
    def _update_added_edge(self, superedge: Superedge):
        pass

    @abstractmethod
    def _update_removed_edge(self, superedge: Superedge):
        pass

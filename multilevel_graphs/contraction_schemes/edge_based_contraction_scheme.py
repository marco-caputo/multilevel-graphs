from abc import ABC, abstractmethod
from typing import Callable, Dict, Any, Set

from multilevel_graphs import ContractionScheme
from multilevel_graphs.dec_graphs import DecGraph, Supernode, Superedge
from multilevel_graphs.contraction_schemes import DecTable, UpdateQuadruple, ComponentSet


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
        self.contraction_sets_table.add_set(ComponentSet(self._get_component_set_id(),
                                                         {node},
                                                         **(self._c_set_attr_function({node}))))
        key_component_set = frozenset(self.contraction_sets_table[node])

        new_supernode = Supernode(self._get_supernode_id(),
                                  level=self.level,
                                  component_sets=key_component_set,
                                  **(self._supernode_attr_function(node)))
        new_supernode.add_node(node)

        self.supernode_table[key_component_set] = new_supernode
        node.supernode = new_supernode
        self.update_quadruple.add_v_plus(new_supernode)

    def _update_removed_node(self, node: Supernode):
        # We can assume the node has no incident edges in the complete decontraction of this contraction scheme graph.
        # So, since this contraction scheme is edge-based, we can assume the node resides in a single component set,
        # composed only by this node.
        removed_supernode = node.supernode
        del self.supernode_table[removed_supernode.component_sets]
        del self.contraction_sets_table[node]
        self.update_quadruple.add_v_minus(removed_supernode)

    @abstractmethod
    def _update_added_edge(self, superedge: Superedge):
        pass

    @abstractmethod
    def _update_removed_edge(self, superedge: Superedge):
        pass

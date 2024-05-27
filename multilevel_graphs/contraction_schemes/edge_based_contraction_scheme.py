from abc import ABC, abstractmethod
from typing import Callable, Dict, Any, Set

from multilevel_graphs import ContractionScheme
from multilevel_graphs.dec_graphs import DecGraph, Supernode, Superedge
from multilevel_graphs.contraction_schemes import DecTable, UpdateQuadruple, ComponentSet


class EdgeBasedContractionScheme(ContractionScheme, ABC):
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

    def update_added_node(self, node: Supernode):
        self.contraction_sets_table.add_set(ComponentSet(self._get_component_set_id(),
                                                         {node},
                                                         **(self._c_set_attr_function({node}))))
        key_component_set = frozenset(self.contraction_sets_table[node])

        new_supernode = Supernode(self._get_supernode_id(),
                                  level=self.level,
                                  contraction_sets=key_component_set,
                                  **(self._supernode_attr_function(node)))
        new_supernode.add_node(node)

        self.supernode_table[key_component_set] = new_supernode
        node.supernode = new_supernode

    def update_removed_node(self, node: Supernode):
        node.supernode.dec
        pass

    @abstractmethod
    def update_added_edge(self, superedge: Superedge):
        pass

    @abstractmethod
    def update_removed_edge(self, superedge: Superedge):
        pass

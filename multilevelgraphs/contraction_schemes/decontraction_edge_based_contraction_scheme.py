from abc import ABC, abstractmethod
from typing import Callable, Dict, Any, Set, Optional

from multilevelgraphs.dec_graphs import DecGraph, Supernode, Superedge
from multilevelgraphs.contraction_schemes import EdgeBasedContractionScheme, CompTable


class DecontractionEdgeBasedContractionScheme(EdgeBasedContractionScheme, ABC):
    """
    An abstract class for edge-based contraction schemes which make use of the complete decontraction of its graph
    in the update algorithms.

    This abstract class enriches the implementations of two of the update procedures defined in the ContractionScheme
    class: ``_update_added_node`` and ``_update_removed_node``. The other update procedures, ``_update_added_edge``
    and ``_update_removed_edge``, are abstract and should be implemented by the subclasses as they depend on the
    specific contraction scheme. The ``_add_edge_to_decontraction`` and ``_remove_edge_from_decontraction`` methods
    of this class can be used to update the complete decontraction of the graph during the update procedures
    ``_update_added_edge`` and ``_update_removed_edge`` respectively.

    See also:
        :class:`EdgeBasedContractionScheme`, :class:`ContractionScheme`
    """

    _decontracted_graph: Optional[DecGraph]

    def __init__(self,
                 supernode_attr_function: Callable[[Supernode], Dict[str, Any]] = None,
                 superedge_attr_function: Callable[[Superedge], Dict[str, Any]] = None,
                 c_set_attr_function: Callable[[Set[Supernode]], Dict[str, Any]] = None):
        super().__init__(supernode_attr_function, superedge_attr_function, c_set_attr_function)
        self._decontracted_graph = None  # Used to store the current complete decontraction during subsequent updates

    @abstractmethod
    def contraction_name(self) -> str:
        pass

    @abstractmethod
    def clone(self):
        pass

    @abstractmethod
    def contraction_function(self, dec_graph: DecGraph) -> CompTable:
        pass

    # The following methods are overridden to update the decontracted graph used during the other update
    # procedures of the scheme.
    def _update_added_node(self, node: Supernode):
        super()._update_added_node(node)

        if not self._decontracted_graph:
            self._decontracted_graph = self.dec_graph.complete_decontraction()
        else:
            self._decontracted_graph.add_node(node)

    def _update_removed_node(self, node: Supernode):
        super()._update_removed_node(node)

        if not self._decontracted_graph:
            self._decontracted_graph = self.dec_graph.complete_decontraction()
        else:
            self._decontracted_graph.remove_node(node)

    @abstractmethod
    def _update_added_edge(self, superedge: Superedge):
        pass

    @abstractmethod
    def _update_removed_edge(self, superedge: Superedge):
        pass

    def set_decontracted_graph(self):
        """
        Sets the complete decontraction of the graph of this scheme.
        This method is used to lazily set the decontracted graph during the update procedures.
        """
        if not self._decontracted_graph:
            self._decontracted_graph = self.dec_graph.complete_decontraction()

    def _add_edge_to_decontraction(self, edge: Superedge):
        """
        Adds the superedge to the complete decontraction of the graph of this scheme.
        This method should be used as the first step of the update procedure ``_update_added_edge``.

        :param edge: the superedge to add to the complete decontraction
        """
        if not self._decontracted_graph:
            self._decontracted_graph = self.dec_graph.complete_decontraction()
        else:
            self._decontracted_graph.add_edge(Superedge(edge.tail, edge.head))

    def _remove_edge_from_decontraction(self, edge: Superedge):
        """
        Removes the superedge from the complete decontraction of the graph of this scheme.
        This method should be used as the first step of the update procedure ``_update_removed_edge``.

        :param edge: the superedge to remove from the complete decontraction
        """
        if not self._decontracted_graph:
            self._decontracted_graph = self.dec_graph.complete_decontraction()
        else:
            self._decontracted_graph.remove_edge(Superedge(edge.tail, edge.head))

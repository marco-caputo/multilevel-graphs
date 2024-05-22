from abc import ABC, abstractmethod
from multilevel_graphs.dec_graphs import DecGraph


class ContractionScheme(ABC):
    def __init__(self):
        """
        Initializes a contraction scheme based on the contraction function
        defined for this scheme.
        """
        self.contraction_sets_table = dict()
        self.supernode_table = dict()
        self.valid = False

    @abstractmethod
    def contraction_function(self, dec_graph: DecGraph) -> dict:
        """
        Returns a dictionary of contraction sets for the given decontractible graph
        according to this contraction scheme.

        :param dec_graph: the decontractible graph to be contracted
        """
        pass

    def contract(self, dec_graph: DecGraph) -> DecGraph:
        """
        Constructs the given decontractible graph in another decontractible graph according
        to this contraction scheme.

        :param dec_graph: the decontractible graph to be contracted
        """
        self.contraction_sets_table = self.contraction_function(dec_graph)
        """ TODO """
        self.supernode_table = dict()
        self.valid = True
        return None

    def isValid(self):
        return self.valid

    def invalidate(self):
        self.valid = False

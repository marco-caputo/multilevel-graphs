from abc import ABC, abstractmethod
from multilevel_graphs.dec_graphs import DecGraph
from dec_table import DecTable
from dec_graphs import Supernode
from dec_graphs import Superedge
from dec_table import DecTable

class ContractionScheme(ABC):
    def __init__(self):
        """
        Initializes a contraction scheme based on the contraction function
        defined for this scheme.
        """
        self.valid = False

    @abstractmethod
    def contraction_function(self, dec_graph: DecGraph) -> DecTable:
        """
        Returns a dictionary of contraction sets for the given decontractible graph
        according to this contraction scheme.

        :param dec_graph: the decontractible graph to be contracted
        """
        pass

    def _make_supernode_table(self, dec_graph: DecGraph, dec_table_: DecTable):
        pass

    def contract(self, dec_graph: DecGraph) -> DecGraph:
        """
        Constructs the given decontractible graph in another decontractible graph according
        to this contraction scheme.

        :param dec_graph: the decontractible graph to be contracted
        """
        self.contraction_sets_table = self.contraction_function(dec_graph)
        self.supernode_table = self._make_supernode_table(dec_graph, self.contraction_sets_table)
        self._dec_graph = self._make_dec_graph(self.contraction_sets_table, dec_graph)
        self.valid = True
        return None

    def is_valid(self):
        return self.valid

    def invalidate(self):
        self.valid = False

    def _make_dec_graph(self, table : DecTable, dec_graph: DecGraph) -> DecGraph:
        """
        Constructs a decontractible graph from the given decontractible graph
        and the table of cliques.

        :param cliques_table: a table of cliques
        :param dec_graph: the decontractible graph to be contracted
        """
        self.supernode_table = dict()
        dec_i_plus_one = DecGraph()

        for node, set_of_sets in table:
            if set_of_sets not in self.supernode_table:
                self.supernode_table[set_of_sets] = Supernode()
                dec_i_plus_one.add_node(self.supernode_table[set_of_sets])
            else:
                self.supernode_table[set_of_sets].add_node(node)
                node.supernode = self.supernode_table[set_of_sets]
        
        # per ciascun nodo in self.supernode_table, dobbiamo
        # creare i grafi indotti
        #TODO
        for node in self.supernode_table.values():
            pass

        for edge in dec_graph.edges():
            tail = edge.tail
            head = edge.head
            if tail.supernode != head.supernode:
                dec_i_plus_one.E.setdefault((tail.supernode.key, head.supernode.key), Superedge(tail.supernode, head.supernode)).add_edge(edge)
            else:
                tail.supernode.add_edge(Superedge(tail, head))
           
        return dec_i_plus_one
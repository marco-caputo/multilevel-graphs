from contraction_scheme import ContractionScheme
from dec_graphs import DecGraph
from dec_graphs import Supernode
from networkx import DiGraph
from networkx import Graph
import networkx as nx
from dec_table import DecTable

class CliquesContractionScheme(ContractionScheme):
    def __init__(self):
        super().__init__()
        self._clique_table = None

    def contraction_function(self, dec_graph: DecGraph) -> dict:
        udigraph = dec_graph._digraph.to_undirected()
        cliques = nx.find_cliques(udigraph)
        self._clique_table = DecTable(cliques)
        return self._clique_table
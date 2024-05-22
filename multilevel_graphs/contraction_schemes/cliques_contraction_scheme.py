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
        new_dec_graph = self.make_dec_graph(self._clique_table, dec_graph)
    
    def make_dec_graph(cliques_table : DecTable, dec_graph: DecGraph) -> DecGraph:
        for clique in cliques_table:
            supernode = Supernode(clique)
            dec_graph.add_node(supernode)
            
        new_dec_graph = DecGraph()

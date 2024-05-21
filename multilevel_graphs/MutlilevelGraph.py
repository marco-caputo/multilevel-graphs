import utilities.ParUtils as pu
import networkx as nx
from typing import List
from multilevel_graphs import DecGraph, Supernode


class MultilevelGraph:
    def __init__(self, graph, contraction_schemes):
        self.graph = graph
        self.contraction_schemes = contraction_schemes

    
    def enqueue_contraction_scheme(self, contraction_scheme):
        self.contraction_scheme.append(contraction_scheme)

    def reduce_contraction_scheme(self) -> List[DecGraph]:
        """
        Reduces the graph using the contraction schemes.
        """
        for scheme in self.contraction_scheme:
            # Add an indented block of code here
            pass
            
    @staticmethod
    def natural_transformation(graph : nx.DiGraph) -> DecGraph:
        """
        Returns the natural transformation of the graph.
        """
        
        vs = pu.par_map(lambda x: Supernode, graph.nodes(data=True))
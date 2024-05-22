import networkx as nx
from typing import List
from multilevel_graphs import DecGraph, Supernode, Superedge


class MultilevelGraph:
    def __init__(self, graph, contraction_schemes):
        self.graph = graph
        self.contraction_schemes = contraction_schemes

    def enqueue_contraction_scheme(self, contraction_scheme):
        self.contraction_scheme.append(contraction_scheme)

    def reduce_contraction_scheme(self) -> List:
        """
        Reduces the graph using the contraction schemes.
        """
        for scheme in self.contraction_scheme:
            # Add an indented block of code here
            pass

    @staticmethod
    def natural_transformation(graph: nx.DiGraph) -> DecGraph:
        """
        Returns the natural transformation of the graph.
        """
        vs = dict(map(lambda c: (c[0], Supernode(c[0], attr=c[1])), graph.nodes(data=True)))
        es = dict(map(lambda t: ((t[0], t[1]), Superedge(vs[t[0]], vs[t[1]], attr=t[2])), graph.edges(data=True)))
        return DecGraph(vs, es)

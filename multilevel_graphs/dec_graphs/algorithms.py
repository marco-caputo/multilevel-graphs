import networkx as nx
from typing import Set, List
from multilevel_graphs.dec_graphs import DecGraph, Supernode


def maximal_cliques(dec_graph: DecGraph, reciprocal: bool = False) -> Set[Set[Supernode]]:
    """
    Enumerates all the maximal cliques in the given decontractible graph as a set of sets of supernodes.
    The cliques are calculated on the undirected version of the given decontractible graph, obtained by
    keeping only edges that appear in both directions in the original digraph or not, depending on the value of the
    reciprocal parameter.
    The cliques are found using the Bron-Kerbosch algorithm.

    :param dec_graph: the decontractible graph
    :param reciprocal: If True, cliques are calculated on the undirected version of the given decontractible graph
     containing only edges that appear in both directions in the original decontractible graph.
    """
    undirected_graph = dec_graph.graph().to_undirected(reciprocal=reciprocal)
    cliques = list(nx.find_cliques(undirected_graph))
    return set(map(lambda c: set(map(lambda n: dec_graph.V[n], c)), cliques))

def simple_cycles(dec_graph: DecGraph) -> Set[List[Supernode]]:
    """
    Enumerates all the simple cycles in the given decontractible graph as a set of list of supernodes.
    A simple cycle, or elementary circuit, is a closed path where no node appears twice.
    In a decontractible (directed) graph, two simple cycles are distinct if they are not cyclic permutations of
    each other.
    The cycles are found using the Johnson's algorithm.

    :param dec_graph: the decontractible graph
    """
    cycles = list(nx.simple_cycles(dec_graph.graph()))
    return set(map(lambda c: list(map(lambda n: dec_graph.V[n], c)), cycles))

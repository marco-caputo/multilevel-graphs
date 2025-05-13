import networkx as nx
from typing import Set, FrozenSet, Tuple, Generator
from multilevelgraphs.dec_graphs import DecGraph, Supernode


def maximal_cliques(dec_graph: DecGraph, reciprocal: bool = False) -> Generator[Set[Supernode], None, None]:
    """
    Enumerates all the maximal cliques in the given decontractible graph as a list of sets of supernodes.
    The cliques are calculated on the undirected version of the given decontractible graph, obtained by
    keeping only edges that appear in both directions in the original digraph or not, depending on the value of the
    reciprocal parameter.

    The implementation is based on the NetworkX library. More precisely, cliques are found using the non-recursive
    version of Bron-Kerbosch algorithm (1973) [1]_, as adapted by Tomita, Tanaka and Takahashi (2006) [2]_
    and discussed in Cazals and Karande (2008) [3]_.

    Parameters
    ----------
    dec_graph : DecGraph
        the decontractible graph
    reciprocal : bool
        If True, cliques are calculated on the undirected version of the given decontractible graph
        containing only edges that appear in both directions in the original decontractible graph.

    Returns
    -------
    set
        the set of maximal cliques as sets of supernodes

    References
    ----------

    .. target-notes::

    .. [1] Bron, C. and Kerbosch, J. "Algorithm 457: finding all cliques of an undirected graph". Communications of the ACM 16, 9 (Sep. 1973), 575–577. <http://portal.acm.org/citation.cfm?doid=362342.362367 >

    .. [2] Etsuji Tomita, Akira Tanaka, Haruhisa Takahashi, "The worst-case time complexity for generating all maximal cliques and computational experiments", Theoretical Computer Science, Volume 363, Issue 1, Computing and Combinatorics, 10th Annual International Conference on Computing and Combinatorics (COCOON 2004), 25 October 2006, Pages 28–42 <https://doi.org/10.1016/j.tcs.2006.06.015 >

    .. [3] Cazals, F. and Karande, C. "A note on the problem of reporting maximal cliques", Theoretical Computer Science, Volume 407, Issues 1–3, 6 November 2008, Pages 564–568, <https://doi.org/10.1016/j.tcs.2008.05.010 >
    """
    undirected_graph = dec_graph.graph().to_undirected(reciprocal=reciprocal)
    cliques = nx.find_cliques(undirected_graph)
    yield from map(lambda c: set(map(lambda n: dec_graph.V[n], c)), cliques)


def simple_cycles(dec_graph: DecGraph) -> Generator[Tuple[Supernode, ...], None, None]:
    """
    Enumerates all the simple cycles in the given decontractible graph as a set of list of supernodes.
    A simple cycle, or elementary circuit, is a closed path where no node appears twice.
    In a decontractible (directed) graph, two simple cycles are distinct if they are not cyclic permutations of
    each other.

    The implementation is based on the NetworkX library. More precisely, simple cycles are found using a nonrecursive,
    iterator/generator version of Johnson's algorithm [4]_, enhanced by some well-known preprocessing techniques
    that restrict the attention to strongly connected components of the graph.

    Parameters
    ----------
    dec_graph : DecGraph
        The decontractible graph.

    Returns
    -------
    set
        An iterator of simple cycles as tuples of supernodes.

    References
    ----------

    .. target-notes::

    .. [4] Johnson D. B. , "Finding all the elementary circuits of a directed graph," SIAM Journal on Computing, vol. 4, no. 1, pp. 77-84, 1975. https://doi.org/10.1137/0204007
    """
    cycles = nx.simple_cycles(dec_graph.graph())
    yield from map(lambda c: tuple(map(lambda n: dec_graph.V[n], c)), cycles)


def strongly_connected_components(dec_graph: DecGraph) -> Generator[FrozenSet[Supernode], None, None]:
    """
    Enumerates all the strongly connected components in the given decontractible graph as a set of sets of supernodes.
    A strongly connected component (SCC) of a decontractible (directed) graph is a maximal subgraph in which
    there is a path between every pair of nodes.

    The implementation is based on the NetworkX library. More precisely, the SCCs are found using the
    Kosaraju's algorithm [5]_.

    Parameters
    ----------
    dec_graph : DecGraph
        the decontractible graph

    Returns
    -------
    set
        The set of strongly connected components as sets of supernodes

    References
    ----------

    .. target-notes::

    .. [5] Sharir M. , "A strong-connectivity algorithm and its applications in data flow analysis", Computers & Mathematics with Applications, 1981 - Elsevier. https://doi.org/10.1016/0898-1221(81)90008-0
    """
    sccs = nx.kosaraju_strongly_connected_components(dec_graph.graph())
    yield from map(lambda c: frozenset(map(lambda n: dec_graph.V[n], c)), sccs)

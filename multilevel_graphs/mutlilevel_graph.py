import networkx as nx
from typing import List, Optional
from multilevel_graphs import DecGraph, Supernode, Superedge, ContractionScheme


class MultilevelGraph:
    _dec_graph_0: DecGraph
    _contraction_schemes: List[ContractionScheme]

    def __init__(self, graph: nx.DiGraph, contraction_schemes: List[ContractionScheme] = None):
        """
        Initializes a multilevel graph based on the given NetworkX graph and list of contraction schemes.
        The multilevel graph is built from the bottom up, starting from the graph at level 0, and
        considering the contraction functions represented by the contraction schemes in the order of the given list.

        After the initialization, the state of each of the given contraction schemes will be affected by the
        contraction.

        :param graph: the NetworkX graph to be used as the base graph of the multilevel graph
        :param contraction_schemes: the list of contraction schemes to be used in the multilevel graph
        """
        self._dec_graph_0 = self.natural_transformation(graph)
        self._contraction_schemes = [scheme.clone() for scheme in contraction_schemes] if contraction_schemes else []
        for i in range(self.height()):
            contraction_schemes[i].level = i + 1
        self._build_contraction_schemes()

    def _build_contraction_schemes(self):
        """
        Builds the contraction schemes of the multilevel graph from bottom to top,
        starting from the graph at level 0.
        The decontractible graphs in this multilevel graph hierarchy are reconstructed and replaced with new ones.
        """
        last_dec_graph = self._dec_graph_0
        for scheme in self._contraction_schemes:
            last_dec_graph = scheme.contract(last_dec_graph)

    def get_graph(self, level: int) -> Optional[DecGraph]:
        """
            Returns the reference of the decontractible graph at the given level in this multilevel graph.
            If the given level is 0, the base decontractible graph is returned, while if the given level is 1
            or higher, the decontractible graph resulting from the contraction scheme at the given level is returned.
            If the given level is not in the range of the contraction schemes in this multilevel graph, None is
            returned.

            The structure of the given decontractible graph should not be modified, as it may affect the integrity of
            the multilevel graph.

            :param level: the level of the decontractible graph to be returned
            :return: the decontractible graph at the given level
        """
        if level == 0:
            return self._dec_graph_0
        elif 1 <= level <= self.height():
            return self._contraction_schemes[level - 1].dec_graph
        else:
            return None

    def __getitem__(self, level: int) -> Optional[DecGraph]:
        """
        Returns the reference of the decontractible graph at the given level in this multilevel graph.
        If the given level is 0, the base decontractible graph is returned, while if the given level is 1
        or higher, the decontractible graph resulting from the contraction scheme at the given level is returned.
        If the given level is not in the range of the contraction schemes in this multilevel graph, None is returned.

        The structure of the given decontractible graph should not be modified, as it may affect the integrity of
        the multilevel graph.

        :param level: the level of the decontractible graph to be returned
        :return: the decontractible graph at the given level
        """
        return self.get_graph(level)

    def append_contraction_scheme(self, contraction_scheme):
        """
        Appends a new contraction scheme to the multilevel graph on top of the existing ones.
        The new contraction scheme is immediately applied to the decontractible graph at the previous level to
        obtain the decontractible graph at the new level.

        :param contraction_scheme: the contraction scheme to be appended
        """
        contraction_scheme.level = self.height() + 1
        contraction_scheme.contract(self._contraction_schemes[-1].dec_graph)
        self._contraction_schemes.append(contraction_scheme)

    def height(self) -> int:
        """
        Returns the height of the multilevel graph.
        The height of a multilevel graph is defined as the number of contraction schemes it has.
        """
        return len(self._contraction_schemes)

    def __len__(self) -> int:
        """
            Returns the height of the multilevel graph.
            The height of a multilevel graph is defined as the number of contraction schemes it has.
        """
        return self.height()

    @staticmethod
    def natural_transformation(graph: nx.DiGraph) -> DecGraph:
        """
        Returns the natural transformation of the graph.
        """
        vs = dict(map(lambda c: (c[0], Supernode(c[0], attr=c[1])), graph.nodes(data=True)))
        es = dict(map(lambda t: ((t[0], t[1]), Superedge(vs[t[0]], vs[t[1]], attr=t[2])), graph.edges(data=True)))
        return DecGraph(vs, es)

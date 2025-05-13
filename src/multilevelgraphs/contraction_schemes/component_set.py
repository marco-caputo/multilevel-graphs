from typing import Any, Set, Dict, Iterable, Union
from multilevelgraphs.dec_graphs import Supernode


class ComponentSet:
    """
    A ComponentSet is a set of supernodes that are part of the same component according to a certain contraction scheme.
    For instance, a componentSet could be representing a clique or a circuit, depending on which contraction scheme
    created it.

    Note that, in general, a supernode can be part of multiple ComponentSets in some contraction schemes, while in
    others, like the SCCs contraction scheme, a supernode can only be part of one ComponentSet at a time.
    In any case, nodes in the same supernode must share the same component sets where they are part of according to
    the contraction scheme at the immediate upper level.
    The set of component sets associated to a supernode is, therefore, the set of component sets that each of its
    nodes share.

    Attributes
    ----------
    key : Any
        the unique identifier of the component set in its contraction scheme

    Examples
    --------
    A ComponentSet can be treated as a set of supernodes, for instance::

        from multilevelgraphs import ComponentSet, Supernode
        c1 = ComponentSet(1, {Supernode(1), Supernode(2)})
        c1.add(Supernode(3))
        for supernode in c1:
            print(supernode)

    A ComponentSet can also have attributes that may be calculated during the contraction process::

        from multilevelgraphs import MultilevelGraph, SCCsContractionScheme
        import networkx as nx
        nx_graph = nx.DiGraph()
        nx_graph.add_edges_from([(1, 2, {'weight': 25}), (2, 3, {'weight': 20}), (3, 1, {'weight': 10})])
        scheme = SCCsContractionScheme(c_set_attr_function=lambda c_set: sum([node['weight'] for node in c_set]))
        ml_graph = MultilevelGraph(nx_graph, [scheme])
        c1 = next(iter(ml_graph.get_component_sets(1)))
        c1['weight'] # 55
        c1['double_wight'] = c1['weight'] * 2
    """
    key: Any
    _supernodes: Set[Supernode]
    _attr: Dict[str, Any]

    def __init__(self, key: Any, supernodes: Set[Supernode] = None, **attr):
        """
        Initialize a ComponentSet with a key, a set of supernodes and optional attributes.

        :param key: the unique identifier of the component set in its contraction scheme
        :param supernodes: the supernodes that are part of the component set
        :param attr: the key-values pairs attributes of the component set
        """
        self.key = key
        self._supernodes = supernodes if supernodes else set()
        self._attr = attr

    def copy(self) -> 'ComponentSet':
        return ComponentSet(self.key, self._supernodes.copy(), **self._attr)

    def deepcopy(self, supernodes_dict: Dict[Any, Supernode]) -> 'ComponentSet':
        """
        Returns a deep copy of the component set where the supernodes are replaced by the supernodes in the given
        dictionary having the same keys.

        :param supernodes_dict: the dictionary of supernodes to replace the supernodes in the component set
        :return: a deep copy of the component set with the new supernodes
        """
        return ComponentSet(self.key, {supernodes_dict[supernode.key] for supernode in self._supernodes}, **self._attr)

    def __contains__(self, value):
        return value in self._supernodes

    def __iter__(self):
        return iter(self._supernodes)

    def __len__(self):
        return len(self._supernodes)

    def add(self, value):
        self._supernodes.add(value)

    def discard(self, value):
        self._supernodes.discard(value)

    def update(self, **attr):
        self._attr.update(attr)

    def __getitem__(self, key: str) -> Any:
        return self._attr[key]

    def __setitem__(self, key: str, value: Any):
        self._attr[key] = value

    def __or__(self, other: Union[Set[Supernode], 'ComponentSet']) -> Set[Supernode]:
        if isinstance(other, ComponentSet):
            return self._supernodes | other._supernodes
        else:
            return self._supernodes | other

    def __ror__(self, other: Union[Set[Supernode], 'ComponentSet']) -> Set[Supernode]:
        return self.__or__(other)

    def __sub__(self, other: Union[Set[Supernode], 'ComponentSet']) -> Set[Supernode]:
        if isinstance(other, ComponentSet):
            return self._supernodes - other._supernodes
        else:
            return self._supernodes - other

    def __str__(self):
        return f'CSet({self.key}):{list([supernode.key for supernode in self._supernodes])}'

    def __repr__(self) -> str:
        return str(self)

    def __hash__(self) -> int:
        return hash(self.key)

    def __eq__(self, other: Union[Iterable[Supernode], 'ComponentSet']) -> bool:
        if isinstance(other, ComponentSet):
            return self.key == other.key
        return self._supernodes == other

from typing import Any, Set
from multilevel_graphs.dec_graphs import Supernode


class ComponentSet:

    def __init__(self, key: Any, supernodes: Set[Supernode] = None, **attr):
        self.key = key
        self._supernodes = supernodes if supernodes else set()
        self._attr = attr

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

    def __str__(self):
        return f'ComponentSet({self.key}):{list(self._supernodes)}'

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other):
        return self.key == other.key


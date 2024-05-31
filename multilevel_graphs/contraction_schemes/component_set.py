from typing import Any, Set, Dict, Iterable
from multilevel_graphs.dec_graphs import Supernode


class ComponentSet:
    key: Any
    _supernodes: Set[Supernode]
    _attr: Dict[str, Any]

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

    def update(self, **attr):
        self._attr.update(attr)

    def __getitem__(self, key: str) -> Any:
        return self._attr[key]

    def __setitem__(self, key: str, value: Any):
        self._attr[key] = value

    def __sub__(self, other: Set[Supernode] | 'ComponentSet') -> Set[Supernode]:
        if isinstance(other, ComponentSet):
            return self._supernodes - other._supernodes
        else:
            return self._supernodes - other

    def __str__(self):
        return f'ComponentSet({self.key}):{list(self._supernodes)}'

    def __repr__(self) -> str:
        return str(self)

    def __hash__(self) -> int:
        return hash(self.key)

    def __eq__(self, other: Iterable[Supernode] | 'ComponentSet') -> bool:
        if isinstance(other, ComponentSet):
            return self.key == other.key
        return self._supernodes == other


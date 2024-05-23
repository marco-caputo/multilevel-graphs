from typing import Iterable

class DecTable:
    def __init__(self, sets : list):
        _table = dict()
        for nodes_set in sets:
            for node in nodes_set:
                _table.setdefault(node, set()).add(nodes_set)
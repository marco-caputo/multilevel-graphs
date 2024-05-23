from typing import Iterable

class DecTable:
    """
    A decontractible table is a data structure that stores 
    the information of which nodes are in which cover.
    """
    def __init__(self, sets : Iterable):
        _table = dict()
        for nodes_set in sets:
            for node in nodes_set:
                _table.setdefault(node, set()).add(nodes_set)
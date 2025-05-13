Package: dec\_graphs
======================================

Decontractible Graphs are recursively defined graphs that can be used to represent graphs which
nodes can be decomposed into smaller graphs.
This module provides classes to represent decontractible graphs, its nodes and edges as independent objects
called supernodes and superedges, respectively, and some algorithms to work with them.

Class: DecGraph
------------------------------------------------

.. autoclass:: multilevelgraphs.dec_graphs.dec_graph.DecGraph
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: V, E

Class: Supernode
------------------------------------------------

.. autoclass:: multilevelgraphs.dec_graphs.dec_graph.Supernode
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: key, level, dec, component_sets, supernode, attr

Class: Superedge
------------------------------------------------

.. autoclass:: multilevelgraphs.dec_graphs.dec_graph.Superedge
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: head, tail, level, dec, attr

Module: Algorithms
------------------------------------------------

.. automodule:: multilevelgraphs.dec_graphs.algorithms
   :members:
   :undoc-members:
   :show-inheritance:

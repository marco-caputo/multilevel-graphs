.. MultiLevelGraphs documentation master file, created by
   sphinx-quickstart on Mon Jun  3 20:03:27 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to MultiLevelGraphs documentation!
============================================
MultiLevelGraphs is a Python package based on NetworkX for creating and managing hierarchical structures of graphs
obtained by gradual contractions of nodes and edges.

A Multi-level graph is a data structure useful for describing structural features of large and sparse directed graphs
by identifying meaningful topological patterns, such as strongly connected components, circuits and cliques.
It provides operations for building multilevel graphs from directed graphs, and for extracting and analyzing
structural patterns at different levels of the hierarchy.

.. toctree::
   :maxdepth: 1
   :caption: User Guide

   installation
   extension
   examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   multilevel_graphs
   contraction_schemes
   contraction_schemes_impl
   dec_graphs
   io


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

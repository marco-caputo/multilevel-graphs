# MultiLevelGraphs

[![Build Status](https://github.com/lorenzo-lupi/multilevel_graphs/actions/workflows/publish.yml/badge.svg)](https://github.com/lorenzo-lupi/multilevel_graphs/actions)
[![TestPyPI version](https://img.shields.io/badge/test%20pypi-v0.1.0-blue)](https://test.pypi.org/project/multilevelgraphs/)
[![Documentation Status](https://readthedocs.org/projects/multilevel-graphs/badge/?version=latest)](https://multilevel-graphs.readthedocs.io/en/latest/?badge=latest)

## Description

MultiLevelGraphs is a Python package based on NetworkX for creating and managing hierarchical structures of graphs
obtained by gradual contractions of nodes and edges.

A Multi-level graph is a data structure useful for describing structural features of large and sparse directed graphs
by identifying meaningful topological patterns, such as strongly connected components, circuits and cliques.
It provides operations for building multi-level graphs from directed graphs, and for extracting and analyzing
structural patterns at different levels of the hierarchy.

## Installation

Before installing MultiLevelGraphs, ensure that you have the following prerequisites:

- Python 3.10 or higher
- pip (Python package installer)

You can install MultiLevelGraphs using pip. Open your terminal or command prompt and run the following command:

```bash
    pip install --index-url https://test.pypi.org/simple/ multilevelgraphs
```

To verify that the library has been installed correctly, you can try importing it in a Python shell or script.
Open your terminal or command prompt and enter:

```python

    import multilevelgraphs
    
    print(multilevelgraphs.__version__)
```

This should print the version number of MultiLevelGraphs if the installation was successful.


## Documentation
Documentation is available at the following links:

[multilevel-graphs.readthedocs.io](multilevel-graphs.readthedocs.io)\
[multilevel-graphs.rtfd.io](multilevel-graphs.rtfd.io)

Dependencies
------------

MultiLevelGraphs has a few dependencies which should be installed automatically when you install the library.
However, for reference, here are the main dependencies:

- NetworkX
- typing
- abc
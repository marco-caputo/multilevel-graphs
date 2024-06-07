# MultiLevelGraphs

[![Build Status](https://travis-ci.com/your-username/your-package-name.svg?branch=master)](https://travis-ci.com/your-username/your-package-name)
[![PyPI version](https://badge.fury.io/py/your-package-name.svg)](https://badge.fury.io/py/your-package-name)

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
    pip install MultiLevelGraphs
```

To verify that the library has been installed correctly, you can try importing it in a Python shell or script.
Open your terminal or command prompt and enter:

```python

    import multilevelgraphs
    
    print(multilevelgraphs.__version__)
```

This should print the version number of MultiLevelGraphs if the installation was successful.

Dependencies
------------

MultiLevelGraphs has a few dependencies which should be installed automatically when you install the library.
However, for reference, here are the main dependencies:

- NetworkX
- typing
- abc
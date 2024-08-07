Usage Examples
===================================

Here are some examples of how to use the core functionalities of the library.

MultilevelGraph
---------------
A multilevel graph can be created from a NetworkX graph and a sequence of contraction schemes. For instance
a multi-level graph of height 2 can be instantiated as follows::

    import networkx as nx
    from multilevel_graphs import MultilevelGraph, CliquesContractionScheme, SCCsContractionScheme

    nx_graph = nx.DiGraph()
    nx_graph.add_edges_from([(1, 2), (2, 3), (3, 1), (3, 4), (4, 5)])
    ml_graph = MultilevelGraph(nx_graph, [CliquesContractionScheme(), SCCsContractionScheme()])

Alternatively, a multilevel graph can be created from a NetworkX graph and the contraction schemes can be appended
subsequently. In the following example, the resulting multilevel graph is equivalent to the one created in the
previous example::

    import networkx as nx
    from multilevel_graphs import MultilevelGraph, CliquesContractionScheme, SCCsContractionScheme

    nx_graph = nx.DiGraph()
    nx_graph.add_edges_from([(1, 2), (2, 3), (3, 1), (3, 4), (4, 5)])
    ml_graph = MultilevelGraph(nx_graph)
    ml_graph.append_contraction_scheme(CliquesContractionScheme())
    ml_graph.append_contraction_scheme(SCCsContractionScheme())

The decontractible graph at a certain level can be retrieved using the ``get_graph`` method or the [] notation::

    dec_graph_1 = ml_graph.get_graph(1)
    dec_graph_2 = ml_graph[2]

Note that the [] notation will return a reference to the decontractible graph, resulting in a performance gain,
while the ``get_graph`` method will return a deep copy of the decontractible graph. For this reason, is
recommended to use the [] notation when the returned decontractible graph is not going to be modified.

Once the multilevel graph is created, nodes and edges can be added or removed from the base graph indicating
the key of the nodes and the attributes of the nodes and edges.
For instance, a new node can be added to the base graph as follows::

    ml_graph.add_node(6, color='red')

Updates to the base graph will be lazily propagated to the upper levels, and further requests for the
decontractible graph at a certain level will trigger the computation of the decontractible graph at that level.

ContractionScheme
-----------------
Let CliquesContractionScheme and SCCsContractionScheme be sample contraction scheme implementations, they can be
used to define a multilevel graph as follows::

    from multilevel_graphs import MultilevelGraph, SCCsContractionScheme, CliquesContractionScheme
    import networkx as nx

    nx_graph = nx.DiGraph()
    nx_graph.add_edges_from([(1, 2), (2, 3), (3, 1)])

    scheme_1 = CliquesContractionScheme()
    scheme_2 = SCCsContractionScheme()
    ml_graph = MultilevelGraph(nx_graph, [scheme_1, scheme_2])

The definition of the contraction scheme could also include attribute functions for supernodes, superedges and
component sets::

    scheme = SCCsContractionScheme(
        supernode_attr_function= lambda n: {'size': len(n)},
        superedge_attr_function= lambda e: {'weight': sum([edge['weight'] for edge in e.edges()])},
        c_set_attr_function= lambda c_set: {'size': len(c_set)}
    )

ComponentSet
------------
A ComponentSet can be treated as a set of supernodes, for instance::

    from multilevel_graphs import ComponentSet, Supernode
    c1 = ComponentSet(1, {Supernode(1), Supernode(2)})
    c1.add(Supernode(3))
    for supernode in c1:
        print(supernode)

A ComponentSet can also have attributes that may be calculated during the contraction process::

    from multilevel_graphs import MultilevelGraph, SCCsContractionScheme
    import networkx as nx
    nx_graph = nx.DiGraph()
    nx_graph.add_edges_from([(1, 2, {'weight': 25}), (2, 3, {'weight': 20}), (3, 1, {'weight': 10})])
    scheme = SCCsContractionScheme(c_set_attr_function=lambda c_set: sum([node['weight'] for node in c_set]))
    ml_graph = MultilevelGraph(nx_graph, [scheme])
    c1 = next(iter(ml_graph.get_component_sets(1)))
    c1['weight'] # 55
    c1['double_wight'] = c1['weight'] * 2

DecGraph
--------
A decontractible graph can be created as follows, creating its supernodes and superedges directly::

    from multilevel_graphs.dec_graphs import DecGraph, Supernode, Superedge
    dec_graph = DecGraph()
    n1 = Supernode(1)
    n2 = Supernode(2)
    e = Superedge(n1, n2)
    dec_graph.add_node(n1)
    dec_graph.add_node(n2)
    dec_graph.add_edge(e)

Or can be created from a NetworkX directed graph using the ``natural_transformation`` static method from
the :class:`MultiLevelGraph` class. In the following example, an equivalent decontractible graph is created::

    import networkx as nx
    from multilevel_graphs import MultiLevelGraph
    nx_graph = nx.DiGraph()
    nx_graph.add_edges_from([(1, 2)])
    dec_graph = MultiLevelGraph.natural_transformation(nx_graph)

In both cases the created supernodes and superedges will have an empty decontraction.

Once the decontractible graph is created, specific supernodes and superedges can be accessed through the
``V`` and ``E`` attributes.
In the following example, a new supernode is added to both decontractible graphs ``n1.dec`` and ``n2.dec``, then
a new superedge between the two new subnodes is added to the decontraction of the superedge with key (1,2)::

    subnode_1 = Supernode(3)
    subnode_2 = Supernode(4)
    dec_graph.V[1].dec.add_node(subnode_1)
    dec_graph.V[2].dec.add_node(subnode_2)
    dec_graph.E[(1, 2)].dec.add(Superedge(subnode_1, subnode_2))

Superedges added to supernodes decontractions must have their tail and head supernodes included in the
decontractions::

    subnode_3 = Supernode(5)
    subnode_4 = Supernode(6)
    dec_graph.V[1].dec.add_node(subnode_3)
    dec_graph.V[1].dec.add_node(subnode_4)
    dec_graph.V[1].dec.add_edge(Superedge(subnode_3, subnode_4))

Note that supernodes must have a unique key relative to the decontractible graph where they are
directly included, so a supernode with key 1 can host a supernode with key 1 in its decontraction.

Supernode
---------
A supernode can be created indicating a key of any type and any other optional attribute, that are typically
automatically initialized when the supernode is created by structures like :class:`MultiLevelGraph`.
Custom attributes, as 'weight', for instance, can be added to the supernode as follows::

    from multilevel_graphs.dec_graphs import Supernode
    supernode = Supernode(key=1, level=0, weight=10)

While the default supernode attributes are accessed with the . notation, custom attributes can be accessed
and assigned with the [] notation::

    print(supernode.level) # 0
    print(supernode['weight']) # 10

Superedge
---------
A superedge can be created indicating the reference to the tail and head supernodes objects and any other
optional attribute, that are typically automatically initialized when the supernode is created by structures
like :class:`MultiLevelGraph`.
Custom attributes, as 'weight', for instance, can be added to the superedge as follows::

    from multilevel_graphs.dec_graphs import Supernode, Superedge
    supernode_1 = Supernode(key=1, level=0)
    supernode_2 = Supernode(key=2, level=0)
    superedge = Superedge(tail=supernode_1, head=supernode_2, level=0, weight=10)

While the default supernode attributes are accessed with the . notation, custom attributes can be accessed
and assigned with the [] notation::

    print(superedge.level) # 0
    print(superedge['weight']) # 10

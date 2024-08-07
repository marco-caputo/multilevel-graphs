Extending ContractionScheme
===================================

Here's a brief guide to extend the library with new contraction schemes.
The library is specifically designed to provide extensibility for new contraction schemes implementations,
which can be used to create new types of multilevel graphs. For this purpose the library provides some abstract classes
such as :any:`ContractionScheme`, :any:`EdgeBasedContractionScheme` and
:any:`DecontractionEdgeBasedContractionScheme`, which can be extended to implement new contraction schemes and aim
to minimize the amount of code required to implement a new one.


Implementing methods
--------------------

The following are the methods that should be implemented when extending the ContractionScheme class. No other methods
should be overridden, as the rest of the methods are already implemented in the ContractionScheme class as general
procedures and should thus be used as they are.
As seen after this section, some of these methods are already implemented in ContractionScheme abstract subclasses.

- **contraction_name**

   This method should provide a unique string identifier for the contraction scheme. This identifier should include
   a brief name of the contraction scheme and any other relevant information that can be used to distinguish the
   different versions of the same contraction scheme. Some contraction schemes may indeed have construction parameters
   that slightly change the behavior of the contraction scheme, in this case, the contraction_name method should include
   the information of the value of these parameters in the identifier.

   See also:
        :any:`ContractionScheme.contraction_name`.

   Example::

        def contraction_name(self) -> str:
            return "cliques_" + ("" if self._reciprocal else "not_") + "rec"

- **clone**
    This method should return a new instance of the contraction scheme with the same parameters as the current instance.
    This should normally consist in a call to the constructor of the contraction scheme with the same parameters as the
    current instance, which include the attribute functions and the parameters of the specific contraction scheme.

    See also:
        :any:`ContractionScheme.clone`.

    Example::

        def clone(self):
            return CliquesContractionScheme(self._supernode_attr_function,
                                        self._superedge_attr_function,
                                        self._c_set_attr_function,
                                        self._reciprocal)

- **contraction_function**
    This is the main method of the contraction scheme, which should implement the contraction of the graph. This method
    should just identify the component sets according to the contraction scheme, and return the corresponding component
    set table, which must represent a covering of the input graph nodes. The single component set should represent
    the specific pattern of the contraction scheme.
    Component sets should be created using the ComponentSet class constructor from the sets of nodes, the
    component set id generator `_get_component_set_id` provided by the contraction scheme abstract class and the
    attribute function.

    Example::

        def contraction_function(self, dec_graph: DecGraph) -> CompTable:
            cliques = maximal_cliques(dec_graph, self._reciprocal)
            return CompTable([ComponentSet(self._get_component_set_id(),
                                           clique,
                                           **(self._c_set_attr_function(clique)))
                              for clique in cliques])

    If the component set table is created with an empty constructor and the component sets are added subsequently with
    the `add_set` method, the modified set of nodes should be cleared with `comp_table.modified.clear()`
    before returning the component set table.

    Example::

        def contraction_function(self, dec_graph: DecGraph) -> CompTable:
            cliques = maximal_cliques(dec_graph, self._reciprocal)
            comp_table = CompTable()
            for clique in cliques:
                comp_table.add_set(ComponentSet(self._get_component_set_id(),
                                                          clique,
                                                          **(self._c_set_attr_function(clique)))
            comp_table.modified.clear()
            return comp_table

    Since the returned component set table must represent a covering of the nodes (the union of all component sets
    should be equal to the input graph set of nodes), if there's a possibility for nodes to not be part of any
    component set. they should be manually included in the component set table as singletons.

    Example::

        def contraction_function(self, dec_graph: DecGraph) -> CompTable:
            stars = self._star_sets(dec_graph)
            comp_table = CompTable([ComponentSet(self._get_component_set_id(),
                                                 star,
                                                 **(self._c_set_attr_function(star)))
                                    for star in stars])

            for node in dec_graph.V.values():
                if node not in comp_table:
                    comp_table.add_set(ComponentSet(self._get_component_set_id(),
                                                    {node},
                                                    **(self._c_set_attr_function({node}))))

            comp_table.modified.clear()

            return comp_table

    Note that component sets representing the same set of nodes should not be added to the component set table multiple
    times, as this could lead to unexpected behavior during the update procedures of the contraction scheme.

    See also:
        :any:`ContractionScheme.contraction_function`, :any:`CompTable`, :any:`ComponentSet`.

- **update_added_node, update_removed_node, update_added_edge, update_removed_edge**
    These method should update the component set table of the contraction scheme when a single node or edge is added
    or removed from the immediate lower-level graph. For this reason, the arguments of these methods must be defined
    in that lower-level graph, and hence, in the complete decontraction of the current level graph.

    For all of these methods, in particular for the `update_added_edge` and `update_removed_edge` methods, the main
    concern of the implementation should be to update the component set table according to a single change in the lower
    level graph, properly invoking the methods `add_set` and `remove_set` of the component set table.
    For instance, if the removal of an edge splits a component set into two, the method should remove the
    original component set and add two new component sets.
    Furthermore, removing or adding an edge at the lower level also requires to update the superedges
    or the supernodes of the current level, depending on the supernodes of the nodes involved in the edge.
    For this purpose, the supernode method `add_edge` and `remove_edge` or the contraction scheme methods
    `_add_edge_in_superedge` or `_remove_edge_in_superedge` should be used.

    Example::

        def _update_added_edge(self, edge: Superedge):
            u = edge.tail.supernode
            v = edge.head.supernode

            if u == v:
                u.add_edge(edge)
            else:
                self._add_edge_in_superedge(u.key, v.key, edge)
                if len(self.dec_graph.E[(u.key, v.key)].dec) == 1:
                    reach_supernodes = self._reach_visit(v, u)
                    if reach_supernodes:
                        for node in reach_supernodes:
                            self.component_sets_table.remove_set(next(iter(node.component_sets)))
                        new_set = set.union(*[supernode.dec.nodes() for supernode in reach_supernodes])
                        self.component_sets_table.add_set(ComponentSet(self._get_component_set_id(),
                                                                       new_set,
                                                                       **(self._c_set_attr_function(new_set))))
                        self._update_graph() # Updates graph structure for further updates


    All the logic and algorithms to update the component set table should be implemented in these methods, and the
    `contraction_function` method should only be used to create the initial component set table.
    As in the example above, some algorithms may require to updated graph structure at the current level in
    order to properly update the component set table. Since several edges may be added or removed in a single `update`
    procedure, it is important for these kind of contraction schemes to update the graph structure immediately after
    each single update with the method `_update_graph`, to avoid inconsistencies in subsequent calls of the same method.
    Conversely, for other contraction schemes the structure where update algorithms are executed is the structure of
    the graph at the lower level. For these cases, methods to manage the complete decontraction of the current level
    are provided in the abstract class :any:`DecontractionEdgeBasedContractionScheme`.

    Note that existing nodes at the lower level graph should be part of at least one component set and should have
    a corresponding supernode in the current level graph at the end of each of these methods, while deleted nodes
    should not.
    For this reason, custom implementations of `update_added_node` should be careful to include the new added supernode
    in a component set and, if necessary, create a new temporary supernode for the new node.
    Conversely, implementations of `update_removed_node` should remove the entry of the node in the
    component set table, set the supernode of the removed node to `None` and track the deleted node in the set mapped
    in the dictionary `self._deleted_subnodes`.
    This basic behavior is implemented in the abstract class :any:`EdgeBasedContractionScheme`.

    See also:
        :any:`ContractionScheme._update_added_node`, :any:`ContractionScheme._update_removed_node`,
        :any:`ContractionScheme._update_added_edge`, :any:`ContractionScheme._update_removed_edge`,
        :any:`ContractionScheme._update_graph`, :any:`ContractionScheme._add_edge_in_superedge`,
        :any:`ContractionScheme._remove_edge_in_superedge`,
        :any:`EdgeBasedContractionScheme`,
        :any:`DecontractionEdgeBasedContractionScheme`.

Abstract classes
----------------

The library provides some abstract classes that can be extended to implement new contraction schemes. These classes
provide some basic implementations of the methods that are not strictly related to the specific contraction scheme
implementation, but are common to all contraction schemes. These classes are:

- **ContractionScheme**

    This is the main abstract class that should be extended to implement a new contraction scheme. It provides the
    basic structure of the contraction scheme, including: attributes, such as the component set table;
    construction parameters, such as the attribute functions; implemented methods for managing the graph structure,
    such as `_make_dec_graph` and `_update_graph`. This class should be extended to implement the specific contraction
    scheme, by implementing the methods described in the previous section.

    See also:
        :any:`ContractionScheme`, :any:`ContractionScheme._make_dec_graph`, :any:`ContractionScheme._update_graph`.

- **EdgeBasedContractionScheme**
    This abstract class extends the ContractionScheme class and provides some basic implementations of the methods
    `update_added_node`, `update_removed_node`. This class should be extended to implement contraction schemes that
    require nodes to be reachable in the undirected version of the graph in order for them to be part of the same
    component set. We call these contraction schemes edge-based contraction schemes, as they require edges in order
    to define the component sets. For this reason, the methods `update_added_node` and `update_removed_node` assume
    new added nodes will reside in a singleton component set, and removed nodes will be always be part of a
    singleton component set (in the method `update` of :any:`ContractionScheme`, the removal of incident edges always
    precedes the removal of nodes).

    See also:
        :any:`EdgeBasedContractionScheme`, :any:`ContractionScheme.update`,

- **DecontractionEdgeBasedContractionScheme**
    This abstract class extends the :any:`EdgeBasedContractionScheme` class and provides an attribute and some
    methods to lazily manage the complete decontraction graph of the scheme graph.
    These methods are `set_decontracted_graph`, `add_edge_to_decontraction` and `remove_edge_from_decontraction`.
    The purpose of this class is to avoid to perform the complete decontraction of the current level graph at each
    update, but to manage the decontraction graph lazily, updating it along with the graph at the current level.
    This class should be extended to implement edge-based contraction schemes that require the updated complete
    decontraction of the current level graph in order to execute update algorithms and modify the component set table.
    For instance, the cycles contraction scheme requires the complete decontraction of the current level graph to
    find all the new cycles that are created by the addition of an edge. Other contraction schemes may use the
    contracted graph structure update the component set table, relying on specific properties, and thus do not require
    the complete decontraction.

    Example::

        def _update_added_edge(self, edge: Superedge):
            u = edge.tail.supernode
            v = edge.head.supernode

            if u == v:
                u.add_edge(edge)
            else:
                self._add_edge_in_superedge(u.key, v.key, edge)

            self._add_edge_to_decontraction(edge)

            # Find all the simple cycles that contain the new edge and track them in the component sets table
            for new_circuit in self.cycle_search(self._decontracted_graph.graph(), [edge.tail.key, edge.head.key]):
                new_c_set = ComponentSet(self._get_component_set_id(),
                                         {self._decontracted_graph.V[node] for node in new_circuit})
                self.component_sets_table.add_set(new_c_set, maximal=self._maximal)

    See also:
        :any:`DecontractionEdgeBasedContractionScheme`, :any:`ContractionScheme.update`,


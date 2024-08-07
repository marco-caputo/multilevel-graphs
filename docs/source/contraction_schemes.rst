Package: contraction\_schemes
===============================================

Abstract Class: ContractionScheme
----------------------------------

.. autoclass:: multilevelgraphs.contraction_schemes.contraction_scheme.ContractionScheme
   :members:
   :undoc-members:
   :private-members: _update_added_node, _update_removed_node, _update_added_edge, _update_removed_edge, _update_graph, _add_edge_in_superedge, _remove_edge_in_superedge, _make_dec_graph
   :show-inheritance:
   :exclude-members: level, dec_graph, component_sets_table, supernode_table, update_quadruple

Abstract Class: EdgeBasedContractionScheme
------------------------------------------

.. autoclass:: multilevelgraphs.contraction_schemes.edge_based_contraction_scheme.EdgeBasedContractionScheme
   :members:
   :undoc-members:
   :show-inheritance:

Abstract Class: DecontractionEdgeBasedContractionScheme
-------------------------------------------------------

.. autoclass:: multilevelgraphs.contraction_schemes.decontraction_edge_based_contraction_scheme.DecontractionEdgeBasedContractionScheme
   :members:
   :undoc-members:
   :show-inheritance:

Class: CompTable
----------------

.. autoclass:: multilevelgraphs.contraction_schemes.comp_table.CompTable
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: modified

Class: ComponentSet
-------------------

.. autoclass:: multilevelgraphs.contraction_schemes.component_set.ComponentSet
   :members:
   :undoc-members:
   :exclude-members: key


Class: UpdateQuadruple
----------------------

.. autoclass:: multilevelgraphs.contraction_schemes.update_quadruple.UpdateQuadruple
   :members:
   :undoc-members:
   :show-inheritance:

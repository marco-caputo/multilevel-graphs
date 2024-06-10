from multilevelgraphs import MultilevelGraph, \
    CliquesContractionScheme, SCCsContractionScheme, write_gexf, write_gexf_for_viz
import networkx as nx

if __name__ == '__main__':
    # Create a MultilevelGraph object
    mlg = MultilevelGraph(nx.les_miserables_graph(), [CliquesContractionScheme(), SCCsContractionScheme()])

    mlg.build_contraction_schemes()

    write_gexf(mlg, 'les_miserables.gexf')
    write_gexf_for_viz(mlg, 'les_miserables_for_viz.gexf')

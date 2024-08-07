from multilevelgraphs import MultilevelGraph, \
    CliquesContractionScheme, SCCsContractionScheme, write_gexf, write_gexf_for_viz
import networkx as nx

if __name__ == '__main__':
    from multilevelgraphs.dec_graphs import Supernode

    supernode = Supernode(key=1, level=0, weight=10)

    print(supernode.level)  # 0
    print(supernode['weight'])  # 10
    supernode['weight'] = 20
    print(supernode['weight'])  # 20
    '''
    # Create a MultilevelGraph object
    mlg = MultilevelGraph(nx.les_miserables_graph(), [CliquesContractionScheme(), SCCsContractionScheme()])

    mlg.build_contraction_schemes()

    write_gexf(mlg, 'les_miserables.gexf')
    write_gexf_for_viz(mlg, 'les_miserables_for_viz.gexf')
    '''

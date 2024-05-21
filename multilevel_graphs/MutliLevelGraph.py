import utilities.MultiprocessingUtils as mp
import networkx as nx

class MultiLevelGraph :
    def __init__(self, graph, contractionSchemes):
        self.graph = graph
        self.contractionSchemes = contractionSchemes

    
    def enqueueContractionScheme(self, contractionScheme):
        self.contractionSchemes.append(contractionScheme)

    def reduceContractionScheme(self) -> List[DecGraph]:
        """
        Reduces the graph using the contraction schemes.
        """
        for scheme in self.contractionSchemes:
            # Add an indented block of code here
            pass
            
    @staticmethod
    def naturalTransformation(graph : nx.DiGraph) -> DecGraph:
        """
        Returns the natural transformation of the graph.
        """
        
        vs = mp.ParUtils.par_map(lambda x : Supernode(x[0], ), graph.nodes(data=True))
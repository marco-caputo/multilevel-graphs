class MultiLevelGraph :
    def __init__(self, graph, contractionSchemes):
        self.graph = graph
        self.contractionSchemes = contractionSchemes

    
    def enqueueContractionScheme(self, contractionScheme):
        self.contractionSchemes.append(contractionScheme)

    def reduceContractionScheme(self) -> [DecGraph]:
        """
        Reduces the graph using the contraction schemes.
        """
        for scheme in self.contractionSchemes:
            # Add an indented block of code here
            pass
            
    @staticmethod
    def naturalTransformation(graph) -> DecGraph:
        """
        Returns the natural transformation of the graph.
        """
        with Pool() as p:
            graph.dec = p.map(Supernode.height, graph.V)
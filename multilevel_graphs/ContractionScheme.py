from multiprocessing import Pool

class ContractionScheme:
    def __init__(self, contractionFunction):
        self.contractionFunction = contractionFunction
        self.contractionSetsTable = dict()
        self.supernodeTable = dict()
        self.valid = False

    
    def contract(self, decGraph) -> DecGraph:
        """
        Contracts a supernode using the contraction function.
        :param supernode: the supernode to be contracted
        """        
        self.contractionSetsTable = self.contractionFunction(decGraph)
        """ TODO """
        self.supernodeTable = dict() 
        self.valid = True
        return None
    
    def isValid(self):
        return self.valid
    
    def invalidate(self):
        self.valid = False
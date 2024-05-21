class ContractionScheme:
    def __init__(self, contractionFunction):
        self.contractionFunction = contractionFunction
        self.contractionSetsTable = dict()
        self.supernodeTable = dict()

    def contract(self, decGraph):
        """
        Contracts a supernode using the contraction function.

        :param supernode: the supernode to be contracted
        """
        self.contractionSetsTable = self.contractionFunction(decGraph)
        """ TODO """
        self.supernodeTable = dict() 
from ..model import modelsData

class Modification(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "Multiply"
    
    class Multiply(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Multiply"
    
    class Add(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Add"
    
    class Subtract(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Subtract"
    
    class Divide(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Divide"
    
    class Set(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Set"

from ..model import modelsData
from typing import Optional

class Quality(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> int:
        return 0
    
    class Normal(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 0
    
    class Silver(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 1
    
    class Gold(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 2
    
    class Iridium(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 3

class QuantityModifiers(modelsData):
    def __init__(
        self,
        *,
        Id:str,
        Condition: Optional[str] = None,
        Amount: Optional[float] = None,
        RandomAmount: Optional[list[float]] = None
    ):
        self.Id = Id
        self.Condition = Condition
        self.Amount = Amount
        self.RandomAmount = RandomAmount

class QualityModifierMode(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "Stack"

    class Stack(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "Stack"
    
    class Minimum(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "Minimum"
    
    class Maximum(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "Maximum"
        
class AvailableStockLimit(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "None"
    
    class none(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "None"
    
    class Player(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Player"
    
    class Global(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Global"
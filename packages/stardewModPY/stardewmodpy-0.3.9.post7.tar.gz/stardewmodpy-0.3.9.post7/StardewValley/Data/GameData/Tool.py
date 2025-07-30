from ..model import modelsData

class ToolUpgradeLevel(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> int:
        return 0

    class Normal(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 0
    
    class Copper(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 1
    
    class Steel(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 2
    
    class Gold(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 3
    
    class IridiumTool(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 4
    
    class Bamboo(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 0
    
    class Training(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 1
    
    class Fiberglass(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 2
    
    class IridiumRod(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 3
    
    class AdvancedIridiumRod(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> int:
            return 4

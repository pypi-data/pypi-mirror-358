from ..model import modelsData

class StackSizeVisibility(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "Show"

    class Hide(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "Hide"
    
    class Show(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "Show"
    
    class ShowIfMultiple(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "ShowIfMultiple"

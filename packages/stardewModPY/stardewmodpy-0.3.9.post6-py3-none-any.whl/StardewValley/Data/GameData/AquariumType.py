from ..model import modelsData

class AquariumType(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "eel"
    
    class Eel(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "eel"
    
    class Cephalopod(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "cephalopod"
    
    class Crawl(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "crawl"
    
    class Ground(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "ground"
    
    class Fish(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "fish"
    
    class Front_crawl(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "front_crawl"

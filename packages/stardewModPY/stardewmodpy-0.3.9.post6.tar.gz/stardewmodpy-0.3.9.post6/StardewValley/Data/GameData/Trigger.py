from ..model import modelsData

class Trigger(modelsData):
    def __init__(self):
        pass

    def getJson(self):
        return "DayStarted"
    
    class DayStarted(modelsData):
        def __init__(self):
            pass
        
        def getJson(self):
            return "DayStarted"
    
    class DayEnding(modelsData):
        def __init__(self):
            pass
        
        def getJson(self):
            return "DayEnding"

    class LocationChanged(modelsData):
        def __init__(self):
            pass
        
        def getJson(self):
            return "LocationChanged"
from ..model import modelsData

class Gender(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "Undefined"
    
    class Male(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Male"
    
    class Female(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Female"
    
    class Undefined(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Undefined"

class Age(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "Adult"
    
    class Adult(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Adult"
    class Teen(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Teen"
    
    

class Social(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "Neutral"
    
    class Neutral(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Neutral"
    
class Manner(Social):
    def __init__(self):
        super().__init__()
    
    class Polite(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Polite"
    
    class Rude(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Rude"

class SocialAnxiety(Social):
    def __init__(self):
        super().__init__()
    
    class Outgoing(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Outgoing"
    
    class Shy(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Shy"

class Optimism(Social):
    def __init__(self):
        super().__init__()
    
    class Negative(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Negative"
    
    class Positive(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Positive"


class HomeRegion(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "Other"
    
    class Town(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Town"
    
    class Desert(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Desert"

    class Other(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Other"


class Calendar(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "AlwaysShown"
    
    
    
    class HiddenAlways(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "HiddenAlways"
    
    class HiddenUntilMet(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "HiddenUntilMet"
    
    class AlwaysShown(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "AlwaysShown"
        

class SocialTab(Calendar):
    def __init__(self):
        super().__init__()
    
    class UnknownUntilMet(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "UnknownUntilMet"


class EndSlideShow(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "MainGroup"
    
    class Hidden(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "Hidden"
        
    class MainGroup(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "MainGroup"
    

    class TrailingGroup(modelsData):
        def __init__(self):
            pass
        
        def getJson(self) -> str:
            return "TrailingGroup"
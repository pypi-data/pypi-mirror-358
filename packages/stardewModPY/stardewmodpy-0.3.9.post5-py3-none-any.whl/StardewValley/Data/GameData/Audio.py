from ..model import modelsData
from typing import Optional

class Music(modelsData):
    def __init__(
        self,
        Track: str,
        Id: Optional[str] = None,
        Condition: Optional[str] = None
    ):
        self.Track = Track
        self.Id = Id
        self.Condition = Condition

class MusicContext(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "Default"

    class Default(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "Default"

    class SubLocation(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "SubLocation"
           
class AudioCategory(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "Default"
    
    class Default(modelsData):
        def __init__(self):
            pass
        def getJson(self) -> str:
            return "Default"
    
    class Music(modelsData):
        def __init__(self):
            pass
        def getJson(self) -> str:
            return "Music"
    
    class Sound(modelsData):
        def __init__(self):
            pass
        def getJson(self) -> str:
            return "Sound"
    
    class Ambient(modelsData):
        def __init__(self):
            pass
        def getJson(self) -> str:
            return "Ambient"
    
    class Footsteps(modelsData):
        def __init__(self):
            pass
        def getJson(self) -> str:
            return "Footsteps"

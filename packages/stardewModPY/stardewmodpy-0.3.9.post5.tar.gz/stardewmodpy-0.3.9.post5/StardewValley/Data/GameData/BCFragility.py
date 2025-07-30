from ..model import modelsData

class BCFragility(modelsData):
    def __init__(self, fragility:int):
        if fragility < 0 or fragility > 2:
            raise ValueError("The possible values are 0 (pick up with any tool), 1 (destroyed if hit with an axe/hoe/pickaxe, or picked up with any other tool), or 2 (can't be removed once placed). Default 0.")
        self.fragility = fragility

    def getJson(self) -> int:
        return self.fragility

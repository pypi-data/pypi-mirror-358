class Season:
    def __init__(self, lower: bool = False):
        self.lower = lower
        self_outer = self

        seasons = ["Spring", "Summer", "Fall", "Winter"]

        for season_name in seasons:
            def make_init(self_outer):
                return lambda self: setattr(self, "_outer", self_outer)

            def make_getJson(season_name):
                return lambda self: season_name.lower() if self._outer.lower else season_name

            cls = type(
                season_name,
                (object,),
                {
                    "__init__": make_init(self_outer),
                    "getJson": make_getJson(season_name),
                    "__repr__": lambda self, name=season_name: f"<{name}>"
                }
            )

            setattr(self, season_name, cls())

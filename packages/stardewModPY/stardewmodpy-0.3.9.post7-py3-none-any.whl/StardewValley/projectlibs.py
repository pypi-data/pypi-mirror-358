import os, re


class colorize:
    def __init__(self):
        self.black=30
        self.red=31
        self.green=32
        self.yellow=33
        self.blue=34
        self.magenta=35
        self.cyan=36
        self.white=37
    
    def colorize(self, color:int):
        return f"\033[{color}m"
    def reset(self):
        return "\033[0m"

class libModel:
    def __init__(self, optionals: dict, modName: str):
        self.optionals=optionals
        self.modName=modName
        self.imports=""
        self.implements=""
        self.classData=""

        self.classFileData=""
        self.classFileData_imports=""
        self.classFileData_Father=""
        self.classFileData_params=""
        self.classFileData_contents=""

        self.import_file="__init__.py"

        self.corrects={
            "Maps":"Maps",
            "NPCS":"NPCs",
            "Dialogues":"Dialogues",
            "Events":"Events",
            "Schedules":"Schedules"
        }
        
    def write_file(self, path, content):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    def contents(self):
        if self.optionals[self.corrects[self.__class__.__name__]]:
            os.makedirs(os.path.join(self.modName, self.__class__.__name__), exist_ok=True)
            file_init=os.path.join(self.modName, self.__class__.__name__, self.import_file)
            if not os.path.isfile(file_init):
                self.write_file(file_init, self.classData)
    
    

    

    def add_item(self, item_name: str):
        self.contents()
        function_name = self.corrects[self.__class__.__name__]
        file_path = os.path.join(self.modName, "ModEntry.py")

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        new_lines = []
        addItem_new = False
        item_already_added = False

        for i, line in enumerate(lines):
            stripped = line.strip()
            indent = line[:len(line) - len(line.lstrip())]

            if addItem_new:
                if stripped == f"{function_name}_List.{item_name}()," or stripped == f"{function_name}_List.{item_name}()":
                    item_already_added = True
                    addItem_new = False
                    print("⚠️ Item already added")
                    new_lines.append(line)
                elif stripped == "]),":
                    if not item_already_added:
                        # Verifica se a linha anterior termina com vírgula
                        if new_lines and not new_lines[-1].rstrip().endswith(","):
                            new_lines[-1] = new_lines[-1].rstrip() + ",\n"
                        new_lines.append(f"{indent}    {function_name}_List.{item_name}(),\n")
                        item_already_added = True
                        self.add_import(item_name)
                    new_lines.append(line)
                    addItem_new = False
                else:
                    new_lines.append(line)

            elif f"{function_name}(mod=self" in stripped and f"{function_name}_List=[]" in stripped:
                print("Criando primeiro item")
                new_lines.append(f"{indent}{function_name}(mod=self, {function_name}_List=[\n")
                new_lines.append(f"{indent}    {function_name}_List.{item_name}(),\n")
                new_lines.append(f"{indent}]),\n")
                self.add_import(item_name)
            elif stripped == f"{function_name}(mod=self, {function_name}_List=[":
                new_lines.append(line)
                addItem_new = True
                item_already_added = False
            else:
                new_lines.append(line)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)



    def add_import(self, name:str):
        importFile=os.path.join(self.modName, self.__class__.__name__, self.import_file)
        with open(importFile, 'a', encoding='utf-8') as f:
            f.write(f"\nfrom NPCS.{name} import {name}\n")

        newFile=os.path.join(self.modName, self.__class__.__name__, name+".py")
        self.buildClassData(name)
        with open(newFile, 'w', encoding='utf-8') as f:
            f.write(self.classFileData)
    
    def buildClassData(self, name):
        self.classFileData=f"""{self.classFileData_imports}

class {name}{self.classFileData_Father}:
    def __init__(self{self.classFileData_params}):
        {self.classFileData_contents.replace("###name###", name)}"""


class Maps(libModel):
    def __init__(self, optionals: dict, modName: str):
        super().__init__(optionals, modName)
        self.imports="from Maps.Maps import Maps" if self.optionals["Maps"] else ""
        
        self.implements="Maps(self)" if self.optionals["Maps"] else ""

        self.classData=f"""from StardewValley.Data.SVModels import Maps as MapsModel
from StardewValley import Helper

class Maps(MapsModel):
    def __init__(self, mod: Helper):
        super().__init__(mod)
        self.mod.assetsFileIgnore=[]
    
    def contents(self):
        super().contents()

"""
        self.import_file="Maps.py"
        self.classFileData_imports="""from StardewValley.Data.SVModels.svmodel import svmodel
from StardewValley.Data.SVModels.mapsModel import MapsModel
from StardewValley.Data import LocationsData"""

        self.classFileData_Father="(MapsModel)"
        self.classFileData_params="*, maps: svmodel"
        
    def add_import(self, name):
        pass

    def buildClassData(self, name):
        self.classFileData=f"""{self.classFileData_imports}

class {name}{self.classFileData_Father}:
    def __init__(self{self.classFileData_params}):
        super().__init__(map_name="{name}", map_file="assets/Maps/{name}.tmx", maps=maps)
        
    def contents(self):
        super().contents()

        LocationsData(
            key=self.map_name,
            DisplayName={name},
            DefaultArrivalTile={"X": 16, "Y": 16},
            CreateOnLoad={"MapPath": f"Maps/{self.map_name}", "AlwaysActive":True},
            FormerLocationNames=[f"Custom_{self.map_name}"],
        ).register(
            LogName=f"Add Location {self.map_name}", 
            Target="Data/Locations",
            mod=self.maps.mod,
            contentFile=self.maps.__class__.__name__
        )
"""

class NPCS(libModel):
    def __init__(self, optionals, modName):
        super().__init__(optionals, modName)

        self.imports="""import NPCS as NPCs_List
from StardewValley.Data.SVModels.NPCs import NPCs
"""
        
        self.implements="NPCs(mod=self, NPCs_List=[])" if self.optionals["NPCs"] else ""

        self.classFileData_imports="""from StardewValley.Data import CharactersData, Home, Gender, Age, Manner, SocialAnxiety, Optimism, Season
from StardewValley.Data.XNA import Position
"""
        self.classFileData_Father="(CharactersData)"
        self.classFileData_contents="""self.key=###name###
        self.DisplayName=###name###
        self.Gender=Gender.Undefined
        self.Age=Age.Adult
        self.Manner=Manner.Neutral
        #self.SocialAnxiety=SocialAnxiety.Neutral
        self.Optimism=Optimism.Neutral
        self.BirthSeason=Season(lower=True).Spring
        self.BirthDay=1
        self.HomeRegion="Town"
        self.CanBeRomanced=False
        self.Home=[
            Home(
                Id="###name###House",
                Tile=Position(10, 10),
                Direction="right",
                Location="Town"
            ).getJson()
        ]"""
    

class Dialogues(libModel):
    def __init__(self, optionals, modName):
        super().__init__(optionals, modName)

        self.imports="""import Dialogues as Dialogues_List
from StardewValley.Data.SVModels.Dialogues import Dialogues
""" if self.optionals["Dialogues"] else ""

        self.implements="Dialogues(mod=self, Dialogues_List=[])" if self.optionals["Dialogues"] else ""

        self.classFileData_imports="""from StardewValley.Data import modelsData
"""
        self.classFileData_Father="(modelsData)"
        self.classFileData_contents="""self.Introduction = ""
        self.FlowerDance_Accept = ""
        self.AcceptBirthdayGift_Positive = ""
        self.AcceptBirthdayGift_Negative = ""
        self.GreenRain = ""
        self.GreenRainFinished = ""
        self.GreenRain_2 = ""
        self.Mon = ""
        self.Tue = ""
        self.Wed = ""
        self.Thu = ""
        self.Fri = ""
        self.Sat = ""
        self.Sun = ""
        """

class Schedules(libModel):
    def __init__(self, optionals, modName):
        super().__init__(optionals, modName)

        self.imports="""import Schedules as Schedules_List
from StardewValley.Data.SVModels.Schedules import Schedules
""" if self.optionals["Schedules"] else ""

        self.implements="Schedules(mod=self, Schedules_List=[])" if self.optionals["Schedules"] else ""

        self.classFileData_imports="""from StardewValley.Characters import scheduleData, scheduleValueData
        """
        
        self.classFileData_contents="""self.json={}

        self.json["spring"]=scheduleData(
            [
                scheduleValueData(
                    time=1000,
                    location="Town",
                    tileX=130,
                    tileY=150,
                    facingDirection=2
                )
            ]
        ).getJson()"""

class Events(libModel):
    def __init__(self, optionals, modName):
        super().__init__(optionals, modName)

        self.imports="""import Events as Events_list
from StardewValley.Data.SVModels.Events import Events
""" if self.optionals["Events"] else ""
        
        self.implements="Events(mod=self, Events_list=[])" if self.optionals["Events"] else ""

        self.classFileData_imports="""from StardewValley.Data import EventData, Eventscripts, Precondition, CharacterID"""

        self.classFileData_Father="(EventData)"
        self.classFileData_contents="""self.key=Precondition(
            ID="###name###",
            ...
        )
        self.value=Eventscripts(
            music="jingleBell",
            coordinates=(0, 0),
            characterID=[
                CharacterID("farmer", 0, 0, "2"),
                CharacterID("###name###", 0, 5, "2")
            ]
        )
        self.value.skippable()
        self.value.pause(1500)
        self.value.end()
        self.location="Farm"
        """

class ExtraContents:
    def __init__(self, optionals, modName):
        self.optionals=optionals
        self.modName=modName

        self.Dialogues=None
        self.Maps=None
        self.Events=None
        self.NPCS=None
        self.Schedules=None

        if self.optionals["Dialogues"]:
            self.Dialogues=Dialogues(optionals, modName)
            self.Dialogues.contents()
        if self.optionals["Maps"]:
            self.Maps=Maps(optionals, modName)
            self.Maps.contents()
        if self.optionals["Events"]:
            self.Events= Events(optionals, modName)
            self.Events.contents()
        if self.optionals["NPCs"]:
            self.NPCS=NPCS(optionals, modName)
            self.NPCS.contents()
        if self.optionals["Schedules"]:
            self.Schedules=Schedules(optionals, modName)
            self.Schedules.contents()



    
    def saveEntry(self):
        mod_entry_path = os.path.join(self.modName, "ModEntry.py")
        framework_content=""
        framework_content_import=""
        if self.optionals["framework"] is not None:
            framework_content=f", modFramework={self.optionals['framework']}(manifest=manifest)"
            framework_content_import=f", {self.optionals['framework']}"
        
        imports=[]
        implements=[]

        if self.Dialogues is not None:
            imports.append(self.Dialogues.imports)
            implements.append(self.Dialogues.implements)
        if self.Maps is not None:
            imports.append(self.Maps.imports)
            implements.append(self.Maps.implements)
        if self.Events is not None:
            imports.append(self.Events.imports)
            implements.append(self.Events.implements)
        if self.NPCS is not None:
            imports.append(self.NPCS.imports)
            implements.append(self.NPCS.implements)
        if self.Schedules is not None:
            imports.append(self.Schedules.imports)
            implements.append(self.Schedules.implements)

        content = f"""from StardewValley import Manifest
from StardewValley.helper import Helper{framework_content_import}

{"\n\n".join(imports)}

class ModEntry(Helper):
    def __init__(self, manifest:Manifest):
        super().__init__(
            manifest=manifest{framework_content}
        )
        self.contents()
    
    def contents(self):
        # Add your contents here
        {",\n\n        ".join(implements)}
"""
        with open(mod_entry_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    def saveMain(self, author:str, version:str, description:str):
        main_path = os.path.join(self.modName, "main.py")
        mainContent=f"""from ModEntry import ModEntry
from StardewValley import Manifest

manifest=Manifest(
    Name="{self.modName}",
    Author="{author}",
    Version="{version}",
    Description="{description}",
    UniqueID="{author}.{self.modName}"
)
mod=ModEntry(manifest=manifest)

mod.write()
"""
        with open(main_path, "w", encoding="utf-8") as f:
            f.write(mainContent)
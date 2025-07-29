from src.generic_classes.space import Space
from src.spaces.Ge import Ge


class TheScorers(Space):
    def __init__(self):
        super().__init__()
        self["_name"] = "Sc"
        self["_modified"] = []  # Track modified attributes


    def getFilePath(self, elemName: str, basename: str = "autotopas") -> str:
        return Ge.getFilePath(Sc[elemName].Component, basename)


    def dumpToFile(self, basename="autotopas"):
        for elemName in self["_modified"]:
            self[elemName].dumpToFile(elemName, 
                                      space_name=self["_name"],
                                      filename=self.getFilePath(elemName, basename=basename))




def setScDefaults(Sc):
    Sc.AddUnitEvenIfItIsOne = False # If unit is 1, rather than, say, Gy, default is to leave out unit in header.
    Sc.RootFileName = "topas" # name for root output files
    Sc.XmlFileName = "topas" # name for xml output files



Sc = TheScorers()
Sc.Name = "Sc"
setScDefaults(Sc)

Sc["_modified"] = []
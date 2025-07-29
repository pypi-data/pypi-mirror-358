from src.generic_classes.space import Space
import quantities as q
from src.spaces.Ge import Ge
from src.printing import writeVal

class TheSources(Space):
    def __init__(self):
        super().__init__()
        self["_name"] = "So"
        self["_modified"] = []  # Track modified attributes


    def getFilePath(self, elemName: str, basename: str = "autotopas") -> str:
        return Ge.getFilePath(So[elemName].Component, basename)

    def dumpToFile(self, basename="autotopas"):

        for elemName in self["_modified"]:
            filepath = self.getFilePath(elemName, basename=basename)

            if hasattr(self[elemName], "dumpToFile"):
                self[elemName].dumpToFile(elemName, 
                                        space_name=self["_name"],
                                        filename=filepath)
            else:
                with open(filepath, "a+") as f:
                    writeVal(f, 
                             space_name=self["_name"],
                             elemName=elemName,
                             key=None,
                             value=self[elemName])



def setSoDefaults(So):
    pass


So = TheSources()
So.Name = "So"
setSoDefaults(So)

So._modified = []
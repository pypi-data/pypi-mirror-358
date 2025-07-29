from src.spaces.Ge import Ge
from src.generic_classes.element import Element
from quantities import cm, deg, m
from rich import print as rprint
from rich.text import Text
from rich.tree import Tree
from src.printing import writeVal
import os
import quantities as q

class GElement(Element):
    def __init__(self):
        super().__init__()
        self.Parent = "World"
        self.Type = ""

        self.Material = "Air" # If material is None, component is parallel
        self.IsParallel = False

        self.TransX = 0.0 * cm
        self.TransY = 0.0 * cm
        self.TransZ = 0.0 * cm

        self.RotX = 0.0 * deg
        self.RotY = 0.0 * deg
        self.RotZ = 0.0 * deg

        self.Color = "White"
        self.IsVisible = True  # Default visibility is True
        self.DrawingStyle = "Solid"

        self["_modified"] = []

    def _GetRelPosAlongAxis(self, axis):
        if axis == 'X':
            return self.TransX
        elif axis == 'Y':
            return self.TransY
        elif axis == 'Z':
            return self.TransZ
        else:
            raise ValueError("Axis must be 'X', 'Y', or 'Z'")
        
    def _GetAbsPosAlongAxis(self, axis):
        if self.Parent == "World":
            return self._GetRelPosAlongAxis(axis)
        
        result = self._GetRelPosAlongAxis(axis)
        parent = self.Parent
        while parent != "World":
            result += Ge[parent]._GetRelPosAlongAxis(axis)
            parent = Ge[parent].Parent

        return result
        
    def AbsPosX(self):
        return self._GetAbsPosAlongAxis('X')
    def AbsPosY(self):
        return self._GetAbsPosAlongAxis('Y')
    def AbsPosZ(self):
        return self._GetAbsPosAlongAxis('Z')
    
    
    def getChainAbove(self, res_so_far=None):
        if res_so_far is None:
            res_so_far = []
        
        if self.Parent is None:
            return res_so_far
        
        res_so_far += [self.Parent]

        chain = Ge[self.Parent].getChainAbove(res_so_far)
        chain.reverse()
        return chain
    
    def printChainAbove(self):
        
        tree = Tree(Text("🌏 World", "bold magenta"), guide_style="bold bright_blue")
        for item in self.getChainAbove():
            if item == "World":
                continue
            else:
                txt = getElemLabel(item)                
            try:
                leaf = leaf.add(txt)
            except NameError:
                leaf = tree.add(txt)
        rprint(tree)

    def dumpToFile(self, elemName, space_name, filename, print_children=False):
        dirmap = Ge["_dirmap"]
        filenamemap = Ge["_filenamemap"]
        keys = sorted(self["_modified"], key=getOrder)
        if "Type" not in keys:
            keys = ["Type"] + keys
        if "Parent" not in keys:
            keys = ["Parent"] + keys
        
        with open(filename, "a") as f:
            for key in keys:
                value = self[key]
                if elemName == "World" and key == "Parent":
                    continue
                writeVal(f, 
                         space_name=space_name,
                         elemName=elemName, 
                         key=key, 
                         value=value)


            for child in Ge["_tree"].find(elemName).children:
                child_filename = f"{dirmap[child]}{filenamemap[child]}"
                if filename != child_filename:
                    f.write(f"includeFile = {child_filename}\n")
            if print_children:
                children = Ge.getChildrenOf(elemName)
                if len(children) > 0:
                    f.write("# Children: [")

                    for child in children:
                        f.write(f"{child}")
                        if child != children[-1]:
                            f.write(", ")
                        if child == children[-1]:
                            f.write("]\n")

            f.write("\n\n")


        # TODO: check if the element has scorers or sources as children
        # and if so, write them to the file



def getOrder(key):
    order = {
        "Type": 0,
        "Parent": 1,
        "Material": 2,
        "IsParallel": 3,
        "TransX": 4,
        "TransY": 5,
        "TransZ": 6,
        "RotX": 7,
        "RotY": 8,
        "RotZ": 9,
        "Color": 10
    }
    return order.get(key, len(order.keys()))  # Default to a large number if key is not found


class TsCylinder(GElement):
    def __init__(self):
        super().__init__()

        self.Type = "TsCylinder"
        self.RMin = 0.0 * cm  # Radius of the cylinder
        self.RMax = 0.0 * cm  # Radius of the cylinder
        self.HL = 0.0 * cm     # Half Length in Z
        self.SPhi = 0.0 * deg    # Starting angle in phi
        self.DPhi = 360.0 * deg  # Total angle in phi
        # self["_modified"] = []



class TsBox(GElement):
    def __init__(self):
        super().__init__()

        self.Type = "TsBox"
        self.HLX = 0.0 * cm  # Half Length in X
        self.HLY = 0.0 * cm  # Half Length in Y
        self.HLZ = 0.0 * cm  # Half Length in Z
        self["_modified"] = []

    def set_dimensions_cm(self, LX, LY, LZ):
        self.HLX = LX * q.cm/ 2.0
        self.HLY = LY * q.cm / 2.0
        self.HLZ = LZ * q.cm / 2.0
    
    def set_half_dimensions_cm(self, HLX, HLY, HLZ):
        self.HLX = HLX * q.cm
        self.HLY = HLY * q.cm
        self.HLZ = HLZ * q.cm

    def LX(self):
        return 2.0 * self.HLX
    def LY(self):
        return 2.0 * self.HLY
    def LZ(self):
        return 2.0 * self.HLZ
    

class VizComponent(TsBox):
    def __init__(self):
        super().__init__()
        self.Type = "TsBox"
        self.Parent = "World"  # Default parent is World
        self.Material = "Air"  # Default material is Air
        self.Color = "Red"  # Default color for visualization
        self.HLX = 10 * cm
        self.HLY = 10 * cm
        self.HLZ = 1 * q.nm
        self["_modified"] = ["Type", "Parent", "Material", "Color", 
                             "HLX", "HLY", "HLZ"]

class G4Cons(GElement):
    def __init__(self):
        super().__init__()

        # self["_modified"] = []
        self.Type = "G4Cons"
        self.RMin1 = 0.0 * cm  # Inner radius at the first face
        self.RMax1 = 0.0 * cm  # Outer radius at the first face
        self.RMin2 = 0.0 * cm  # Inner radius at the second face
        self.RMax2 = 0.0 * cm  # Outer radius at the second face
        self.HL = 0.0 * cm     # Half Length in Z
        self.SPhi = 0.0 * deg   # Starting angle in phi
        self.DPhi = 360.0 * deg # Total angle in phi

    
class TsJaws(GElement):
    def __init__(self):
        super().__init__()

        self.Type = "TsJaws"
        self.JawTravelAxis = "X"
        self.PositiveFieldSetting = 0.0 * cm
        self.NegativeFieldSetting = 0.0 * cm
        self.LX = 0.0 * cm  # Length in X
        self.LY = 0.0 * cm  # Length in Y
        self.LZ = 0.0 * cm  # Length in Z
        self.SourceToUpstreamSurfaceDistance = 0.0 * cm  # Distance from source to upstream surface
        self.SAD = 0.0 * cm  # Source to Axis Distance
        self["_modified"] = []

class G4Trd(GElement):
    def __init__(self):
        super().__init__()

        self.Type = "G4Trd"
        self.HLX1 = 0.0 * cm  # Half Length in X for the first face
        self.HLX2 = 0.0 * cm  # Half Length in X for the second face
        self.HLY1 = 0.0 * cm  # Half Length in Y for the first face
        self.HLY2 = 0.0 * cm  # Half Length in Y for the second face
        self.HLZ = 0.0 * cm   # Half Length in Z
        self["_modified"] = []


class Group(GElement):
    def __init__(self, expand=True):
        super().__init__()
        self.Type = "Group"
        self.Parent = "World"  # Default parent is World

        self["_modified"] = []
        self["_expand"] = expand  # Whether to create a separate file for each child

def getElemLabel(elem):
    if Ge.getChildrenOf(elem) == []:
        txt = Text(f"📦 {elem}", "bold cyan")
    elif isinstance(Ge[elem], Group):
        txt = Text(f"🗂️  {elem}", "bold green")
    elif len(Ge.getChildrenOf(elem)) > 0:
        txt = Text(f"📂 {elem}", "bold cyan")
    
    txt.append(f" ({len(Ge[elem]['_modified'])})", "black")

    return txt





Ge.World = TsBox()
Ge.World.Parent = None
Ge.World.HLX = 5. * m
Ge.World.HLY = 5. * m
Ge.World.HLZ = 5. * m
Ge.World["_modified"] = []

Ge.BeamPosition.Parent = "World"
Ge.BeamPosition.Type = "Group"
Ge.BeamPosition.TransX = 0. * m
Ge.BeamPosition.TransY = 0. * m
Ge.BeamPosition.TransZ =  Ge.World.HLZ * m
Ge.BeamPosition.RotX = 180. * deg
Ge.BeamPosition.RotY = 0. * deg
Ge.BeamPosition.RotZ = 0. * deg
Ge.BeamPosition["_modified"] = []

Ge["_modified"] = []
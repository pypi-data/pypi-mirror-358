from src.generic_classes.space import Space
import re
def setGrDefaults(Gr):
    Gr.Enable = True # Set False to avoid instantiating any part of Geant4 visualization system (useful for running on batch machines that lack the OpenGL graphics library)
    Gr.Verbosity = 0 # Set to higher integer to increase verbosity of Geant4 visualization system
    Gr.RefreshEvery = "Run" # "History", "Run" or "Session"
    Gr.ShowOnlyOutlineIfVoxelCountExceeds = 8000 # Above this limit, only show outer box
    Gr.SwitchOGLtoOGLIifVoxelCountExceeds = 70000000 # Above this limit, switch OpenGL Graphics to Immediate mode


    Gr.Color.White =     [255, 255, 255]
    Gr.Color.Silver =    [191, 191, 191]
    Gr.Color.Gray =      [127, 127, 127]
    Gr.Color.Grey =      [127, 127, 127]
    Gr.Color.Black =     [0, 0, 0]
    Gr.Color.Red =       [255, 0, 0]
    Gr.Color.Maroon =    [127, 0, 0]
    Gr.Color.Yellow =    [255, 255, 0]
    Gr.Color.Olive =     [127, 127, 0]
    Gr.Color.Lime =      [0, 255, 0]
    Gr.Color.Green =     [0, 127, 0]
    Gr.Color.Aqua =      [0, 255, 255]
    Gr.Color.Teal =      [0, 127, 127]
    Gr.Color.Blue =      [0, 0, 255]
    Gr.Color.Navy =      [0, 0, 127]
    Gr.Color.Fuchsia =   [255, 0, 255]
    Gr.Color.Purple =    [127, 0, 127]

    Gr.Color.Lightblue = [175, 255, 255]
    Gr.Color.Skyblue =   [175, 124, 255]
    Gr.Color.Magenta =   [255, 0, 255]
    Gr.Color.Violet =    [224, 0, 255]
    Gr.Color.Pink =      [255, 0, 222]
    Gr.Color.Indigo =    [0, 0, 190]
    Gr.Color.Grass =     [0, 239, 0]
    Gr.Color.Orange =    [241, 224, 0]
    Gr.Color.Brown =     [225, 126, 66]

    Gr.Color.grey020 =   [20, 20, 20]
    Gr.Color.grey040 =   [40, 40, 40]
    Gr.Color.grey060 =   [60, 60, 60]
    Gr.Color.grey080 =   [80, 80, 80]
    Gr.Color.grey100 =   [100, 100, 100]
    Gr.Color.grey120 =   [120, 120, 120]
    Gr.Color.grey140 =   [140, 140, 140]
    Gr.Color.grey160 =   [160, 160, 160]
    Gr.Color.grey180 =   [180, 180, 180]
    Gr.Color.grey200 =   [200, 200, 200]
    Gr.Color.grey220 =   [220, 220, 220]
    Gr.Color.grey240 =   [240, 240, 240]


class TheGraphics(Space):
    def __init__(self):
        super().__init__()
        self["_name"] = "Gr"
        self["_enable"] = True  # Enable or disable Geant4 visualization
        self["_modified"] = []  # Track modified attributes

    def enable(self):
        """Enable Geant4 visualization."""
        self["_enable"] = True
    def disable(self):
        """Disable Geant4 visualization."""
        self["_enable"] = False
    
    def dumpToFile(self, basename="autotopas", method="bool"):
        
        if method == "bool" and self["_enable"]:
            with open(f"{basename}/main.in", "a+") as f:
                res = """
                        b:Gr/Main/Enable              = "True"
                        s:Gr/Main/Type                = "OpenGL"
                        i:Gr/Main/WindowSizeX         = 500
                        i:Gr/Main/WindowSizeY         = 500
                        b:Ts/UseQt                    = "True"
                        b:Gr/Main/IncludeGeometry     = "True"
                        b:Gr/Main/IncludeTrajectories = "True"
                        b:Gr/Main/IncludeStepPoints   = "True"
                        b:Gr/Main/IncludeAxes         = "False"
                        """
                res = re.sub(r"[ ]+", " ", res)  # Remove extra whitespace
                res = re.sub(r"\n\s*", "\n", res)
                f.write(res)
        elif method != "bool":
            super().dumpToFile(basename=basename)


Gr = TheGraphics()
setGrDefaults(Gr)

Gr.Verbosity         = 0


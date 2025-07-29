from src.generic_classes.element import Element
from quantities import cm, deg, MeV, rad
from src.geometry import Ge
from src.spaces.So import So
from src.printing import writeVal

class Source(Element):
    def __init__(self):
        super().__init__()
      
        self.Type = "Beam" # Beam, Isotropic, Emittance or PhaseSpace
        self.Component = "BeamPosition"
        self.NumberOfHistoriesInRun = 0

        self["_modified"] = []

        


    def dumpToFile(self, elemName, space_name, filename):
        keys = sorted(self["_modified"], key=getOrder)
        if "Type" not in keys:
            keys = ["Type"] + keys

        with open(filename, "a") as f:
            for key in keys:
                value = self[key]
                writeVal(f, 
                         space_name=space_name, 
                         elemName=elemName, 
                         key=key, 
                         value=value)
            
            f.write("\n\n")





class Beam(Source):
    def __init__(self):
        super().__init__()

        self.Component = "DefaultBeamComponent"
        self.Type = "Beam" # Beam, Isotropic, Emittance or PhaseSpace
        self.BeamParticle = "proton"
        self.BeamEnergy = 169.23 * MeV
        self.BeamEnergySpread = 0.757504

        self.BeamPositionCutoffShape = "Ellipse" # Rectangle or Ellipse
        self.BeamPositionCutoffX = 10. * cm # X extent of position 
        self.BeamPositionCutoffY = 10. * cm
        
        self.BeamPositionDistribution = "Flat"
        self.BeamPositionSpreadX = 0.65 * cm # distribution (if Gaussian)
        self.BeamPositionSpreadY = 0.65 * cm # distribution (if Gaussian)
        
        self.BeamAngularDistribution = "Gaussian" # None, Flat or Gaussian
        self.BeamAngularCutoffX = 90. * deg # X cutoff of angular distrib (if Flat or Gaussian)
        self.BeamAngularCutoffY = 90. * deg # Y cutoff of angular distrib (if Flat or Gaussian)
        self.BeamAngularSpreadX = 0.0032 * rad # X angular distribution (if Gaussian)
        self.BeamAngularSpreadY = 0.0032 * rad # Y angular distribution (if Gaussian)

        self["_modified"] = []


        self.Verbosity = 0  # Verbosity level for the source

class PhaseSpaceSource(Source):
    def __init__(self):
        super().__init__()

        self.Type = "PhaseSpace" # Beam, Isotropic, Emittance or PhaseSpace
        self.PhaseSpaceFileName = ""

        self["_modified"] = []

        self.Verbosity = 0  # Verbosity level for the source


def getOrder(key):
    order = {
        "Type": 0,
        "PhaseSpaceFileName": 1,
        "BeamParticle": 2,
        "BeamEnergy": 3,
    }
    return order.get(key, len(order.keys()))  # Default order for unspecified keys


So.Demo = Beam()
So.Demo.NumberOfHistoriesInRandomJob = 0
So.Demo["_modified"] = []

So["_modified"] = []
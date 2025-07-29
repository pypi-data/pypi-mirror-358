from src.spaces.Sc import Sc
from src.generic_classes.element import Element


class Scorer(Element):
    def __init__(self):
        super().__init__()

        self.Quantity = "Dose"  # Dose, Energy, ParticleCount, etc.
        self.Component = "World"

        self["_modified"] = []  # Track modified attributes



class PhaseSpaceScorer(Scorer):
    def __init__(self):
        super().__init__()

        self.Quantity = "PhaseSpace"  # PhaseSpace, Energy, ParticleCount, etc.
        self.Surface = "World/ZPlusSurface"  # Surface to score on
        self.OutputType = "Binary"  # Output type: Binary, Text, etc.
        self.OutputToConsole = False
        self.IfOutputFileAlreadyExists = "Overwrite"  # Action if output file already exists: Overwrite, Append, Skip
from src.generic_classes.space import Space
import quantities as q

def setMaDefaults(Ma):
    Ma.DefaultColor = "white"
    Ma.Verbosity = 0 # Set to 1 to report each time a material is defined

    Ma.Vacuum.Components = ["Carbon", "Nitrogen", "Oxygen", "Argon"]
    Ma.Vacuum.Fractions = [0.000124, 0.755268, 0.231781, 0.012827]
    Ma.Vacuum.Density = 1.0E-25 * q.g / (q.cm**3)
    Ma.Vacuum.State = "Gas"
    Ma.Vacuum.Temperature = 2.73 * q.kelvin
    Ma.Vacuum.Pressure = 3.0E-18 * q.pascal
    Ma.Vacuum.DefaultColor = "skyblue"

    Ma.Carbon.Components = ["Carbon"]
    Ma.Carbon.Fractions = [1.0]
    Ma.Carbon.Density = 1.867 * q.g / (q.cm**3)
    Ma.Carbon.MeanExcitationEnergy = 78 * q.eV
    Ma.Carbon.DefaultColor = "green"

    Ma.Aluminum.Components = ["Aluminum"]
    Ma.Aluminum.Fractions = [1.0]
    Ma.Aluminum.Density = 2.6989 * q.g / (q.cm**3)
    Ma.Aluminum.DefaultColor = "skyblue"
    Ma.Aluminum.AtomicNumber =  13
    Ma.Aluminum.AtomicMass = 26.98154 * q.g / q.mol

    Ma.Nickel.Components = ["Nickel"]
    Ma.Nickel.Fractions = [1.0]
    Ma.Nickel.Density = 8.902 * q.g / (q.cm**3)
    Ma.Nickel.DefaultColor = "indigo"

    Ma.Copper.Components = ["Copper"]
    Ma.Copper.Fractions = [1.0]
    Ma.Copper.Density = 8.96 * q.g / (q.cm**3)
    Ma.Copper.DefaultColor = "orange"

    Ma.Iron.Components = ["Iron"]
    Ma.Iron.Fractions = [1.0]
    Ma.Iron.Density = 7.87 * q.g / (q.cm**3)
    Ma.Iron.DefaultColor = "skyblue"

    Ma.Tantalum.Components = ["Tantalum"]
    Ma.Tantalum.Fractions = [1.0]
    Ma.Tantalum.Density = 16.654 * q.g / (q.cm**3)
    Ma.Tantalum.DefaultColor = "indigo"

    Ma.Lead.Components = ["Lead"]
    Ma.Lead.Fractions = [1.0]
    Ma.Lead.Density = 11.35 * q.g / (q.cm**3)
    Ma.Lead.AtomicNumber =  82
    Ma.Lead.AtomicMass = 207.19 * q.g / q.mol
    Ma.Lead.MeanExcitationEnergy = 823 * q.eV
    Ma.Lead.DefaultColor = "brown"

    Ma.Air.Components = ["Carbon", "Nitrogen", "Oxygen", "Argon"]
    Ma.Air.Fractions = [0.000124, 0.755268, 0.231781, 0.012827]
    Ma.Air.Density = 1.20484 * q.g / (q.cm**3)
    Ma.Air.MeanExcitationEnergy = 85.7 * q.eV
    Ma.Air.DefaultColor = "lightblue"

    Ma.Brass.Components = ["Copper", "Zinc"]
    Ma.Brass.Fractions = [0.7, 0.3]
    Ma.Brass.Density = 8.550 * q.g / (q.cm**3)
    Ma.Brass.MeanExcitationEnergy = 324.4 * q.eV
    Ma.Brass.DefaultColor = "grass"

    Ma.Lexan.Components = ["Hydrogen", "Carbon", "Oxygen"]
    Ma.Lexan.Fractions = [0.055491, 0.755751, 0.188758]
    Ma.Lexan.Density = 1.2 * q.g / (q.cm**3)
    Ma.Lexan.MeanExcitationEnergy = 73.1 * q.eV
    Ma.Lexan.DefaultColor = "grey"

    Ma.Lucite.Components = ["Hydrogen", "Carbon", "Oxygen"]
    Ma.Lucite.Fractions = [0.080538, 0.599848, 0.319614]
    Ma.Lucite.Density = 1.190 * q.g / (q.cm**3)
    Ma.Lucite.MeanExcitationEnergy = 74.0 * q.eV
    Ma.Lucite.DefaultColor = "grey"

    Ma.Mylar.Components = ["Hydrogen", "Carbon", "Oxygen"]
    Ma.Mylar.Fractions = [0.041959, 0.625017, 0.333025]
    Ma.Mylar.Density = 1.40 * q.g / (q.cm**3)
    Ma.Mylar.DefaultColor = "red"

    Ma.Mylon.Components = ["Hydrogen", "Carbon", "Nitrogen", "Oxygen"]
    Ma.Mylon.Fractions = [0.097976, 0.636856, 0.123779, 0.141389]
    Ma.Mylon.Density = 1.140 * q.g / (q.cm**3)
    Ma.Mylon.DefaultColor = "purple"

    Ma.Kapton.Components = ["Hydrogen", "Carbon", "Nitrogen", "Oxygen"]
    Ma.Kapton.Fractions = [0.026362, 0.691133, 0.073270, 0.209235]
    Ma.Kapton.Density = 1.420 * q.g / (q.cm**3)
    Ma.Kapton.DefaultColor = "purple"

    Ma.Water_75eV.Components = ["Hydrogen", "Oxygen"]
    Ma.Water_75eV.Fractions = [0.111894, 0.888106]
    Ma.Water_75eV.Density = 1.0 * q.g / (q.cm**3)
    Ma.Water_75eV.MeanExcitationEnergy = 75.0 * q.eV
    Ma.Water_75eV.DefaultColor = "blue"

    Ma.Titanium.Components = ["Titanium"]
    Ma.Titanium.Fractions = [1.0]
    Ma.Titanium.Density = 4.54 * q.g / (q.cm**3)
    Ma.Titanium.DefaultColor = "blue"

    Ma.Steel.Components = ["Carbon", "Silicon", "Phosphorus", "Sulfur", "Chromium", "Manganese", "Iron", "Nickel"]
    Ma.Steel.Fractions = [0.0015, 0.01, 0.00045, 0.0003, 0.19, 0.02, 0.67775, 0.1]
    Ma.Steel.Density = 8.027 * q.g / (q.cm**3)
    Ma.Steel.DefaultColor = "lightblue"



Ma = Space()
setMaDefaults(Ma)
Ma["_name"] = "Ma"  # Set the name of the space
Ma["_modified"] = []  # Track modified attributes

Ma.Verbosity = 0  # Set verbosity level for material definitions







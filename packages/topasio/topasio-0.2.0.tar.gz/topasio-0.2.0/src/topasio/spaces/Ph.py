from src.topasio import Space
import quantities as q

Ph = Space()

Ph.ListName = "Default"
Ph.ListProcesses = False # Set true to dump list of active physics processes to console
Ph.Default.Type = "Geant4_Modular"
Ph.Default.Modules = ["g4em-standard_opt4", "g4h-phy_QGSP_BIC_HP", "g4decay", "g4ion-binarycascade", "g4h-elastic_HP", "g4stopping"]
Ph.Default.EMRangeMin = 100. * q.eV
Ph.Default.EMRangeMax = 500. * q.MeV
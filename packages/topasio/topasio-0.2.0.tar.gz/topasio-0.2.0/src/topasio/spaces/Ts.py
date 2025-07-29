from src.generic_classes.space import Space


def setTsDefaults(Ts):
    Ts.Seed                                                 = 1 # starting random seed
    Ts.MaxStepNumber                                        = 1000000 # limit on number of steps before a track is killed
    Ts.MaxInterruptedHistories                              = 10 # limit on how many histories can throw rare Geant4 errors
    Ts.DumpParameters                                       = False # Set true to dump full set of parameters to html file TopasParameterDump_Run0.html
    Ts.DumpNonDefaultParameters                             = False # Like above but omits defaults
    Ts.ListUnusedParameters                                 = False # Set true to list unused parameters on the console
    Ts.ShowHistoryCountAtInterval                           = 1 # How often to print history count to the console
    Ts.ShowHistoryCountLessFrequentlyAsSimulationProgresses = False # Counts by 1, then by 10, then by 100, etc.
    Ts.MaxShowHistoryCountInterval                          = 2147483647 # Stops increasing count interval after this limit
    Ts.ShowHistoryCountOnSingleLine                         = False # Set true to make history count reuse same line of console
    Ts.IncludeTimeInHistoryCount                            = False # Adds time stamp to history count
    Ts.RunIDPadding                                         = 4 # pad Run ID numbers to this many places in file names
    Ts.PauseBeforeInit                                      = False # Pause for Geant4 commands before initialization
    Ts.PauseBeforeSequence                                  = False # Pause for Geant4 commands before run sequence
    Ts.PauseBeforeQuit                                      = False # Pause for Geant4 commands before quitting
    Ts.RunVerbosity                                         = 0 # Set to larger integer to see details of run. Maximum is 2
    Ts.EventVerbosity                                       = 0 # Set to larger integer to see details of event. Maximum is 5
    Ts.TrackingVerbosity                                    = 0 # Set to larger integer to see details of tracking
    Ts.SequenceVerbosity                                    = 0 # Set to larger integer to see details of TOPAS run sequence
    Ts.QuitIfManyHistoriesSeemAnomalous                     = True # Quits if Geant4 warnings issued on too many histories
    Ts.NumberOfAnomalousHistoriesToAllowInARow              = 10000 # Limit for above
    Ts.RestoreResultsFromFile                               = False # Re-reads previous results to allow new output format or outcome modeling
    Ts.NumberOfThreads                                      = 1 # Number of CPU threads to which work will be distributed
    Ts.BufferThreadOutput                                   = False # Causes console output to be show one thread at a time
    Ts.TreatExcitedIonsAsGroundState                        = False # Allows you to read back in excited ions in a phase space file
    Ts.G4DataDirectory                                      = "" # Specify path to Geant4 Data files (instead of having to set environment variable)


Ts = Space()
Ts["_name"] = "Ts"  # Name of the space
Ts["_modified"] = []  # Track modified attributes



Ts.NumberOfThreads = 25  # Set to 1 for single-threaded execution
Ts.RunVerbosity      = 0                     # Set to larger integer to see details of run. Maximum is 2
Ts.EventVerbosity    = 0                     # Set to larger integer to see details of event. Maximum is 5
Ts.TrackingVerbosity = 0                     # Set to larger integer to see details of tracking
Ts.SequenceVerbosity = 0                     # Set to larger integer to see details of TOPAS run sequence
Ts.Verbosity            = 0                     # Set to larger integer to see details of run. Maximum is 2



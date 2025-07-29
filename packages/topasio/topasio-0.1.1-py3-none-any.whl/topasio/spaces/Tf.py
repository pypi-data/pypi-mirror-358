from src.topasio import Space
import quantities as q

Tf = Space()

Tf.RandomizeTimeDistribution = False # Causes each history to be at a different time sampled from timeline
Tf.TimelineStart             = 0. * q.s
Tf.TimelineEnd               = Tf.TimelineStart * q.s
Tf.NumberOfSequentialTimes   = 1
Tf.Verbosity                 = 0 # set to 1 to generate time log, set to 2 to get detailed update messages
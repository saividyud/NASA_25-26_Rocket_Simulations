import os
import sys

import numpy as np
import warnings
from matplotlib import pyplot as plt

import orlab as ol
from random import gauss

num = 5

print()
print('=' * 100)
with ol.OpenRocketInstance('./ORLab Tests/OpenRocket-23.09.jar') as instance:
    # Defining ORLab helper
    orl = ol.Helper(instance)
    print('=' * 100)
    print()

    # Loading the OpenRocket file
    doc = orl.load_doc('./ORLab Tests/10-14-24 NASA 24-25 Subscale.ork')

    # Getting the Nth simulation
    sim = doc.getSimulation(3)
    
    print(sim.getName())
    print('-' * 20)

    # Extracting the options from the simulation
    opts = sim.getOptions()
    opts.setLaunchRodAngle(0)  # Set a default launch rod angle

    # Extracting data about the rocket from the simulation
    rocket = sim.getRocket()

    orl.run_simulation(sim)

    data = orl.get_timeseries(
        sim, [
            ol.FlightDataType.TYPE_TIME, ol.FlightDataType.TYPE_ALTITUDE, ol.FlightDataType.TYPE_VELOCITY_Z
        ]
    )

    index_at = lambda t: (np.abs(data[ol.FlightDataType.TYPE_TIME] - t)).argmin()

    events = orl.get_events(sim)
    apogee_time = events[ol.FlightEvent.APOGEE]
    apogee_index = index_at(apogee_time)
    apogee_height = data[ol.FlightDataType.TYPE_ALTITUDE][apogee_index]

    print(apogee_index, apogee_time, apogee_height)

    print('-' * 20)

# Leave OpenRocketInstance context before showing plot in order to shutdown JVM first
print('=' * 100)
print('Shut down JVM')
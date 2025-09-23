import os
import sys

import numpy as np
import warnings
import csv
import pandas as pd

import orlab as ol

print()
print('=' * 100)
with ol.OpenRocketInstance('./OpenRocket-23.09.jar') as instance:
    # Defining ORLab helper
    orl = ol.Helper(instance)
    print('=' * 100)
    print()

    # Loading the OpenRocket file
    doc = orl.load_doc('./Fin Testing/NASA 25-26 Proposal Rocket (Trap).ork')

    # Getting the Nth simulation
    sim = doc.getSimulation(0)
    
    print(sim.getName())
    print('-' * 20)

    # Extracting the options from the simulation
    opts = sim.getOptions()

    # Extracting data about the rocket from the simulation
    rocket = sim.getRocket()

    # forward_body_tube = orl.get_component_named(rocket, 'NASA Forward Body')
    # print(dir(forward_body_tube))

    # Run the simulation
    orl.run_simulation(sim)

    # Extracting data from simulation
    data = orl.get_timeseries(
            sim, [
                ol.FlightDataType.TYPE_TIME, ol.FlightDataType.TYPE_ALTITUDE
            ]
        )
    
    events = orl.get_events(sim)

    print('-' * 20)
    print()

index_at = lambda t: (np.abs(data[ol.FlightDataType.TYPE_TIME] - t)).argmin()

apogee_time = events[ol.FlightEvent.APOGEE][0]
apogee_index = index_at(apogee_time)
apogee_height = data[ol.FlightDataType.TYPE_ALTITUDE][apogee_index]

print(f'Apogee time: {apogee_time} s')
print(f'Apogee height: {apogee_height} m')
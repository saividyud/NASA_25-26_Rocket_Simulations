import os
import sys

import numpy as np
import warnings
import csv
import pandas as pd
import pickle as pkl
import argparse

import orlab as ol
from tqdm import tqdm

print()
print('=' * 100)

with ol.OpenRocketInstance('./OpenRocket-23.09.jar') as instance:
    # Defining ORLab helper
    orl = ol.Helper(instance)
    print('=' * 100)
    print()

    # Loading the OpenRocket file
    doc = orl.load_doc(f'./Monte Carlo Sims CDR/NASA 25-26 CDR Rocket.ork')

    # Getting the 1st simulation
    sim = doc.getSimulation(0)
    
    print(sim.getName())
    print('-' * 20)

    # Extracting the options from the simulation
    opts = sim.getOptions()

    # Extracting data about the rocket from the simulation
    rocket = sim.getRocket()

    comps = orl.get_all_components(rocket)

    print(f'Total number of components: {len(comps)}')
    total_mass = 0
    for comp in comps:
        # print(f'- {comp.getName()}')
        total_mass += comp.getMass()

    print(f'Total mass of rocket: {total_mass * 2.20462} lbs')

    nosecone = orl.get_component_named(rocket, 'NASA Nose Cone')
    print(f'Nose cone mass: {nosecone.getMass() * 2.20462} lbs')

    # Run the simulation
#     orl.run_simulation(sim)

#     # Extracting data from simulation
#     data = orl.get_timeseries(
#             sim, [
#                 ol.FlightDataType.TYPE_TIME, ol.FlightDataType.TYPE_ALTITUDE
#             ]
#         )
    
#     events = orl.get_events(sim)

#     print('-' * 20)
#     print()

# index_at = lambda t: (np.abs(data[ol.FlightDataType.TYPE_TIME] - t)).argmin()

# apogee_time = events[ol.FlightEvent.APOGEE][0]
# apogee_index = index_at(apogee_time)
# apogee_height = data[ol.FlightDataType.TYPE_ALTITUDE][apogee_index]

# print(f'Apogee time: {apogee_time} s')
# print(f'Apogee height: {apogee_height * 3.28084} ft')


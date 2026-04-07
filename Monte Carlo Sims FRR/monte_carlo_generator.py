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

samples = 1000
print(f'Number of samples: {samples}')

wind_speeds = [0, 5, 9, 10, 13, 15, 20]

print()
print('=' * 100)
with ol.OpenRocketInstance('./OpenRocket-23.09.jar') as instance:
    # Defining ORLab helper
    orl = ol.Helper(instance)
    print('=' * 100)
    print()

    for wind_speed in wind_speeds:
        wind_speed_input = str(f'{wind_speed:.0f}')
        print(f'\n===================SETTING UP WIND SPEED: {wind_speed_input}===================\n')
        
        # Loading the OpenRocket file
        doc = orl.load_doc(f'./Monte Carlo Sims FRR/NASA 25-26 FRR Rocket FINAL (1.444lbs Ballast).ork')

        # Getting the 1st simulation
        sim = doc.getSimulation(0)
        
        print(sim.getName())
        print('-' * 20)

        # Extracting the options from the simulation
        opts = sim.getOptions()

        # Extracting data about the rocket from the simulation
        rocket = sim.getRocket()

        header = [
            'Wind Speed [mph]', 
            'Wind Direction [deg]',
            'Air Temperature [K]',
            'Air Pressure [Pa]',
            'Launch Rod Angle [deg]',
            'Launch Rod Direction [deg]'
        ]

        # name_delimiter = '|'

        # components = orl.get_all_components(rocket)
        # for comp in components:
        #     if comp.getName() == 'V3.0 NASA 25-26 CDR Rocket':
        #         continue

        #     elif comp.getName() == 'Sustainer - Full Scale V':
        #         continue

        #     else:
        #         header += [f'{comp.getName()}{name_delimiter}Mass [kg]']

        #         if 'Body Tube' in comp.getName():
        #             header += [f'{comp.getName()}{name_delimiter}Outer Diameter [m]', f'{comp.getName()}{name_delimiter}Length [m]']

        #         elif comp.getName() == 'NASA Nose Cone':
        #             header += [f'{comp.getName()}{name_delimiter}Length [m]']

        with open(f'./Monte Carlo Sims FRR/Data Files/{wind_speed_input}_monte_carlo_parameters.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)

            for i in tqdm(range(samples)):
                parameters = []

                # Reading in parameters
                wind_speed = float(wind_speed_input)
                wind_direction = np.random.uniform(0, 360) # deg
                air_temperature = np.random.uniform(283, 302)  # K
                air_pressure = np.random.normal(101325, 500)  # Pa

                launch_rod_angle = np.random.uniform(5, 10) # deg
                launch_rod_direction = 180 # deg

                # Changing simulation parameters
                # opts.setWindSpeedAverage(wind_speed * 0.44704)  # Convert mph to m/s
                # opts.setWindSpeedDeviation(0)
                # opts.setWindDirection(np.radians(wind_direction))
                # opts.setLaunchTemperature(air_temperature)
                # opts.setLaunchPressure(air_pressure)

                # opts.setLaunchRodAngle(np.radians(launch_rod_angle))
                # opts.setLaunchRodDirection(np.radians(launch_rod_direction))

                parameters += [wind_speed, wind_direction, air_temperature, air_pressure, launch_rod_angle, launch_rod_direction]

                # components = orl.get_all_components(rocket)
                # for comp in components:
                #     if comp.getName() == 'V3.0 NASA 25-26 CDR Rocket':
                #         continue

                #     elif comp.getName() == 'Sustainer - Full Scale V':
                #         continue

                #     elif 'Body Tube' in comp.getName():
                #         outer_diameter = 2*comp.getOuterRadius()
                #         new_outer_diameter = np.random.normal(outer_diameter, 0.000254)  # 0.01 inch in meters
                #         # comp.setOuterRadius(new_outer_diameter / 2)

                #         length = comp.getLength()
                #         new_length = np.random.normal(length, 0.00254)  # 0.1 inch in meters
                #         # comp.setLength(new_length)

                #         mass_uncertainty = 0.05 # 5%

                #     elif comp.getName() == 'NASA Nose Cone':
                #         length = comp.getLength()
                #         new_length = np.random.normal(length, 0.00254)  # 0.1 inch in meters
                #         # comp.setLength(new_length)

                #         mass_uncertainty = 0.05 # 5%

                #     elif comp.getName() == 'Payload':
                #         mass_uncertainty = 0.10 # 10%

                #     elif comp.getName() == 'AV Bay':
                #         mass_uncertainty = 0.10 # 10%

                #     else:
                #         mass_uncertainty = 0.05 # 5%

                #     mass = comp.getMass()
                #     # comp.setMassOverridden(True)
                #     new_mass = np.random.normal(mass, mass_uncertainty * mass)
                #     # comp.setOverrideMass(new_mass)

                #     if 'Body Tube' in comp.getName():
                #         parameters += [new_mass, new_outer_diameter, new_length]
                #     elif comp.getName() == 'NASA Nose Cone':
                #         parameters += [new_mass, new_length]
                #     else:
                #         parameters += [new_mass]

                writer.writerow(parameters)

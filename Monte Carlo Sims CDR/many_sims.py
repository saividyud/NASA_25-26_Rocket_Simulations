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

def pickler(obj, path):
    with open(path, 'wb') as file:
        pkl.dump(obj, file)

parser = argparse.ArgumentParser()
parser.add_argument('--wind_speed', type=float, default=None, help='Specify a wind speed to run (in mph).')
args = parser.parse_args()

wind_speed_input = str(f'{args.wind_speed:.0f}')

print(f'\n===================RUNNING WIND SPEED: {wind_speed_input}===================\n')

df = pd.read_csv(f'./Monte Carlo Sims CDR/Data Files/{wind_speed_input}_monte_carlo_parameters.csv')

samples = 1000
print(f'Number of samples: {samples}')

data = []
events = []

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

    # Running multiple simulations
    for i in tqdm(range(samples)):

        # Reading in parameters
        wind_speed = float(wind_speed_input)
        wind_direction = df.loc[i, 'Wind Direction [deg]']
        air_temperature = df.loc[i, 'Air Temperature [K]']
        air_pressure = df.loc[i, 'Air Pressure [Pa]']

        launch_rod_angle = df.loc[i, 'Launch Rod Angle [deg]']
        launch_rod_direction = df.loc[i, 'Launch Rod Direction [deg]']

        # Changing simulation parameters
        opts.setWindSpeedAverage(wind_speed * 0.44704)  # Convert mph to m/s
        opts.setWindSpeedDeviation(0)
        opts.setWindDirection(np.radians(wind_direction))
        opts.setLaunchTemperature(air_temperature)
        opts.setLaunchPressure(air_pressure)

        opts.setLaunchRodAngle(np.radians(launch_rod_angle))
        opts.setLaunchRodDirection(np.radians(launch_rod_direction))

        for j in range(6, len(df.columns)):
            col_name = df.columns[j]
            comp_name = col_name.split('|')[0]
            comp = orl.get_component_named(rocket, comp_name)

            if col_name.split('|')[1] == 'Mass [kg]':
                new_mass = df.loc[i, col_name]
                comp.setMassOverridden(True)
                comp.setOverrideMass(new_mass)

            elif col_name.split('|')[1] == 'Outer Diameter [m]':
                new_outer_diameter = df.loc[i, col_name]
                comp.setOuterRadius(new_outer_diameter / 2)

            elif col_name.split('|')[1] == 'Length [m]':
                new_length = df.loc[i, col_name]
                comp.setLength(new_length)

        # components = orl.get_all_components(rocket)
        # for comp in components:
        #     if comp.getName() == 'V3.0 NASA 25-26 CDR Rocket':
        #         continue

        #     elif comp.getName() == 'Sustainer - Full Scale V':
        #         continue

        #     elif 'Body Tube' in comp.getName():
        #         outer_diameter = 2*comp.getOuterRadius()
        #         new_outer_diameter = np.random.normal(outer_diameter, 0.000254)  # 0.01 inch in meters
        #         comp.setOuterRadius(new_outer_diameter / 2)

        #         length = comp.getLength()
        #         new_length = np.random.normal(length, 0.00254)  # 0.1 inch in meters
        #         comp.setLength(new_length)

        #         mass_uncertainty = 0.05 # 5%

        #     elif comp.getName() == 'NASA Nose Cone':
        #         length = comp.getLength()
        #         new_length = np.random.normal(length, 0.00254)  # 0.1 inch in meters
        #         comp.setLength(new_length)

        #         mass_uncertainty = 0.05 # 5%

        #     elif comp.getName() == 'Payload':
        #         mass_uncertainty = 0.10 # 10%

        #     elif comp.getName() == 'AV Bay':
        #         mass_uncertainty = 0.10 # 10%

        #     else:
        #         mass_uncertainty = 0.05 # 5%

        #     mass = comp.getMass()
        #     comp.setMassOverridden(True)
        #     new_mass = np.random.normal(mass, mass_uncertainty * mass)
        #     comp.setOverrideMass(new_mass)

        # Running the simulation
        orl.run_simulation(sim)

        # Extracting data from simulation
        data.append(
            orl.get_timeseries(
                sim, [
                    ol.FlightDataType.TYPE_TIME, 
                    ol.FlightDataType.TYPE_ALTITUDE, 
                    ol.FlightDataType.TYPE_VELOCITY_TOTAL, 
                    ol.FlightDataType.TYPE_ACCELERATION_TOTAL, 
                    ol.FlightDataType.TYPE_STABILITY,
                    ol.FlightDataType.TYPE_POSITION_X,
                    ol.FlightDataType.TYPE_POSITION_Y,
                ]
            )
        )

        events.append(orl.get_events(sim))

    print('-' * 20)
    print()

# Leave OpenRocketInstance context before showing plot in order to shutdown JVM first
print('=' * 100)
print('Shut down JVM')

pickler(data, f'./Monte Carlo Sims CDR/Data Files/{wind_speed_input}_monte_carlo_data.pkl')
pickler(events, f'./Monte Carlo Sims CDR/Data Files/{wind_speed_input}_monte_carlo_events.pkl')
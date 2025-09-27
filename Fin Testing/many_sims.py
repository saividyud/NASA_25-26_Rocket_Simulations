import os
import sys

import numpy as np
import warnings
import csv
import pandas as pd
import pickle as pkl
import argparse

import orlab as ol

def pickler(obj, path):
    with open(path, 'wb') as file:
        pkl.dump(obj, file)

parser = argparse.ArgumentParser()
parser.add_argument('--fin_shape', type=str, default=None, help='Specify a fin shape to run (Trapezoidal, Elliptical, Swept, Tapered Swept). If not specified, will fail.')
args = parser.parse_args()

fin_shapes = ['Trapezoidal', 'Elliptical', 'Swept', 'Tapered Swept']

if args.fin_shape:
    if args.fin_shape not in fin_shapes:
        raise ValueError(f'Invalid fin shape specified. Must be one of: {fin_shapes}')
    else:
        fin_shape = args.fin_shape

print(f'\n========================RUNNING FIN SHAPE: {fin_shape}========================\n')

if fin_shape == 'Trapezoidal':
    name = 'trap'
elif fin_shape == 'Elliptical':
    name = 'ellip'
elif fin_shape == 'Swept':
    name = 'swept'
elif fin_shape == 'Tapered Swept':
    name = 'tapered_swept'

df = pd.read_csv(f'./Fin Testing/Data Files/{fin_shape}/{name}_monte_carlo_parameters.csv')

samples = len(df['Wind Speed'])
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
    doc = orl.load_doc(f'./Fin Testing/OpenRocket Files/NASA 25-26 Proposal Rocket ({fin_shape}).ork')

    # Getting the Nth simulation
    sim = doc.getSimulation(0)
    
    print(sim.getName())
    print('-' * 20)

    # Extracting the options from the simulation
    opts = sim.getOptions()

    # Extracting data about the rocket from the simulation
    rocket = sim.getRocket()

    # Running multiple simulations
    for i in range(samples):
        print(f'Running simulation {i + 1}/{samples}')

        # Reading in parameters
        wind_speed = df['Wind Speed'][i]
        wind_direction = df['Wind Direction'][i]
        air_temperature = df['Air Temperature'][i]
        air_pressure = df['Air Pressure'][i]

        nose_cone_mass = df['Nose Cone Mass'][i]
        nose_cone_shape_parameter = df['Nose Cone Shape Parameter'][i]
        nose_cone_length = df['Nose Cone Length'][i]

        forward_body_tube_mass = df['Forward Body Tube Mass'][i]
        middle_body_tube_mass = df['Middle Body Tube Mass'][i]
        aft_body_tube_mass = df['Aft Body Tube Mass'][i]

        forward_body_tube_length = df['Forward Body Tube Length'][i]
        middle_body_tube_length = df['Middle Body Tube Length'][i]
        aft_body_tube_length = df['Aft Body Tube Length'][i]

        forward_body_tube_outer_diameter = df['Forward Body Tube Outer Diameter'][i]
        middle_body_tube_outer_diameter = df['Middle Body Tube Outer Diameter'][i]
        aft_body_tube_outer_diameter = df['Aft Body Tube Outer Diameter'][i]

        launch_rod_angle = df['Launch Rod Cant'][i]
        launch_rod_direction = df['Launch Rod Direction'][i]

        # Changing simulation parameters
        opts.setWindSpeedAverage(wind_speed)
        opts.setWindSpeedDeviation(0)
        opts.setWindDirection(np.radians(wind_direction))
        opts.setLaunchTemperature(air_temperature)
        opts.setLaunchPressure(air_pressure)

        nose_cone = orl.get_component_named(rocket, 'NASA Nose Cone')
        nose_cone.setMassOverridden(True)
        nose_cone.setOverrideMass(nose_cone_mass)
        nose_cone.setShapeParameter(nose_cone_shape_parameter)
        nose_cone.setLength(nose_cone_length)

        forward_body_tube = orl.get_component_named(rocket, 'NASA Forward Body')
        forward_body_tube.setMassOverridden(True)
        forward_body_tube.setOverrideMass(forward_body_tube_mass)
        forward_body_tube.setLength(forward_body_tube_length)
        forward_body_tube.setOuterRadius(forward_body_tube_outer_diameter/2)

        middle_body_tube = orl.get_component_named(rocket, 'NASA Middle Body')
        middle_body_tube.setMassOverridden(True)
        middle_body_tube.setOverrideMass(middle_body_tube_mass)
        middle_body_tube.setLength(middle_body_tube_length)
        middle_body_tube.setOuterRadius(middle_body_tube_outer_diameter/2)

        aft_body_tube = orl.get_component_named(rocket, 'NASA Aft Body')
        aft_body_tube.setMassOverridden(True)
        aft_body_tube.setOverrideMass(aft_body_tube_mass)
        aft_body_tube.setLength(aft_body_tube_length)
        aft_body_tube.setOuterRadius(aft_body_tube_outer_diameter/2)

        opts.setLaunchRodAngle(np.radians(launch_rod_angle))
        opts.setLaunchRodDirection(np.radians(launch_rod_direction))

        # Running the simulation
        orl.run_simulation(sim)

        # Extracting data from simulation
        data.append(
            orl.get_timeseries(
                sim, [
                    ol.FlightDataType.TYPE_TIME, ol.FlightDataType.TYPE_ALTITUDE, ol.FlightDataType.TYPE_VELOCITY_TOTAL, ol.FlightDataType.TYPE_ACCELERATION_TOTAL, ol.FlightDataType.TYPE_STABILITY
                ]
            )
        )

        # index_at = lambda t: (np.abs(data[ol.FlightDataType.TYPE_TIME] - t)).argmin()
        events.append(orl.get_events(sim))

    print('-' * 20)
    print()

# Leave OpenRocketInstance context before showing plot in order to shutdown JVM first
print('=' * 100)
print('Shut down JVM')

pickler(data, f'./Fin Testing/Data Files/{fin_shape}/{name}_monte_carlo_data.pkl')
pickler(events, f'./Fin Testing/Data Files/{fin_shape}/{name}_monte_carlo_events.pkl')
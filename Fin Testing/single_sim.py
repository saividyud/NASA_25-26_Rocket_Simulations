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
    doc = orl.load_doc('./Fin Testing/OpenRocket Files/NASA 25-26 PDR Rocket (Swept).ork')

    # Getting the Nth simulation
    sim = doc.getSimulation(0)
    
    print(sim.getName())
    print('-' * 20)

    # Extracting the options from the simulation
    opts = sim.getOptions()

    # Extracting data about the rocket from the simulation
    rocket = sim.getRocket()

    # Changing simulation parameters
    opts.setWindSpeedAverage(0)
    opts.setWindSpeedDeviation(0)
    opts.setWindDirection(np.radians(0))
    opts.setLaunchTemperature(296)  # Kelvin
    opts.setLaunchPressure(101325)  # Pa

    nose_cone = orl.get_component_named(rocket, 'NASA Nose Cone')
    nose_cone.setMassOverridden(True)
    nose_cone.setOverrideMass(0.9)
    nose_cone.setLength(0.7)

    # forward_body_tube = orl.get_component_named(rocket, 'NASA Forward Body')
    # forward_body_tube.setMassOverridden(True)
    # forward_body_tube.setOverrideMass(forward_body_tube_mass)
    # forward_body_tube.setLength(forward_body_tube_length)
    # forward_body_tube.setOuterRadius(forward_body_tube_outer_diameter/2)

    # middle_body_tube = orl.get_component_named(rocket, 'NASA Middle Body')
    # middle_body_tube.setMassOverridden(True)
    # middle_body_tube.setOverrideMass(middle_body_tube_mass)
    # middle_body_tube.setLength(middle_body_tube_length)
    # middle_body_tube.setOuterRadius(middle_body_tube_outer_diameter/2)

    # aft_body_tube = orl.get_component_named(rocket, 'NASA Aft Body')
    # aft_body_tube.setMassOverridden(True)
    # aft_body_tube.setOverrideMass(aft_body_tube_mass)
    # aft_body_tube.setLength(aft_body_tube_length)
    # aft_body_tube.setOuterRadius(aft_body_tube_outer_diameter/2)

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
print(f'Apogee height: {apogee_height * 3.28084} ft')
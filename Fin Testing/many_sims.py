import os
import sys

import numpy as np
import warnings
import csv
import pandas as pd

import orlab as ol

df = pd.read_csv('./Fin Testing/monte_carlo_parameters.csv')

samples = len(df['Wind Speed'])
print(f'Number of samples: {samples}')

print()
print('=' * 100)
with ol.OpenRocketInstance('./OpenRocket-23.09.jar') as instance:
    # Defining ORLab helper
    orl = ol.Helper(instance)
    print('=' * 100)
    print()

    # Loading the OpenRocket file
    doc = orl.load_doc('./Fin Testing/NASA 25-26 Proposal rocket (Trap).ork')

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

        opts.setLaunchRodAngle(np.radians(df['Launch Rod Angle'][i]))

        # Running the simulation
        orl.run_simulation(sim)

        # Extracting data from simulation
        data.append(
            orl.get_timeseries(
                sim, [
                    ol.FlightDataType.TYPE_TIME, ol.FlightDataType.TYPE_ALTITUDE, ol.FlightDataType.TYPE_VELOCITY_Z
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

apogees = []
for i in range(num):
    apogee_index = (np.abs(data[i][ol.FlightDataType.TYPE_TIME] - events[i][ol.FlightEvent.APOGEE])).argmin()
    apogees.append(data[i][ol.FlightDataType.TYPE_ALTITUDE][apogee_index])

# Create a figure with two rows of subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Plot histogram of launch rod angles
ax1.hist(launch_rod_angles, bins=15, color='skyblue', edgecolor='black')
ax1.set_title('Histogram of Launch Rod Angles')
ax1.set_xlabel('Launch Rod Angle (degrees)')
ax1.set_ylabel('Frequency')

# Plot histogram of apogee heights
ax2.hist(apogees, bins=15, color='salmon', edgecolor='black')
ax2.set_title('Histogram of Apogee Heights')
ax2.set_xlabel('Apogee Height (meters)')
ax2.set_ylabel('Frequency')

plt.tight_layout()

# fig = plt.figure(figsize=(10, 8))
# ax = fig.add_subplot()

# fig.suptitle('Apogee Height vs Launch Rod Angle')

# ax.set_xlabel('Launch Rod Angle (degrees)')
# ax.set_ylabel('Apogee Height (meters)')

# ax.scatter(launch_rod_angles, apogees, marker='o')

# ax.grid(True)

plt.show()

# for i in range(num):
#     print(f'Launch Rod Angle: {launch_rod_angles[i]} degrees')
#     print(f'Apogee Time: {events[i][ol.FlightEvent.APOGEE]} seconds')
#     apogee_index = (np.abs(data[i][ol.FlightDataType.TYPE_TIME] - events[i][ol.FlightEvent.APOGEE])).argmin()
#     print(f'Apogee Height: {data[i][ol.FlightDataType.TYPE_ALTITUDE][apogee_index]} meters')
#     print('-' * 20)
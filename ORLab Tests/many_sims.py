import os
import sys

import numpy as np
import warnings
from matplotlib import pyplot as plt

import orlab as ol
from random import gauss

plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['figure.titlesize'] = 20
plt.rcParams['figure.titleweight'] = 'bold'
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['figure.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 12
plt.rcParams['mathtext.fontset'] = 'cm'

num = 100
data = []
events = []
launch_rod_angles = []

print()
print('=' * 100)
with ol.OpenRocketInstance('./OpenRocket-23.09.jar') as instance:
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

    # Extracting data about the rocket from the simulation
    rocket = sim.getRocket()

    # Running multiple simulations
    for i in range(num):
        print(f'Running simulation {i + 1}/{num}')

        # Randomizing launch rod angle (0 degrees +- 5 degrees)
        launch_rod_angles.append(gauss(0, 5))
        opts.setLaunchRodAngle(np.radians(launch_rod_angles[-1]))

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
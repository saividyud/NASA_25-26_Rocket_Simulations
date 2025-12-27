import os
import sys

import numpy as np
import warnings
import csv
import pandas as pd
from scipy import interpolate
from scipy import optimize
import matplotlib.pyplot as plt

import orlab as ol

plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['figure.titlesize'] = 20
plt.rcParams['figure.titleweight'] = 'bold'
plt.rcParams['figure.figsize'] = (10, 8)
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['figure.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 12
plt.rcParams['mathtext.fontset'] = 'cm'

print()
print('=' * 100)

with ol.OpenRocketInstance('./OpenRocket-23.09.jar') as instance:
    # Defining ORLab helper
    orl = ol.Helper(instance)
    print('=' * 100)
    print()

    # Loading the OpenRocket file
    doc = orl.load_doc('./Fin Testing/OpenRocket Files/NASA 25-26 ACTUAL Subscale Rocket.ork')

    # Getting the Nth simulation
    sim = doc.getSimulation(0)
    
    print(sim.getName())
    print('-' * 20)

    # Extracting the options from the simulation
    opts = sim.getOptions()

    # Extracting data about the rocket from the simulation
    rocket = sim.getRocket()

    # Importing avionics and payload flight data
    data_avionics = pd.read_csv('./Subscale Flight Analysis/Subscale Telemega.csv')
    data_avionics2 = data_avionics.assign(**{'Altitude [ft]': data_avionics['height'] * 3.28084, 'Time [s]': data_avionics['time']})
    data_avionics2 = data_avionics2[data_avionics2['Time [s]'].values < 50]

    # Deleting error point before apogee
    data_avionics2 = data_avionics2.drop(index=data_avionics2[(data_avionics2['Time [s]'] > 9) & (data_avionics2['Time [s]'] < 10) & (data_avionics2['Altitude [ft]'] < 1500)].index).reset_index(drop=True)

    start_time = 5464.5
    end_time = start_time + 50
    data_payload = pd.read_csv('./Subscale Flight Analysis/Subscale Payload.csv')
    data_payload2 = data_payload[(data_payload['Time [s]'].values > start_time) & (data_payload['Time [s]'].values < end_time)]
    data_payload2 = data_payload2.assign(**{'Time [s]': data_payload2['Time [s]'] - start_time, 'Altitude [ft]': (data_payload2['Altitude [m]'] - data_payload2['Altitude [m]'].values[0]) * 3.28084}).reset_index(drop=True)

    # Creating interpolation functions for avionics and payload data
    interp_avionics = interpolate.interp1d(data_avionics2['Time [s]'], data_avionics2['Altitude [ft]'], kind='linear', fill_value=0, bounds_error=False)
    interp_payload = interpolate.interp1d(data_payload2['Time [s]'], data_payload2['Altitude [ft]'], kind='linear', fill_value=0, bounds_error=False)

    # Fitting simulation parameters to actual rocket flight
    '''
    Parameters to fit:
    1. Wind speed average (m/s) (not done)
    2. Turbulence intensity (0 to 0.2) (not done)
    3. Wind direction (degrees) (not done)
    4. Launch temperature (C)
    5. Launch pressure (Pa)
    6. Launch rod angle (degrees)
    7. Drogue parachute drag coefficient
    8. Main parachute drag coefficient
    9. Main parachute deployment delay (s)
    '''
    def objective_function(params):
        launch_temp_c, launch_pressure_pa, launch_rod_angle_deg, drogue_drag_coeff, main_drag_coeff, main_deploy_delay_s, time_offset = params

        # Setting simulation parameters
        # opts.setWindSpeedAverage(wind_speed_avg) # m/s
        # opts.setWindSpeedDeviation(wind_speed_avg * turbulence_intensity)
        # opts.setWindDirection(np.radians(wind_direction_deg))
        opts.setLaunchTemperature(launch_temp_c + 273.15)  # Kelvin
        opts.setLaunchPressure(launch_pressure_pa)  # Pa
        opts.setLaunchRodAngle(np.radians(launch_rod_angle_deg))

        # Setting rocket parameters
        drogue_parachute = orl.get_component_named(rocket, f'Drogue Parachute')
        drogue_parachute.setCD(drogue_drag_coeff)

        main_parachute = orl.get_component_named(rocket, f'Main Parachute')
        main_parachute.setCD(main_drag_coeff)

        parachute_config = main_parachute.getDeploymentConfigurations()
        deployment_config = parachute_config.getDefault()
        deployment_config.setDeployDelay(main_deploy_delay_s)

        # Run the simulation
        orl.run_simulation(sim)

        # Extracting data from simulation
        data = orl.get_timeseries(
                sim, [
                    ol.FlightDataType.TYPE_TIME, ol.FlightDataType.TYPE_ALTITUDE
                ]
            )

        sim_time = data[ol.FlightDataType.TYPE_TIME]
        sim_altitude_ft = data[ol.FlightDataType.TYPE_ALTITUDE] * 3.28084  # Convert to feet

        # Calculate error between simulation and actual flight data
        interp_altitudes_avionics = interp_avionics(sim_time + time_offset)

        time_to_apogee_avionics = data_avionics2['Time [s]'][np.argmax(data_avionics2['Altitude [ft]'])]

        error_ascent = np.linalg.norm(sim_altitude_ft[sim_time < time_to_apogee_avionics] - interp_altitudes_avionics[sim_time < time_to_apogee_avionics])
        error_descent = np.linalg.norm(sim_altitude_ft[sim_time >= time_to_apogee_avionics] - interp_altitudes_avionics[sim_time >= time_to_apogee_avionics])

        return error_ascent + (10.0 * error_descent) # Heavily weight the parachute phase


    def callback(xk):
        print('Current error:', objective_function(xk))
    
    # Initial guess for parameters
    initial_guess = [
        # 0.0, # wind speed average (m/s)
        # 0.0, # turbulence intensity
        # 0.0, # wind direction (degrees)
        10.0, # launch temperature (C)
        98320.0, # launch pressure (Pa)
        0.0, # launch rod angle (degrees)
        0.73, # drogue parachute drag coefficient
        0.30, # main parachute drag coefficient
        2.7, # main parachute deployment delay (s)
        0 # time offset (s)
    ]

    # Bounds for parameters
    # bounds = [
    #     # (0, 8.9408),    # wind speed average (m/s)
    #     # (0.0, 0.2),     # turbulence intensity
    #     # (0.0, 360.0),   # wind direction (degrees)
    #     (5.0, 30.0),   # launch temperature (C)
    #     (90000.0, 110000.0), # launch pressure (Pa)
    #     (0.0, 10.0),      # launch rod angle (degrees)
    #     (0.5, 3),     # drogue parachute drag coefficient
    #     (1, 4),     # main parachute drag coefficient
    #     (500, 800) # main parachute deployment altitude (ft)
    # ]

    # Optimize parameters using L-BFGS-B algorithm
    result = optimize.minimize(objective_function, initial_guess, method='Nelder-Mead', options={'disp': True}, callback=callback)
    print('Optimized parameters:', result.x)

    # Run the simulation
    orl.run_simulation(sim)

    # Extracting data from simulation
    data = orl.get_timeseries(
            sim, [
                ol.FlightDataType.TYPE_TIME, ol.FlightDataType.TYPE_ALTITUDE, ol.FlightDataType.TYPE_VELOCITY_TOTAL
            ]
        )
    
    events = orl.get_events(sim)

    # print('-' * 20)
    print()

index_at = lambda t: (np.abs(data[ol.FlightDataType.TYPE_TIME] - t)).argmin()

apogee_time = events[ol.FlightEvent.APOGEE][0]
apogee_index = index_at(apogee_time)
apogee_height = data[ol.FlightDataType.TYPE_ALTITUDE][apogee_index]

print(f'Apogee time: {apogee_time} s')
print(f'Apogee height: {apogee_height * 3.28084} ft')
print(f'Flight duration: {data[ol.FlightDataType.TYPE_TIME][-1]} s')

fig = plt.figure()
ax = fig.add_subplot()

ax.plot(data[ol.FlightDataType.TYPE_TIME], data[ol.FlightDataType.TYPE_ALTITUDE] * 3.28084, label='Simulation', color='blue')
ax.scatter(data_avionics2['Time [s]'], data_avionics2['Altitude [ft]'], label='Avionics Data', color='red', s=10)

ax.set_xlabel('Time (s)')
ax.set_ylabel('Altitude (ft)')
ax.set_title('Rocket Altitude vs Time')
ax.legend()

plt.show()
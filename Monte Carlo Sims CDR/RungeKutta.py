import numpy as np

# Constants
rho = 0.00238        # slug/ft^3
dt = 0.1             # timestep (s)

# Drag areas (Cd * pi * r^2)
CdA_drogue = 3.64
CdA_main   = 141.3

# Masses (slugs)
m_drogue = 39.996564 / 32.2
m_main   = 37.996564 / 32.2

# Descent times
t_drogue = 41.00454     # apogee -> 700 ft
t_main   = 42.78372     # 700 ft -> landing

# Initial conditions
theta = np.deg2rad(7)    # launch rail angle
v_exit = 87.37            # ft/s
vx0 = v_exit * np.sin(theta)

# Wind speeds (mph -> ft/s)
wind_speeds_mph = [0, 5, 9, 10, 13, 15, 20]
wind_speeds = [v * 1.46667 for v in wind_speeds_mph]

# Derivative function
def derivatives(vx, CdA, m, vw):
    drag = -0.5 * rho * CdA * (vx - vw) * abs(vx - vw)
    ax = drag / m
    return vx, ax

# RK4 step
def rk4_step(vx, x, dt, CdA, m, vw):
    k1x, k1v = derivatives(vx, CdA, m, vw)
    k2x, k2v = derivatives(vx + 0.5*dt*k1v, CdA, m, vw)
    k3x, k3v = derivatives(vx + 0.5*dt*k2v, CdA, m, vw)
    k4x, k4v = derivatives(vx + dt*k3v, CdA, m, vw)

    x_new  = x  + dt/6 * (k1x + 2*k2x + 2*k3x + k4x)
    vx_new = vx + dt/6 * (k1v + 2*k2v + 2*k3v + k4v)

    return vx_new, x_new

# Loop over wind speeds
results = []

for vw, vw_mph in zip(wind_speeds, wind_speeds_mph):
    vx = vx0
    x = 0.0

    # Phase 1: Drogue
    t = 0.0
    while t < t_drogue:
        vx, x = rk4_step(vx, x, dt, CdA_drogue, m_drogue, vw)
        t += dt

    x_drogue = x

    # Phase 2: Main
    t = 0.0
    while t < t_main:
        vx, x = rk4_step(vx, x, dt, CdA_main, m_main, vw)
        t += dt

    results.append((vw_mph, x_drogue, x, vw*(t_drogue + t_main)))

# Output
print("Wind (mph) | Drogue Drift (ft) | Total Drift (ft) | Simple Calc (ft) | Average of Calculations (ft)")
print("---------------------------------------------------------------")
for r in results:
    print(f"{r[0]:>10} | {r[1]:>17.2f} | {r[2]:>15.2f} | {r[3]:>15.2f} | {(r[2] + r[3])/2:>25.2f}")
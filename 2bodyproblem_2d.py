import numpy as np

# 2D, 2 Body Problem Orbit Simulation
# Assumptions:
    # Earth has constant radius and is homogeneous
    # Treat Earth as a point mass with center of mass at its center (0,0)
    # x-y coordinate plane is centered at Earth's center
    # Equatorial orbit to satisfy 2D modelling (z=0)


# Parameters (all in SI Units)
rad_Earth = 6378137 # meters
mass_Earth = 5.972e24 # kg
g_sea_level = 9.81 # m/s^2
grav_const = 6.6743e-11 # (m^3)(kg^-1)(s^-2)
mu_Earth = grav_const * mass_Earth # m^3/s^2

# Define state vector and acceleration (using numpy array to...???)
state = np.array([0,0,0,0]) # r_x (m), r_y (m), v_x (m/s), v_y (m/s)
acceleration = np.array([0,0]) # a_x (m/s^2), a_y (m/s^2)


# Find acceleration in terms of x and y coordinates (derived from Newton's Second Law
def acceleration_calc(state):
    a_x = -mu_Earth * state[0]/((state[0])**2+(state[1])**2)**1.5
    a_y = -mu_Earth * state[1]/((state[0])**2+(state[1])**2)**1.5
    return [a_x,a_y]

# Implement Runge-Kutta to iterate over ODE and find position of satellite


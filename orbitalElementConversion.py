import numpy as np

# Takes state vector and calculates orbital elements
def orbitalElementConversion(state):

    # Initiate vector to hold orbital elements
    # Index 0 - semimajor axis (m), Index 1 - eccentricity (dimensionless), Index 2 - inclination (rads)
    # Index 3 - RAAN (rads), Index 4 - Argument of Periapsis (rads), Index 5 - True Anomaly (rads)
    orbitalElements = np.zeros(6)

    # Defined constants
    # TODO: Create a comprehensive parameters header file
    mass_earth = 5.9722e24 # kg
    grav_const = 6.6743e-11 # (m^3)(kg^-1)(s^-2)
    mu_earth = grav_const * mass_earth # m^3/s^2

    # Position (m) and velocity (m/s)
    pos = np.array(state[0:3])
    vel = np.array(state[3:6])

    # Calculate magnitude of position and velocity
    mag_pos = np.linalg.norm(pos)
    mag_vel = np.linalg.norm(vel)

    # Calculate specific angular momentum (m^2/s)
    h = np.cross(pos, vel)

    # Calculate semi major axis (m)
    orbitalElements[0] = 1/((2/mag_pos)-(mag_vel**2/mu_earth))

    # Calculate eccentricity
    orbitalElements[1] = (1/mu_earth)*np.cross(vel, h)-pos/mag_pos




    return(orbitalElements)
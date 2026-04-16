import numpy as np

# 3D, 2 Body Problem Orbit Simulation
# Assumptions:
    # Earth has constant radius and is homogeneous
    # Treat Earth as a point mass with center of mass at its center (0,0)
    # x-y-z coordinate plane is centered at Earth's center


# Parameters (all in SI Units)
rad_Earth = 6378137 # meters
mass_Earth = 5.972e24 # kg
g_sea_level = 9.81 # m/s^2
grav_const = 6.6743e-11 # (m^3)(kg^-1)(s^-2)
mu_Earth = grav_const * mass_Earth # m^3/s^2



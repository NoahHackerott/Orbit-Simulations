# 2D, 2 Body Problem Orbit Simulation
# Assumptions:
# Earth has constant radius and is homogeneous
# Treat Earth as a point mass with center of mass at its center (0,0)
# x-y coordinate plane is centered at Earth's center



# Parameters (all in SI Units)
rad_Earth = 6378137 # meters
mass_Earth = 5.972e24 # kg
g_sea_level = 9.81 # m/s^2
grav_const = 6.6743e-11 # (m^3)(kg^-1)(s^-2)

# Define state vector
state=[0,0,0,0] # r_x (m), r_y (m), v_x (m/s), v_y (m/s)


# Calculation of gravitational acceleration in terms of altitude
def gcalculator(altitude):
    g = (grav_const * mass_Earth)/(rad_Earth + altitude)^2
    return g

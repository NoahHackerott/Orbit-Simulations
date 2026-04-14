# Parameters (all in SI Units)
# Assuming: Earth has constant radius and homogeneous
rad_Earth = 6378137 # meters
mass_Earth = 5.972e24 # kg
g_sea_level = 9.81 # m/s^2
grav_const = 6.6743e-11 # (m^3)(kg^-1)(s^-2)




# Calculation of gravitational acceleration in terms of altitude
def gcalculator(altitude):
    g = (grav_const * mass_Earth)/(rad_Earth + altitude)^2
    return g

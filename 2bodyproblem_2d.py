import numpy as np
import sys

# 2D, 2 Body Problem Orbit Simulation
# Assumptions:
    # Earth has constant radius and is homogeneous
    # Treat Earth as a point mass with center of mass at origin
    # x-y coordinate plane is centered at Earth's center
    # Equatorial orbit to satisfy 2D modelling (z=0)


# Parameters (all in SI Units)
rad_Earth = 6378137 # meters
mass_Earth = 5.972e24 # kg
g_sea_level = 9.81 # m/s^2
grav_const = 6.6743e-11 # (m^3)(kg^-1)(s^-2)
mu_Earth = grav_const * mass_Earth # m^3/s^2

# Find acceleration in terms of x and y coordinates (derived from Newton's Second Law
def acceleration_calc(state):
    # Grabs a "slice" of the state vector (first and second elements)
    r = state[0:2]
    r_mag = np.linalg.norm(r)

    # Returns both a_x and a_y
        # Multiplying a scalar by an entire array which in our case is the r vector (allowed by Numpy)
    return -mu_Earth * r / r_mag**3

# Implement Runge-Kutta to iterate over ODE and find position of satellite (NEED to do)




# Main function
def main():
    # Define acceleration vector (using numpy array to allow for smoother/faster vector calculations)
    acceleration = np.array([0, 0])  # a_x (m/s^2), a_y (m/s^2)

    # Other variables
    time = 0 # (s)
    dt = 0.01 # needs to be updated (s)
    t_final = 100 # Needs to be updated (s)


    state = input("Enter the initial state of the body in standard units [r_x (m), r_y (m), v_x (m/s), v_y (m/s)]: ")

    # The input function takes in a string, so need to separate each piece delimited by a comma into the state vector
    state = np.array([float(x) for x in state.split(',')]) # r_x (m), r_y (m), v_x (m/s), v_y (m/s)


    # Grabs a "slice" of the state vector (first and second elements)
    r = state[0:2]
    r_mag = np.linalg.norm(r)


    # Check for valid conditions of initial position (if not valid stop the program)
    if r_mag <= 6378137:
        print("Error, the body is inside Earth. Exiting...")
        sys.exit()


    # Calculate how many steps for loop will iterate over
    steps = int(t_final/dt)

    # For loop to collect data through iterations
    # NEED to write this for loop body
    for i in range(0, steps):

if __name__ == "__main__":
    main()








import numpy as np
import sys
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

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

# Calculates f(t,y) that will be plugged into IVP solver
def deriv_calc(t, state):
    state_prime = np.concatenate([state[2:4], acceleration_calc(state[0:2])])
    return state_prime

# Calculate orbital energy for later plotting
def orbital_energy(state):



# Main function
def main():

    # Other variables
    dt = 10 # (s)
    t_final = 60000 # (s)


    state = input("Enter the initial state of the body in standard units [r_x (m), r_y (m), v_x (m/s), v_y (m/s)]: ")

    # The input function takes in a string, so need to separate each piece delimited by a comma into the state vector
    state = np.array([float(x) for x in state.split(',')]) # r_x (m), r_y (m), v_x (m/s), v_y (m/s)


    # Grabs a "slice" of the state vector (first and second elements)
    r = state[0:2]
    r_mag = np.linalg.norm(r)

    # Create a variable that will guide how many points will be saved to solution by solve_ivp
    t_eval = np.linspace(0, t_final, 1000)


    # Check for valid conditions of initial position (if not valid stop the program)
    if r_mag <= 6378137:
        print("Error, the body is inside Earth. Exiting...")
        sys.exit()

    # ODE solver (using RK45)
    solution = solve_ivp(deriv_calc, [0, t_final], state, method='RK45', t_eval = t_eval, first_step=dt)

    # Store r_x and r_y in respective variables for plotting
    x = solution.y[0]
    y = solution.y[1]

    # Plot solution to visualize orbit
    # Looking down at the North Pole (equatorial orbit in 2D)
    plt.plot(x, y, 'b')
    plt.xlabel('X Position [m]')
    plt.ylabel('Y Position [m]')
    plt.title('Orbital Path')
    plt.show()


if __name__ == "__main__":
    main()








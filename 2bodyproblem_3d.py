import numpy as np
import sys
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# 3D, 2 Body Problem Orbit Simulation
# Assumptions:
    # Earth has constant radius and is homogeneous
    # Treat Earth as a point mass with center of mass at origin
    # x-y coordinate plane is centered at Earth's center


# Parameters (all in SI Units)
rad_Earth = 6378137 # meters
mass_Earth = 5.9722e24 # kg
grav_const = 6.6743e-11 # (m^3)(kg^-1)(s^-2)
mu_Earth = grav_const * mass_Earth # m^3/s^2

# Find acceleration in terms of x and y coordinates (derived from Newton's Second Law
def acceleration_calc(state):
    # Grabs a "slice" of the state vector (first and second elements)
    r = state[0:3]
    r_mag = np.linalg.norm(r)

    # Returns both a_x and a_y
        # Multiplying a scalar by an entire array which in our case is the r vector (allowed by Numpy)
    return -mu_Earth * r / r_mag**3

# Calculates f(t,y) that will be plugged into IVP solver
def deriv_calc(t, state):
    state_prime = np.concatenate([state[3:6], acceleration_calc(state[0:3])])
    return state_prime

def user_input():
    state = input("Enter the initial altitude and velocity of the body in the following units [r_x (km), r_y (km) r_z (km)"
         ", v_x (m/s), v_y (m/s), v_z (m/s]: ")

    # The input function takes in a string, so need to separate each piece delimited by a comma into the state vector
    # r_x (km), r_y (km), r_z (km), v_x (m/s), v_y (m/s), v_z (m/s)
    state = np.array([float(x) for x in state.split(',')])
    return state

def plotting(solution):
    # Store r_x, r_y, and r_z in respective variables for plotting
    x = solution.y[0]/1000
    y = solution.y[1]/1000
    z = solution.y[2]/1000

    # Plot solution to visualize orbit
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(x, y, z, 'r')
    ax.set_xlabel('X Position (km)')
    ax.set_ylabel('Y Position (km)')
    ax.set_zlabel('Z Position (km)')


    # Create sphere that will represent Earth on plot (in spherical coordinates for meshgrid)

    # Sphere parameters
    theta = np.linspace(0, 2 * np.pi, 100) # longitude
    phi = np.linspace(0, np.pi, 100) # latitude
    # Create grid
    theta, phi = np.meshgrid(theta, phi)

    # Parametric equations (switch to km)
    xs = (rad_Earth/1000) * np.cos(theta) * np.sin(phi)
    ys = (rad_Earth/1000) * np.sin(theta) * np.sin(phi)
    zs = (rad_Earth/1000) * np.cos(phi)

    # Plot sphere
    # Alpha is the transparency scale (0.7 should allow to see orbit on other side of Earth)
    ax.plot_surface(xs, ys, zs, rstride=1, cstride=1, color='darkblue', alpha = 0.7)

    ax.set_aspect('equal')
    plt.show()



def main():

    # Other variables
    dt = 0.01 # (s)
    t_final = 60000 # (s)
    state = [7500, 0, 0, 600, 7800, 150] # r_x (km), r_y (km), r_z (km), v_x (m/s), v_y (m/s), v_z (m/s)

    # Commented everything with inputs out until J2 Perturbation is resolved
    # state = user_input()

    # Convert positions to meters and altitude to radius from Earth's center
    state = np.array(state, dtype=float)
    state[0:3] = state[0:3] * 1000

    # Grabs a "slice" of the state vector (first and second elements)
    r = state[0:3]
    r_mag = np.linalg.norm(r)

    # Create a variable that will guide how many points will be saved to solution by solve_ivp
    t_eval = np.linspace(0, t_final, 1000)

    # Check for valid conditions of initial position (if not valid stop the program)
    if r_mag <= 6378137:
        print("Error, the body is inside Earth. Exiting...")
        sys.exit()

    # ODE solver (using RK45)
    solution = solve_ivp(deriv_calc, [0, t_final], state, method='RK45', t_eval = t_eval,
    first_step=dt, rtol=1e-9, atol=1e-12)

    plotting(solution)


if __name__ == "__main__":
    main()










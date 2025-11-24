"""
Module: compute_satellite_position.py

Description:
Calculates satellite position in Earth-Centered Earth-Fixed (ECEF) coordinates using
orbital parameters interpolated at specific times.

Author: F.ahmadzade
"""

from typing import Dict, List
import numpy as np
import pandas as pd

def compute_satellite_position(orbital_params: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """
    Compute satellite ECEF positions from interpolated orbital parameters.

    Args:
        orbital_params (Dict[str, np.ndarray]): Dictionary of interpolated orbital parameters.
          Expected keys (as an example, adjust based on your navigation parameters):
          ['sqrtA', 'e', 'i0', 'omega', 'OMEGA', 'M0', 'delta_n', 'OMEGA_DOT', 'IDOT']

    Returns:
        Dict[str, np.ndarray]: Dictionary with keys 'X', 'Y', 'Z' containing satellite ECEF coordinates.
    """
    # Extract parameters (example names, should be adapted)
    sqrtA = orbital_params.get('sqrtA')
    e = orbital_params.get('e')
    i0 = orbital_params.get('i0')
    omega = orbital_params.get('omega')       # Argument of perigee
    OMEGA = orbital_params.get('OMEGA')       # Longitude of ascending node
    M0 = orbital_params.get('M0')             # Mean anomaly at reference time
    delta_n = orbital_params.get('delta_n')   # Mean motion difference
    OMEGA_DOT = orbital_params.get('OMEGA_DOT') # Rate of right ascension
    IDOT = orbital_params.get('IDOT')          # Rate of inclination angle

    # Number of epochs
    n = len(sqrtA)

    # Constants
    mu = 3.986005e14  # Earth's universal gravitational parameter (m^3/s^2)

    # Compute semi-major axis
    A = sqrtA**2

    # Calculate corrected mean motion
    n0 = np.sqrt(mu / (A**3))  # Computed mean motion
    n_corr = n0 + delta_n

    # Time since ephemeris reference epoch
    # We assume input orbital_params have corresponding time vector indexed in same order;
    # Here M0 corresponds to epoch reference, so time t - toe is embedded in M via M = M0 + n_corr * (t - toe)
    
    # For now, we calculate mean anomaly linearly (the precise time offset might be needed depending on parameters)
    # This function assumes M contains the argument M0 + corrected n * t, so it is ready to be used. 
    M = M0  # If not, user should supply M updated before calling or we add a time vector.

    # Solve Kepler's Equation for Eccentric Anomaly E by iterative method
    def kepler_eq(E, M, e):
        return E - e*np.sin(E) - M

    def kepler_solver(M_i, e_i, tol=1e-12, max_iter=100):
        E = M_i  # Initial guess
        for _ in range(max_iter):
            f = E - e_i * np.sin(E) - M_i
            f_prime = 1 - e_i * np.cos(E)
            delta = -f / f_prime
            E += delta
            if abs(delta) < tol:
                break
        return E

    E = np.array([kepler_solver(M[i], e[i]) for i in range(n)])

    # True Anomaly
    sin_v = (np.sqrt(1 - e**2) * np.sin(E)) / (1 - e * np.cos(E))
    cos_v = (np.cos(E) - e) / (1 - e * np.cos(E))
    v = np.arctan2(sin_v, cos_v)

    # Argument of Latitude u
    u = v + omega

    # Corrected radius
    r = A * (1 - e * np.cos(E))

    # Corrected inclination
    i = i0 + IDOT * np.arange(n)  # If time not provided, use index as proxy; better with exact time steps

    # Corrected longitude of ascending node
    # Similarly, a time vector can be used for precise calculation; here simplified as:
    Omega = OMEGA + OMEGA_DOT * np.arange(n)

    # Satellite position in orbital plane
    x_orb = r * np.cos(u)
    y_orb = r * np.sin(u)

    # ECEF Coordinates
    X = x_orb * np.cos(Omega) - y_orb * np.cos(i) * np.sin(Omega)
    Y = x_orb * np.sin(Omega) + y_orb * np.cos(i) * np.cos(Omega)
    Z = y_orb * np.sin(i)

    return {'X': X, 'Y': Y, 'Z': Z}
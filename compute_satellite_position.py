"""
Module: compute_satellite_position.py

Description:
Calculates satellite position in Earth-Centered Earth-Fixed (ECEF) coordinates using
orbital parameters interpolated at specific times.

Author: F.Ahmadzade
"""

from typing import Dict
import numpy as np

def compute_satellite_position(orbital_params: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """
    Compute satellite ECEF positions from interpolated orbital parameters.

    Args:
        orbital_params (Dict[str, np.ndarray]): Dictionary of interpolated orbital parameters.
            Expected keys:
            ['sqrtA', 'e', 'i0', 'omega', 'OMEGA', 'M0', 'delta_n', 'OMEGA_DOT', 'IDOT', 'tk']

            'tk' is the time difference array in seconds from ephemeris reference epoch.

    Returns:
        Dict[str, np.ndarray]: Dictionary with keys 'X', 'Y', 'Z' containing satellite ECEF coordinates.
    """

    # Extract parameters
    sqrtA = orbital_params.get('sqrtA')
    e = orbital_params.get('e')
    i0 = orbital_params.get('i0')
    omega = orbital_params.get('omega')       # Argument of perigee
    OMEGA = orbital_params.get('OMEGA')       # Longitude of ascending node at reference time
    M0 = orbital_params.get('M0')             # Mean anomaly at reference time
    delta_n = orbital_params.get('delta_n')   # Mean motion difference
    OMEGA_DOT = orbital_params.get('OMEGA_DOT') # Rate of right ascension
    IDOT = orbital_params.get('IDOT')          # Rate of inclination angle
    tk = orbital_params.get('tk')              # Time from ephemeris reference epoch (seconds)

    # Number of epochs
    n = len(sqrtA)

    # Earth's universal gravitational parameter (m^3/s^2)
    mu = 3.986005e14

    # Compute semi-major axis
    A = sqrtA**2

    # Computed mean motion (rad/s)
    n0 = np.sqrt(mu / (A**3))

    # Corrected mean motion
    n_corr = n0 + delta_n

    # Mean anomaly at time tk
    M = M0 + n_corr * tk

    # Normalize M within 0 to 2*pi
    M = np.mod(M, 2 * np.pi)

    # Solve Kepler's Equation for Eccentric Anomaly E by iterative method
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

    # True Anomaly v
    sin_v = (np.sqrt(1 - e**2) * np.sin(E)) / (1 - e * np.cos(E))
    cos_v = (np.cos(E) - e) / (1 - e * np.cos(E))
    v = np.arctan2(sin_v, cos_v)

    # Argument of Latitude u
    u = v + omega

    # Radius r
    r = A * (1 - e * np.cos(E))

    # Inclination i corrected
    i = i0 + IDOT * tk

    # Longitude of ascending node corrected
    Omega = OMEGA + (OMEGA_DOT - 7.2921151467e-5) * tk  # Earth rotation rate subtracted

    # Satellite position in orbital plane
    x_orb = r * np.cos(u)
    y_orb = r * np.sin(u)

    # ECEF Coordinates
    X = x_orb * np.cos(Omega) - y_orb * np.cos(i) * np.sin(Omega)
    Y = x_orb * np.sin(Omega) + y_orb * np.cos(i) * np.cos(Omega)
    Z = y_orb * np.sin(i)

    return {'X': X, 'Y': Y, 'Z': Z}
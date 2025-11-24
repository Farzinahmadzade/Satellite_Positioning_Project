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

    # Helper to safely retrieve arrays and replace NaN or None with zeros
    def safe_array_get(key):
        arr = orbital_params.get(key)
        if arr is None:
            return np.zeros_like(orbital_params['tk'])
        arr = np.array(arr)
        arr = np.where(np.isnan(arr), 0.0, arr)
        return arr

    sqrtA = safe_array_get('sqrtA')
    e = safe_array_get('e')
    i0 = safe_array_get('i0')
    omega = safe_array_get('omega')       # Argument of perigee
    OMEGA = safe_array_get('OMEGA')       # Longitude of ascending node at reference time
    M0 = safe_array_get('M0')              # Mean anomaly at reference time
    delta_n = safe_array_get('delta_n')   # Mean motion difference
    OMEGA_DOT = safe_array_get('OMEGA_DOT') # Rate of right ascension
    IDOT = safe_array_get('IDOT')          # Rate of inclination angle
    tk = safe_array_get('tk')              # Time from ephemeris reference epoch (seconds)

    n = len(sqrtA)
    mu = 3.986005e14  # Earth's universal gravitational parameter (m^3/s^2)

    A = sqrtA**2
    n0 = np.sqrt(mu / (A**3))
    n_corr = n0 + delta_n

    M = M0 + n_corr * tk
    M = np.mod(M, 2 * np.pi)

    def kepler_solver(M_i, e_i, tol=1e-12, max_iter=100):
        E = M_i
        for _ in range(max_iter):
            f = E - e_i * np.sin(E) - M_i
            f_prime = 1 - e_i * np.cos(E)
            delta = -f / f_prime
            E += delta
            if abs(delta) < tol:
                break
        return E

    E = np.array([kepler_solver(M[i], e[i]) for i in range(n)])

    sin_v = (np.sqrt(1 - e**2) * np.sin(E)) / (1 - e * np.cos(E))
    cos_v = (np.cos(E) - e) / (1 - e * np.cos(E))
    v = np.arctan2(sin_v, cos_v)

    u = v + omega
    r = A * (1 - e * np.cos(E))
    i = i0 + IDOT * tk
    Omega = OMEGA + (OMEGA_DOT - 7.2921151467e-5) * tk  # Earth's rotation rate subtracted

    x_orb = r * np.cos(u)
    y_orb = r * np.sin(u)

    X = x_orb * np.cos(Omega) - y_orb * np.cos(i) * np.sin(Omega)
    Y = x_orb * np.sin(Omega) + y_orb * np.cos(i) * np.cos(Omega)
    Z = y_orb * np.sin(i)

    return {'X': X, 'Y': Y, 'Z': Z}

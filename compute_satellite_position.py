"""
Module: compute_satellite_position.py

Description:
Calculates satellite position in Earth-Centered Earth-Fixed (ECEF) coordinates using
orbital parameters interpolated at specific times.

Author: F.Ahmadzade
"""

import numpy as np

# GNSS CONSTANTS (WGS84 + GPS)
C = 299792458.0            # Speed of light [m/s]
MU = 3.986005e14           # Earth gravitational constant [m³/s²]
OMEGA_EARTH = 7.292115e-5  # Earth rotation rate [rad/s]
F = -4.442807633e-10       # GPS relativistic parameter

def compute_satellite_position(orbital_params):
    """
    GPS Broadcast Ephemeris → ECEF Position (IS-GPS-200 compliant)
    
    Args:
        orbital_params: dict with keys ['tk','sqrtA','e','i0','omega','OMEGA','M0',
                                       'delta_n','OMEGA_DOT','IDOT','Cuc','Cus','Crc',
                                       'Crs','Cic','Cis']
    
    Returns:
        dict: {'X':ecef_x, 'Y':ecef_y, 'Z':ecef_z, 'r':radius}
    """
    
    # Safe parameter extraction (vectorized)
    def safe_get(key, default=0.0):
        arr = orbital_params.get(key, None)
        if arr is None:
            return np.full_like(orbital_params['tk'], default)
        return np.nan_to_num(arr.flatten())
    
    # Extract Keplerian + perturbation parameters
    sqrtA = safe_get('sqrtA')
    e = np.abs(safe_get('e'))  # Eccentricity ≥ 0
    i0 = safe_get('i0')
    omega = safe_get('omega')
    OMEGA = safe_get('OMEGA')
    M0 = safe_get('M0')
    delta_n = safe_get('delta_n')
    OMEGA_DOT = safe_get('OMEGA_DOT')
    IDOT = safe_get('IDOT')
    tk = safe_get('tk')
    
    # Harmonic corrections (radius + angle perturbations)
    Cuc = safe_get('Cuc', 0.0)
    Cus = safe_get('Cus', 0.0)
    Crc = safe_get('Crc', 0.0)
    Crs = safe_get('Crs', 0.0)
    Cic = safe_get('Cic', 0.0)
    Cis = safe_get('Cis', 0.0)
    
    # 1. KEPLERIAN ORBIT ELEMENTS
    A = sqrtA**2                # Semi-major axis [m]
    n0 = np.sqrt(MU / A**3)     # Nominal mean motion [rad/s]
    n = n0 + delta_n            # Corrected mean motion
    
    # 2. MEAN ANOMALY
    M = M0 + n * tk
    
    # GPS relativistic correction
    a_dot = 0
    F_rel = -2 * np.sqrt(MU / A) / C**2 * e * sqrtA * (1 + 0.5 * a_dot * tk / A)
    M = np.mod(M + F_rel, 2 * np.pi)
    
    # 3. KEPLER EQUATION SOLVER
    E = M.copy()
    for _ in range(12):
        sinE, cosE = np.sin(E), np.cos(E)
        delta_E = (M - E + e * sinE) / (1 - e * cosE)
        E += delta_E
        E = np.mod(E, 2 * np.pi)
        if np.max(np.abs(delta_E)) < 1e-12:
            break
    
    # 4. TRUE ANOMALY
    sin_v = np.sqrt((1 + e) / (1 - e)) * np.sin(E/2)
    cos_v = np.cos(E/2)
    nu = 2 * np.arctan2(sin_v, cos_v)
    
    # 5. ORBIT PERTURBATIONS
    phi = nu + omega  # Argument of latitude
    
    # Second harmonic corrections
    delta_u = Cuc * np.cos(2 * phi) + Cus * np.sin(2 * phi)  # Along-track
    delta_r = Crc * np.cos(2 * phi) + Crs * np.sin(2 * phi)  # **Radial wobble**
    delta_i = Cic * np.cos(2 * phi) + Cis * np.sin(2 * phi)  # Cross-track
    
    # Orbit frame coordinates
    u = phi + delta_u
    r = A * (1 - e * np.cos(E)) + delta_r
    i = i0 + IDOT * tk + delta_i
    
    # 6. RIGHT ASCENSION + EARTH ROTATION
    Omega = np.mod(OMEGA + OMEGA_DOT * tk, 2 * np.pi)
    theta_earth = OMEGA_EARTH * tk
    
    # 7. ECEF TRANSFORMATION
    x_orb = r * np.cos(u)
    y_orb = r * np.sin(u)
    
    # ECEF coordinates (ITRF reference frame)
    X = x_orb * np.cos(Omega - theta_earth) - y_orb * np.cos(i) * np.sin(Omega - theta_earth)
    Y = x_orb * np.sin(Omega - theta_earth) + y_orb * np.cos(i) * np.cos(Omega - theta_earth)
    Z = y_orb * np.sin(i)
    
    # VALIDATION
    radius = np.sqrt(X**2 + Y**2 + Z**2)
    
    # Check GPS orbit reasonableness
    if np.mean(radius) < 2.5e7 or np.mean(radius) > 2.8e7:
        print("⚠️  WARNING: Unrealistic orbit radius detected!")
    
    return {
        'X': X,           # ECEF X [m]
        'Y': Y,           # ECEF Y [m]  
        'Z': Z,           # ECEF Z [m]
        'r': radius,      # Radial distance [m]
        'A': A,           # Semi-major axis [m]
        'e': e,           # Eccentricity
        'i': i            # Inclination [rad]
    }

def validate_orbit(positions):
    """GNSS orbit validation"""
    r_km = positions['r'] / 1000
    print(f"   Orbit radius:     {np.mean(r_km):7.1f} ± {np.std(r_km):5.1f} km")
    print(f"   Range:            {np.min(r_km):7.1f} - {np.max(r_km):7.1f} km")
    print(f"   Ellipticity:      {(np.max(r_km)-np.min(r_km))/np.mean(r_km)*100:4.2f}%")
    print(f"   GPS valid:        {'✅ PASS' if 26000 < np.mean(r_km) < 27000 else '❌ FAIL'}")

# Test function
if __name__ == "__main__":
    t_test = np.linspace(0, 7200, 241)
    
    test_params = {
        'tk': t_test,
        'sqrtA': np.full_like(t_test, 5153.8),
        'e': np.full_like(t_test, 0.01),
        'i0': np.full_like(t_test, np.deg2rad(54)),
        'omega': np.full_like(t_test, 1.25),
        'OMEGA': np.full_like(t_test, 2.35),
        'M0': np.mod(np.sqrt(MU/(5153.8**6)) * t_test, 2*np.pi),
        'delta_n': np.full_like(t_test, 5e-10),
        'OMEGA_DOT': np.zeros_like(t_test),
        'IDOT': np.zeros_like(t_test),
        'Crc': np.full_like(t_test, 200),
        'Crs': np.full_like(t_test, -2)
    }
    
    pos = compute_satellite_position(test_params)
    validate_orbit(pos)
    
    print("\n✅ compute_satellite_position.py ready!")
    print("Usage: positions = compute_satellite_position(params)")
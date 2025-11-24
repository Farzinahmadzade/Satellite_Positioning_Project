"""
GNSS Constants and Frequencies
------------------------------
Defines carrier frequencies, wavelengths, and combination coefficients
for GPS, GLONASS, Galileo, BeiDou

Author: F.Ahmadzade
"""

# Speed of light (m/s)
C = 299792458.0

# ==================== GPS ====================
# GPS L1/L2 frequencies (Hz)
GPS_F1 = 1575.42e6  # L1
GPS_F2 = 1227.60e6  # L2

# GPS wavelengths (meters)
GPS_L1 = C / GPS_F1  # ≈ 0.1903 m
GPS_L2 = C / GPS_F2  # ≈ 0.2442 m

# GPS combination coefficients
ALPHA_GPS = (GPS_F1 / GPS_F2) ** 2  # ≈ 1.6469
F1_GPS = GPS_F1 / 1e6  # MHz for display
F2_GPS = GPS_F2 / 1e6  # MHz for display

# ==================== Galileo ====================
GALILEO_F1 = 1575.42e6  # E1
GALILEO_F2 = 1176.45e6  # E5a
GALILEO_L1 = C / GALILEO_F1
GALILEO_L2 = C / GALILEO_F2
ALPHA_GALILEO = (GALILEO_F1 / GALILEO_F2) ** 2

# ==================== BeiDou ====================
BEIDOU_F1 = 1561.098e6  # B1
BEIDOU_F2 = 1207.140e6  # B2
BEIDOU_L1 = C / BEIDOU_F1
BEIDOU_L2 = C / BEIDOU_F2
ALPHA_BEIDOU = (BEIDOU_F1 / BEIDOU_F2) ** 2

# ==================== GLONASS ====================
# GLONASS frequency channel numbers (k = -7 to +6)
GLONASS_K = {
    'R01': 1,  'R02': -4, 'R03': 5,  'R04': 6,  'R05': 1,  'R06': -4,
    'R07': 5,  'R08': 6,  'R09': -2, 'R10': -7, 'R11': 0,  'R12': -1,
    'R13': -2, 'R14': -7, 'R15': 0,  'R16': -1, 'R17': 4,  'R18': -3,
    'R19': 3,  'R20': 2,  'R21': 4,  'R22': -3, 'R23': 3,  'R24': 2
}

def get_glonass_frequencies(sat_id: str) -> tuple:
    """
    Get GLONASS frequencies for a specific satellite.
    
    Args:
        sat_id: Satellite ID (e.g., 'R01', 'R15')
    
    Returns:
        (F1, F2, L1, L2, alpha) in Hz, meters, and coefficient
    """
    k = GLONASS_K.get(sat_id, 0)
    
    # GLONASS FDMA frequencies (MHz to Hz)
    F1 = (1602.0 + k * 0.5625) * 1e6
    F2 = (1246.0 + k * 0.4375) * 1e6
    
    # Wavelengths
    L1 = C / F1
    L2 = C / F2
    
    # Alpha coefficient
    alpha = (F1 / F2) ** 2
    
    return F1, F2, L1, L2, alpha

def get_frequencies(sat_system: str, sat_id: str = None) -> dict:
    """
    Get carrier frequencies and wavelengths for a satellite system.
    
    Args:
        sat_system: 'G' (GPS), 'R' (GLONASS), 'E' (Galileo), 'C' (BeiDou)
        sat_id: Full satellite ID (required for GLONASS, e.g., 'R01')
    
    Returns:
        dict with keys: 'F1', 'F2', 'L1', 'L2', 'alpha'
    """
    if sat_system == 'G':  # GPS
        return {
            'F1': GPS_F1, 'F2': GPS_F2,
            'L1': GPS_L1, 'L2': GPS_L2,
            'alpha': ALPHA_GPS
        }
    elif sat_system == 'R':  # GLONASS
        if sat_id is None:
            raise ValueError("GLONASS requires satellite ID")
        F1, F2, L1, L2, alpha = get_glonass_frequencies(sat_id)
        return {
            'F1': F1, 'F2': F2,
            'L1': L1, 'L2': L2,
            'alpha': alpha
        }
    elif sat_system == 'E':  # Galileo
        return {
            'F1': GALILEO_F1, 'F2': GALILEO_F2,
            'L1': GALILEO_L1, 'L2': GALILEO_L2,
            'alpha': ALPHA_GALILEO
        }
    elif sat_system == 'C':  # BeiDou
        return {
            'F1': BEIDOU_F1, 'F2': BEIDOU_F2,
            'L1': BEIDOU_L1, 'L2': BEIDOU_L2,
            'alpha': ALPHA_BEIDOU
        }
    else:
        # Default to GPS
        return {
            'F1': GPS_F1, 'F2': GPS_F2,
            'L1': GPS_L1, 'L2': GPS_L2,
            'alpha': ALPHA_GPS
        }

# Confirmation print
print(f"✓ Constants loaded:")
print(f"  GPS: F1={F1_GPS:.2f} MHz, F2={F2_GPS:.2f} MHz, λ1={GPS_L1:.4f} m, λ2={GPS_L2:.4f} m")
print(f"  Alpha (GPS): {ALPHA_GPS:.4f}")
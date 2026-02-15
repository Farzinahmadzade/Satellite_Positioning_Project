"""
GNSS Constants and Frequencies
------------------------------
Defines carrier frequencies, wavelengths, and combination coefficients
for GPS, GLONASS, Galileo, BeiDou

Author: F.Ahmadzade
"""

import numpy as np

# Global constants
C = 299792458.0  # m/s

# GPS
GPS_L1 = 1575.42e6  # L1 C/A, P(Y)
GPS_L2 = 1227.60e6  # L2 P(Y), L2C
GPS_L5 = 1176.45e6  # L5 (modern)

GPS_lambda1 = C / GPS_L1  # 0.190293 m
GPS_lambda2 = C / GPS_L2  # 0.244210 m
GPS_lambda5 = C / GPS_L5  # 0.254824 m

ALPHA_GPS_12 = (GPS_L1 / GPS_L2) ** 2  # 1.6469 (iono-free)

# Galileo
E1 = 1575.42e6    # E1 B+C
E5A = 1176.45e6   # E5a
E5B = 1207.14e6   # E5b
E6 = 1278.75e6    # E6

GALILEO_L1 = C / E1
GALILEO_L5A = C / E5A
ALPHA_GALILEO = (E1 / E5A) ** 2

# BeiDou
B1C = 1575.42e6   # B1C (GPS-compatible)
B2A = 1176.45e6   # B2a (L5-compatible)
B3I = 1268.52e6   # B3

BEIDOU_L1 = C / B1C
BEIDOU_L5 = C / B2A
ALPHA_BEIDOU = (B1C / B2A) ** 2

# GLONASS
GLONASS_K_NUMBERS = {
    'R01': 1, 'R02': -4, 'R03': 5, 'R04': 6, 'R05': 1, 'R06': -4,
    'R07': 5, 'R08': 6, 'R09': -2, 'R10': -7, 'R11': 0, 'R12': -1,
    'R13': -2, 'R14': -7, 'R15': 0, 'R16': -1, 'R17': 4, 'R18': -3,
    'R19': 3, 'R20': 2, 'R21': 4, 'R22': -3, 'R23': 3, 'R24': 2
}

def glonass_frequencies(prn: str) -> tuple:
    """GLONASS L1/L2 frequencies (Hz, m, alpha)"""
    k = GLONASS_K_NUMBERS.get(prn, 0)
    
    # GLONASS frequency model (RINEX 3.04)
    f1 = 1602.0e6 + k * 0.5625e6  # L1
    f2 = 1246.0e6 + k * 0.4375e6  # L2
    
    l1, l2 = C / f1, C / f2
    alpha = (f1 / f2) ** 2
    
    return f1, f2, l1, l2, alpha

# Universal Interface
def get_gnss_frequencies(system: str, prn: str = None) -> dict:
    """Receive frequencies based on system and PRN"""
    
    if system == 'G':  # GPS
        return {
            'f1': GPS_L1, 'f2': GPS_L2, 'f5': GPS_L5,
            'l1': GPS_lambda1, 'l2': GPS_lambda2, 'l5': GPS_lambda5,
            'alpha_12': ALPHA_GPS_12
        }
    elif system == 'E':  # Galileo
        return {
            'f1': E1, 'f5a': E5A, 'f5b': E5B,
            'l1': GALILEO_L1, 'l5a': GALILEO_L5A,
            'alpha': ALPHA_GALILEO
        }
    elif system == 'C':  # BeiDou
        return {
            'f1': B1C, 'f2': B2A,
            'l1': BEIDOU_L1, 'l2': BEIDOU_L5,
            'alpha': ALPHA_BEIDOU
        }
    elif system == 'R':  # GLONASS
        if prn is None:
            raise ValueError("GLONASS needs PRN (e.g., 'R01')")
        f1, f2, l1, l2, alpha = glonass_frequencies(prn)
        return {'f1': f1, 'f2': f2, 'l1': l1, 'l2': l2, 'alpha': alpha}
    else:
        return get_gnss_frequencies('G')  # Default GPS

# Testing and validation
if __name__ == "__main__":
    print("✅ GNSS Constants Validation (2026 standards)")
    print(f"GPS L1:  {GPS_lambda1*1e3:.1f} mm  |  α12: {ALPHA_GPS_12:.4f}")
    print(f"GLONASS R01 L1: {glonass_frequencies('R01')[2]*1e3:.1f} mm")
    print(f"Galileo E1:     {GALILEO_L1*1e3:.1f} mm")
    print(f"BeiDou B1C:     {BEIDOU_L1*1e3:.1f} mm")

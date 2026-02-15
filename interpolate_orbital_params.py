"""
Module: interpolate_orbital_params.py

Description:
Interpolate satellite orbital navigation parameters at specified times.
Interpolation ensures continuous and accurate parameter values for position calculation.

Author: F.Ahmadzade
"""

from typing import Dict, List
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

# GNSS Ephemeris parameter classification (RINEX 3.04)
STATIC_PARAMS = ['sqrtA', 'delta_n', 'OMEGA_DOT', 'IDOT']
LINEAR_PARAMS = ['e', 'i0', 'omega', 'M0', 'OMEGA', 'Cuc', 'Cus', 'Crc', 'Crs', 'Cic', 'Cis']
ALL_PARAMS = STATIC_PARAMS + LINEAR_PARAMS

def interpolate_orbital_params(nav_data: pd.DataFrame, time_list: List[pd.Timestamp], 
                              max_extrapolate_sec: float = 7200) -> Dict[str, np.ndarray]:
    """
    GNSS-standard interpolation with validity checks
    
    Args:
        nav_data: time-indexed ephemeris DataFrame
        time_list: target times
        max_extrapolate_sec: maximum extrapolation (default 2hr)
    
    Returns:
        interpolated parameters with NaN out of validity
    """
    if nav_data.empty:
        raise ValueError("Empty navigation data")
    
    nav_data = nav_data.sort_index()
    base_time = nav_data.index[0]
    nav_times_sec = (nav_data.index - base_time).total_seconds()
    target_times_sec = np.array([(t - base_time).total_seconds() for t in time_list])
    
    interpolated = {}
    
    for param in nav_data.columns:
        if param not in ALL_PARAMS:
            print(f"⚠️ Unknown parameter '{param}' - using linear")
        
        y = nav_data[param].values
        valid_mask = ~np.isnan(y)
        
        if valid_mask.sum() < 1:
            interpolated[param] = np.full_like(target_times_sec, np.nan)
            continue
        
        # GNSS-specific interpolation strategy
        if param in STATIC_PARAMS:
            # Step function: nearest valid ephemeris
            interp_func = interp1d(nav_times_sec[valid_mask], y[valid_mask],
                                 kind='previous', bounds_error=False, 
                                 fill_value=np.nan)
        else:
            # Linear for dynamic parameters
            interp_func = interp1d(nav_times_sec[valid_mask], y[valid_mask],
                                 kind='linear', bounds_error=False, 
                                 fill_value=np.nan)
        
        interpolated[param] = interp_func(target_times_sec)
        
        # Validity check: NaN outside ±2hr of each ephemeris
        interpolated[param] = np.where(
            np.abs(target_times_sec - nav_times_sec[valid_mask][np.argmin(np.abs(nav_times_sec[valid_mask] - target_times_sec[:, None]))]) > max_extrapolate_sec,
            np.nan, interpolated[param]
        )
    
    # Debug info
    valid_count = sum(~np.isnan(interpolated['sqrtA']))
    print(f"✓ Interpolated {valid_count}/{len(time_list)} epochs ({100*valid_count/len(time_list):.1f}%)")
    
    return interpolated

# Realistic GNSS test
if __name__ == "__main__":
    # Real GPS ephemeris pattern: constant + slow drift
    times = pd.date_range("2026-02-13 00:00", periods=5, freq='2H')
    
    nav_data = pd.DataFrame({
        'sqrtA': [5153.795] * 5,                     # CONSTANT
        'e': [0.01, 0.0101, 0.0102, 0.0101, 0.01],   # LINEAR drift
        'i0': np.linspace(0.94, 0.945, 5),
        'M0': np.linspace(0.1, 0.3, 5),
        'OMEGA': [0.5, 0.51, 0.52, 0.53, 0.54],
    }, index=times)
    
    target_times = pd.date_range("2026-02-13 00:30", periods=50, freq='30Min')
    result = interpolate_orbital_params(nav_data, target_times)
    
    print("Sample interpolated sqrtA (must be constant):")
    print(result['sqrtA'][:5])
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

def interpolate_orbital_params(nav_data: pd.DataFrame, 
                              time_list: List[pd.Timestamp]) -> Dict[str, np.ndarray]:
    """
    Interpolate orbital parameters from navigation data to target times.

    Args:
        nav_data (pd.DataFrame): Navigation data with time as index and orbital parameters as columns.
        time_list (List[pd.Timestamp]): List of target timestamps for interpolation.

    Returns:
        Dict[str, np.ndarray]: Dictionary of orbital parameters interpolated at target times.
            Keys are parameter names, values are numpy arrays.
    """
    if nav_data.empty:
        raise ValueError("Navigation data is empty.")

    # Ensure data is sorted by time
    nav_data = nav_data.sort_index()

    # Convert times to seconds relative to base_time
    base_time = nav_data.index[0]
    time_seconds = (nav_data.index - base_time).total_seconds()
    target_seconds = np.array([(t - base_time).total_seconds() for t in time_list])

    interpolated_params = {}
    for param in nav_data.columns:
        y = nav_data[param].values
        valid_mask = ~np.isnan(y)
        if valid_mask.sum() < 2:
            # Insufficient valid data to interpolate
            interpolated_params[param] = np.full_like(target_seconds, np.nan, dtype=float)
            continue

        interp_func = interp1d(time_seconds[valid_mask], y[valid_mask],
                               kind='linear', bounds_error=False, fill_value='extrapolate')
        interpolated_params[param] = interp_func(target_seconds)

    return interpolated_params

if __name__ == "__main__":
    # Example usage with dummy data
    import pandas as pd

    dates = pd.date_range("2025-11-24 00:00:00", periods=5, freq='30T')
    data = {
        'sqrtA': [5153.795, 5153.795, 5153.795, 5153.795, 5153.795],
        'e': [0.01, 0.011, 0.012, 0.0115, 0.01],
        'i0': [0.94, 0.941, 0.942, 0.943, 0.944],
        'omega': [1.0, 1.001, 1.002, 1.003, 1.002],
        'OMEGA': [0.5, 0.51, 0.52, 0.53, 0.54],
        'M0': [0.1, 0.15, 0.2, 0.25, 0.3],
        'delta_n': [0.0001, 0.0001, 0.0001, 0.0001, 0.0001],
        'OMEGA_DOT': [-8.0e-9, -8.0e-9, -8.0e-9, -8.0e-9, -8.0e-9],
        'IDOT': [0.0, 0.0, 0.0, 0.0, 0.0]
    }
    nav_df = pd.DataFrame(data, index=dates)

    target_times = pd.date_range("2025-11-24 00:10:00", periods=10, freq='10T')
    result = interpolate_orbital_params(nav_df, target_times)
    for key, val in result.items():
        print(f"{key}: {val}")
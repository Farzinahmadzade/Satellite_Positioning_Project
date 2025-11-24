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

    # Convert target times to numeric values (e.g., seconds since epoch)
    base_time = nav_data.index[0]
    time_seconds = (nav_data.index - base_time).total_seconds()
    target_seconds = np.array([(t - base_time).total_seconds() for t in time_list])

    interpolated_params = {}
    for param in nav_data.columns:
        y = nav_data[param].values
        # Remove NaNs for interpolation if any
        valid_mask = ~np.isnan(y)
        if valid_mask.sum() < 2:
            # Not enough points to interpolate; fill with NaNs
            interpolated_params[param] = np.full_like(target_seconds, np.nan)
            continue

        interp_func = interp1d(time_seconds[valid_mask], y[valid_mask], kind='linear',
                               bounds_error=False, fill_value="extrapolate")
        interpolated_params[param] = interp_func(target_seconds)

    return interpolated_params
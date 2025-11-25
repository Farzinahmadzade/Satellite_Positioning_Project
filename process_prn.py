"""
Module: process_prn.py

Description:
Main pipeline function for GNSS satellite trajectory computation.
Given a navigation file and target PRN, extracts relevant ephemeris data
by selecting the closest ephemeris in time to observation time (or midpoint),
generates sample epochs, interpolates orbital parameters, computes 3D ECEF positions,
and outputs results as a DataFrame. Optionally saves to CSV and renders a 3D plot.

Author: F.Ahmadzade
"""

import pandas as pd
import numpy as np
from read_navigation import read_navigation_file, get_ephemeris_batch
from generate_times import generate_times
from interpolate_orbital_params import interpolate_orbital_params
from compute_satellite_position import compute_satellite_position
from save_to_csv import save_to_csv
from plot_3d_path import plot_3d_path


def process_prn(nav_filepath, prn, obs_time=None, save_csv=True, show_plot=True):
    """
    Computes ECEF satellite positions for a given PRN using a RINEX navigation file.

    Args:
        nav_filepath (str): Path to RINEX navigation file (*.21n)
        prn (str): PRN of GNSS satellite (e.g., 'G05')
        obs_time (pd.Timestamp or None): Observation time for ephemeris extraction.
                                         If None, defaults to midpoint of file time range.
        save_csv (bool): Whether to save output results to CSV file (default: True)
        show_plot (bool): Whether to display a 3D trajectory plot (default: True)

    Returns:
        pd.DataFrame or None: DataFrame with columns ['t', 'x', 'y', 'z'], or None if ephemeris not found.
    """

    # Load navigation data
    nav_data = read_navigation_file(nav_filepath, systems=prn[0])

    # Determine default obs_time (midpoint)
    if obs_time is None:
        times = nav_data.time.values
        if len(times) == 0:
            raise ValueError("No valid times found in navigation data to use for obs_time.")
        obs_time = pd.Timestamp(times[len(times) // 2])

    # Find closest ephemeris before or equal to obs_time for the given PRN
    # Iterate backwards in time to find valid ephemeris
    times_nav = nav_data.time.values
    sat_nav = nav_data.sel(sv=prn, method='nearest')

    # Find ephemeris time stamps for the satellite
    eph_times = pd.to_datetime(sat_nav.time.values)

    # Find ephemeris nearest to obs_time within tolerance (e.g. 4 hours)
    max_age_hours = 4
    valid_eph_times = [t for t in eph_times if abs((t - obs_time).total_seconds()) <= max_age_hours * 3600]

    if not valid_eph_times:
        print(f"No ephemeris within {max_age_hours} hours of observation time {obs_time} for satellite {prn}.")
        return None

    # Choose the ephemeris closest to obs_time
    closest_eph_time = min(valid_eph_times, key=lambda t: abs((t - obs_time).total_seconds()))

    # Extract ephemeris at closest time (using get_ephemeris)
    eph = None
    try:
        eph = get_ephemeris(nav_data, prn, closest_eph_time)
    except Exception as e:
        print(f"Error extracting ephemeris for {prn} at {closest_eph_time}: {e}")
        return None

    if eph is None:
        print(f"Ephemeris not found for PRN {prn} at time {closest_eph_time}. Computation aborted.")
        return None

    start_time = eph['eph_time']
    end_time = start_time + pd.Timedelta(hours=23, minutes=59, seconds=59)

    # Generate time samples every 30 seconds
    times = generate_times(start_time, end_time, interval_sec=30)

    # Clean ephemeris data into floats or NaN
    cleaned_ephemeris = {}
    for k, v in eph.items():
        try:
            cleaned_ephemeris[k] = float(v)
        except (TypeError, ValueError):
            cleaned_ephemeris[k] = np.nan

    # Build DataFrame with ephemeris repeated for all times for interpolation
    nav_df = pd.DataFrame({k: [v] * len(times) for k, v in cleaned_ephemeris.items()})
    nav_df['time'] = pd.Series(times).values
    nav_df = nav_df.set_index('time').astype(float)

    # Interpolate orbital parameters to all sample times
    orbital_params = interpolate_orbital_params(nav_df, times)

    # Compute relative time tk in seconds from first timepoint for navigation
    base_time = nav_df.index[0]
    tk_seconds = np.array([(t - base_time).total_seconds() for t in nav_df.index])
    orbital_params['tk'] = tk_seconds

    # Compute satellite ECEF positions (X, Y, Z)
    positions = compute_satellite_position(orbital_params)

    # Build output DataFrame
    df_out = pd.DataFrame({
        't': times,
        'x': positions['X'],
        'y': positions['Y'],
        'z': positions['Z']
    })

    # Save CSV if requested
    if save_csv:
        out_filename = f'output_{prn}.csv'
        save_to_csv(positions, out_filename, timestamps=pd.Series(times))
        print(f"Output CSV saved to {out_filename}")

    # Show 3D plot if requested
    if show_plot:
        plot_3d_path(positions, title=f"Satellite {prn} 3D Trajectory")

    return df_out

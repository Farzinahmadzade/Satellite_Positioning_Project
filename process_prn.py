"""
Module: process_prn.py

Description:
Main pipeline function for GNSS satellite trajectory computation. Given a navigation file and target PRN,
extracts relevant ephemeris data, generates sample epochs, interpolates orbital parameters, and computes
3D ECEF positions at specified intervals. Outputs results as a DataFrame and optionally saves to CSV and
renders a 3D trajectory plot. Designed for single satellite analysis and as the final callable interface
of the project.

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

def process_prn(nav_filepath, prn, save_csv=True, show_plot=True):
    """
    Computes ECEF satellite positions for a given PRN using a RINEX navigation file.

    Args:
        nav_filepath (str): Path to RINEX navigation file (*.21n)
        prn (str): PRN of GNSS satellite (e.g., 'G05' or '05')
        save_csv (bool): Whether to save output results to CSV file (default: True)
        show_plot (bool): Whether to display a 3D trajectory plot (default: True)

    Returns:
        pd.DataFrame: DataFrame with columns ['t', 'x', 'y', 'z']
    """

    # Load navigation data
    nav_data = read_navigation_file(nav_filepath, systems=prn[0])

    # Print available PRNs for debug
    available_prns = list(nav_data.keys())
    print("Available PRNs in nav_data:", available_prns)

    # Try to match input PRN with available keys
    prn_key = None
    if prn in available_prns:
        prn_key = prn
    elif prn[-2:] in available_prns:
        prn_key = prn[-2:]  # e.g. 'G05' -> '05'
    elif prn.startswith('G') and prn[1:] in available_prns:
        prn_key = prn[1:]   # e.g. 'G05' -> '05'
    else:
        raise ValueError(f"PRN {prn} not found. Available: {available_prns}")

    # Select a reasonable start_time from ephemeris for chosen PRN
    eph_dict = get_ephemeris_batch(nav_data, [prn_key], None)
    if prn_key not in eph_dict:
        raise ValueError(f'PRN {prn_key} not found in navigation file.')
    eph = eph_dict[prn_key]

    start_time = eph['epoch']
    end_time = start_time + pd.Timedelta(hours=23, minutes=59, seconds=59)

    # Generate time samples at 30-second intervals
    times = generate_times(start_time, end_time, interval_sec=30)

    # Build DataFrame for interpolation (ephemeris repeated for all times)
    cleaned_ephemeris = {}
    for k, v in eph.items():
        try:
            cleaned_ephemeris[k] = float(v)
        except (TypeError, ValueError):
            cleaned_ephemeris[k] = np.nan
    nav_df = pd.DataFrame({k: [v]*len(times) for k, v in cleaned_ephemeris.items()})
    nav_df['time'] = pd.Series(times).values
    nav_df = nav_df.set_index('time')
    nav_df = nav_df.astype(float)

    # Interpolate orbital parameters and compute 'tk' (relative time in seconds)
    orbital_params = interpolate_orbital_params(nav_df, times)
    base_time = nav_df.index[0]
    tk_seconds = np.array([(t - base_time).total_seconds() for t in nav_df.index])
    orbital_params['tk'] = tk_seconds

    # Compute ECEF positions
    positions = compute_satellite_position(orbital_params)

    # Build output DataFrame
    df_out = pd.DataFrame({
        't': times,
        'x': positions['X'],
        'y': positions['Y'],
        'z': positions['Z']
    })

    # (Optional) Save to CSV
    if save_csv:
        out_filename = f'output_{prn_key}.csv'
        save_to_csv(positions, out_filename, timestamps=pd.Series(times))
        print(f"Results saved to {out_filename}")

    # (Optional) Show 3D plot
    if show_plot:
        plot_3d_path(positions, title=f"Satellite {prn_key} 3D Path")

    return df_out
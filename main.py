"""
Module: main.py

Description:
Main script to run the satellite positioning pipeline.
Reads RINEX navigation and observation files, interpolates orbital parameters,
computes satellite ECEF positions, saves results to CSV, and plots 3D satellite orbits.

Author: F.Ahmadzade
"""

import os
import numpy as np
import pandas as pd
from read_rinex import read_rinex, get_observation_summary
from read_navigation import read_navigation_file, get_ephemeris_batch
from get_time_range import get_time_range
from generate_times import generate_times
from interpolate_orbital_params import interpolate_orbital_params
from compute_satellite_position import compute_satellite_position
from save_to_csv import save_to_csv
from plot_3d_path import plot_3d_path
from read_navigation import to_float


def main():
    nav_file = r"K:\GitHub\Satellite_Positioning_Project\Data\brdc2580.21n"
    obs_file = r"K:\GitHub\Satellite_Positioning_Project\Data\tehn2580.21o"
    prn = 'G05'  # Target satellite PRN for processing

    if not os.path.exists(nav_file):
        print(f"Navigation file not found: {nav_file}")
        return

    if not os.path.exists(obs_file):
        print(f"Observation file not found: {obs_file}")
        return

    print("Loading navigation data...")
    nav_data = read_navigation_file(nav_file, systems='G')

    print("Loading observation data...")
    sat_dict = read_rinex(obs_file, systems='G', min_epochs=3, verbose=True)

    print("Summary of loaded satellites (observations):")
    print(get_observation_summary(sat_dict).to_string(index=False))

    if prn not in sat_dict:
        print(f"Satellite {prn} not found in observations.")
        return

    print(f"Extracting observation time range for satellite {prn}...")
    start_time, end_time = get_time_range(sat_dict, prn)
    print(f"Observation interval: {start_time} to {end_time}")

    print("Generating sampling times at 30-second intervals...")
    times = generate_times(start_time, end_time, interval_sec=30)

    print("Extracting ephemeris for satellite batch...")
    eph_dict = get_ephemeris_batch(nav_data, [prn], times[0])

    if prn not in eph_dict:
        print(f"No valid ephemeris found for satellite {prn} at starting time.")
        return

    # Convert ephemeris values explicitly to float or np.nan to avoid None type
    cleaned_ephemeris = {}
    for k, v in eph_dict[prn].items():
        try:
            val = float(v)
            if val is None:
                val = np.nan
            cleaned_ephemeris[k] = val
        except (TypeError, ValueError):
            cleaned_ephemeris[k] = np.nan

    nav_df = pd.DataFrame({k: [v] * len(times) for k, v in cleaned_ephemeris.items()})
    nav_df['time'] = pd.Series(times).values
    nav_df = nav_df.set_index('time')

    nav_df = nav_df.astype(float)  # Ensure numeric type for interpolation

    print("Interpolating orbital parameters over sample times...")
    orbital_params = interpolate_orbital_params(nav_df, times)

    # Add 'tk' : time difference array in seconds from reference
    base_time = nav_df.index[0]
    tk_seconds = np.array([(t - base_time).total_seconds() for t in nav_df.index])
    orbital_params['tk'] = tk_seconds

    print("Computing satellite ECEF positions...")
    positions = compute_satellite_position(orbital_params)

    output_csv = "output_satellite_positions.csv"
    print(f"Saving satellite positions to {output_csv}...")
    save_to_csv(positions, output_csv, timestamps=pd.Series(times))

    print("Plotting satellite 3D trajectory...")
    plot_3d_path(positions, title=f"Satellite {prn} 3D Path")


if __name__ == "__main__":
    main()
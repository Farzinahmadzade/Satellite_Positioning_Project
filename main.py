"""
main.py

Description:
Main script to run the complete satellite positioning pipeline.
It reads RINEX navigation and observation data, computes satellite positions
over specified time intervals, saves results to CSV, and plots 3D satellite paths.

Author: F.Ahmadzade
"""

import os
import pandas as pd
from read_rinex import read_rinex, get_observation_summary
from get_time_range import get_time_range
from generate_times import generate_times
from interpolate_orbital_params import interpolate_orbital_params
from compute_satellite_position import compute_satellite_position
from save_to_csv import save_to_csv
from plot_3d_path import plot_3d_path

def main():
    rinex_file = r"K:\GitHub\Satellite_Positioning_Project\Data\GODS00USA_R_20240010000_01D_GN.rnx"
    prn = 'G05'  # Target satellite PRN to process
    
    if not os.path.exists(rinex_file):
        print(f"RINEX file not found at {rinex_file}")
        return
    
    print("Reading RINEX observation data...")
    sat_dict = read_rinex(rinex_file, systems='G', verbose=True)

    # Print columns of each satellite for inspection
    for sat, df in sat_dict.items():
        print(f"Satellite {sat} columns: {list(df.columns)}")

    print("Generating observation summary:")
    summary = get_observation_summary(sat_dict)
    print(summary.to_string(index=False))
    
    print(f"Extracting time range for satellite {prn}...")
    start_time, end_time = get_time_range(sat_dict, prn)
    print(f"Start time: {start_time}, End time: {end_time}")
    
    print("Generating sampling times...")
    times = generate_times(start_time, end_time, interval_sec=30)
    
    print("Preparing navigation data DataFrame for interpolation...")
    nav_df = sat_dict[prn].set_index('time')
    
    print("Interpolating orbital parameters...")
    orbital_params = interpolate_orbital_params(nav_df, times)
    
    print("Computing satellite ECEF positions...")
    positions = compute_satellite_position(orbital_params)
    
    output_csv = "output_satellite_positions.csv"
    print(f"Saving positions to CSV: {output_csv}...")
    save_to_csv(positions, output_csv, timestamps=pd.Series(times))
    
    print("Plotting 3D satellite path...")
    plot_3d_path(positions, title=f"Satellite {prn} 3D Path")

if __name__ == "__main__":
    main()
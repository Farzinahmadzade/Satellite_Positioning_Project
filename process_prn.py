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
import warnings
import matplotlib.pyplot as plt

from datetime import timedelta
from typing import Dict, Optional
from read_navigation import read_navigation_file, get_ephemeris
from generate_times import generate_times
from compute_satellite_position import compute_satellite_position
from mpl_toolkits.mplot3d import Axes3D

def process_prn(nav_filepath: str, prn: str, obs_time: Optional[pd.Timestamp] = None, 
                interval_sec: int = 30, save_csv: bool = True, show_plot: bool = True) -> pd.DataFrame:
    
    # 1. Read navigation file
    nav_data = read_navigation_file(nav_filepath, systems=prn[0])
    if len(nav_data.time) == 0:
        raise ValueError(f"No navigation data found in {nav_filepath}")
    
    # 2. Determination of observation time
    if obs_time is None:
        times = pd.to_datetime(nav_data.time.values)
        obs_time = times[len(times) // 2]
    
    # 3. Extraction of all satellite ephemeris
    try:
        sat_nav = nav_data.sel(sv=prn)
    except KeyError:
        raise ValueError(f"PRN {prn} not found in navigation data")
    
    eph_times = pd.to_datetime(sat_nav.time.values)
    if len(eph_times) == 0:
        raise ValueError(f"No ephemeris for {prn}")
    
    # 4. Choosing suitable ephemeris (±6 hours from obs_time)
    time_window = timedelta(hours=6)
    valid_eph = []
    for eph_time in eph_times:
        if abs((eph_time - obs_time).total_seconds()) <= time_window.total_seconds():
            eph = get_ephemeris(nav_data, prn, eph_time)
            if eph:
                valid_eph.append({**eph, 'eph_time': eph_time})
    
    if not valid_eph:
        raise ValueError(f"No valid ephemeris for {prn} within ±6h of {obs_time}")
    
    print(f"Found {len(valid_eph)} ephemeris sets for {prn}")
    
    # 5. Generate times for 24 hours
    start_time = min(e.time for e in valid_eph)
    end_time = start_time + timedelta(days=1)
    times = generate_times(start_time, end_time, interval_sec)
    
    # 6. Multiple ephemeris interpolation (nearest neighbor + linear blending)
    orbital_params = interpolate_multiple_eph(valid_eph, times)
    
    # 7. Calculate tk relative to each epoch ephemeris
    tk_seconds = np.zeros(len(times))
    for i, t in enumerate(times):
        closest_eph_time = min(valid_eph, key=lambda e: abs((e['eph_time'] - t).total_seconds()))
        tk_seconds[i] = (t - closest_eph_time['eph_time']).total_seconds()
    
    orbital_params['tk'] = tk_seconds
    orbital_params['tk'] = np.clip(orbital_params['tk'], -7200, 7200)  # ±2 hours max
    
    # 8. Calculation of positions
    positions = compute_satellite_position(orbital_params)
    
    # 9. Validation checks
    validate_positions(positions, prn)
    
    # 10. Output DataFrame
    df_out = pd.DataFrame({
        'time': times,
        'x_ecef': positions['X'],
        'y_ecef': positions['Y'], 
        'z_ecef': positions['Z'],
        'radius': positions.get('r', np.linalg.norm(np.stack([positions['X'], positions['Y'], positions['Z']]), axis=0))
    })
    
    # 11. Save CSV
    if save_csv:
        filename = f"trajectory_{prn}_{obs_time.strftime('%Y%m%d_%H%M')}.csv"
        df_out.to_csv(filename, index=False)
        print(f"✓ Saved: {filename}")
    
    # 12. 3D Plot
    if show_plot:
        plot_trajectory_3d(df_out, prn)
    
    return df_out

def interpolate_multiple_eph(ephemerides: list, times: list) -> Dict[str, np.ndarray]:
    """Interpolation با blending چندین ephemeris"""
    params = ['sqrtA', 'e', 'i0', 'omega', 'OMEGA', 'M0', 'delta_n', 'OMEGA_DOT', 'IDOT',
              'Cuc', 'Cus', 'Crc', 'Crs', 'Cic', 'Cis']
    
    interpolated = {p: np.zeros(len(times)) for p in params}
    
    for i, t in enumerate(times):
        weights = []
        values = []
        for eph in ephemerides:
            dt = abs((eph['eph_time'] - t).total_seconds())
            if dt <= 7200:  # 2 hours
                weight = 1.0 / (1.0 + (dt / 3600.0)**2)
                weights.append(weight)
                for param in params:
                    values.append(eph.get(param, 0.0))
        
        if weights:
            total_weight = sum(weights)
            for j, param in enumerate(params):
                interpolated[param][i] = sum(w * values[j] for w, v in zip(weights, values)) / total_weight
    
    return interpolated

def validate_positions(positions: Dict, prn: str):
    """Validation of results"""
    X, Y, Z = positions['X'], positions['Y'], positions['Z']
    radius = np.sqrt(X**2 + Y**2 + Z**2)
    
    stats = {
        'mean_radius_km': np.mean(radius)/1000,
        'radius_std_km': np.std(radius)/1000,
        'min_alt_km': np.min(radius)/1000,
        'max_alt_km': np.max(radius)/1000
    }
    
    print(f"Validation {prn}: R={stats['mean_radius_km']:.1f}±{stats['radius_std_km']:.1f}km")
    
    if not (25000 < stats['mean_radius_km'] < 27000):
        warnings.warn("⚠️  Radius out of GPS range (25-27k km)")
    
    if stats['radius_std_km'] > 50:
        warnings.warn("⚠️  High radius variation - check ephemeris quality")

def plot_trajectory_3d(df: pd.DataFrame, prn: str):
    """Draw a 3D trajectory"""
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')
    
    ax.plot(df['x_ecef']/1000, df['y_ecef']/1000, df['z_ecef']/1000, 
            'b-', linewidth=2, label=f'{prn} trajectory')
    ax.scatter(df['x_ecef'].iloc[0]/1000, df['y_ecef'].iloc[0]/1000, df['z_ecef'].iloc[0]/1000, 
              c='green', s=100, label='Start')
    ax.scatter(df['x_ecef'].iloc[-1]/1000, df['y_ecef'].iloc[-1]/1000, df['z_ecef'].iloc[-1]/1000, 
              c='red', s=100, label='End')
    
    # Earth reference
    u = np.linspace(0, 2*np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    x_earth = 6371 * np.outer(np.cos(u), np.sin(v))
    y_earth = 6371 * np.outer(np.sin(u), np.sin(v))
    z_earth = 6371 * np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x_earth, y_earth, z_earth, alpha=0.3, color='lightblue')
    
    ax.set_xlabel('X (km)')
    ax.set_ylabel('Y (km)')
    ax.set_zlabel('Z (km)')
    ax.legend()
    ax.set_title(f'GNSS Satellite {prn} - 24hr ECEF Trajectory')
    plt.tight_layout()
    plt.show()
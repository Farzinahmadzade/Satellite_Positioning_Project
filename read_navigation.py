"""
RINEX Navigation File Parser 
--------------------------------------------
Reads GPS/GLONASS/Galileo navigation files and extracts ephemeris data
Supports RINEX 2.x, 3.x, 4.x formats

Author: F.Ahmadzade
"""

import georinex as gr
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import numpy as np
import os


# Mapping of possible field names (georinex versions may differ)
FIELD_MAPPING = {
    'toe': ['Toe', 'toe', 'TimeEph'],
    'toc': ['Toc', 'toc', 'TransTime'],
    'M0': ['M0', 'MeanAnomaly'],
    'sqrtA': ['sqrtA', 'sqrtSemiMajorAxis'],
    'e': ['Eccentricity', 'e', 'ecc'],
    'omega': ['omega', 'Omega', 'ArgPerigee'],
    'Omega0': ['Omega0', 'OMEGA0', 'LongAscNode'],
    'i0': ['Io', 'i0', 'Inclination'],
    'DeltaN': ['DeltaN', 'deltaN', 'MeanMotionDifference'],
    'OmegaDot': ['OmegaDot', 'OMEGADOT', 'RateRightAscension'],
    'IDOT': ['IDOT', 'Idot', 'InclinationRate'],
    'Crs': ['Crs', 'CRS'],
    'Crc': ['Crc', 'CRC'],
    'Cus': ['Cus', 'CUS'],
    'Cuc': ['Cuc', 'CUC'],
    'Cis': ['Cis', 'CIS'],
    'Cic': ['Cic', 'CIC'],
    'SVclockBias': ['SVclockBias', 'af0', 'ClockBias'],
    'SVclockDrift': ['SVclockDrift', 'af1', 'ClockDrift'],
    'SVclockDriftRate': ['SVclockDriftRate', 'af2', 'ClockDriftRate'],
    'TGD': ['TGD', 'Tgd', 'GroupDelayDiff'],
    'IODE': ['IODE', 'Iode'],
    'IODC': ['IODC', 'Iodc'],
}


def to_float(val) -> Optional[float]:
    """
    Convert xarray value to float, handling different data types.
    
    Args:
        val: xarray value (DataArray, numpy array, scalar, etc.)
    
    Returns:
        Float value or None if conversion fails
    """
    try:
        # Extract the actual value
        if hasattr(val, 'values'):
            v = val.values
            if hasattr(v, 'item'):
                v = v.item()
        else:
            v = val
        
        # Convert to float
        if isinstance(v, (str, bytes)):
            v = float(v)
        elif isinstance(v, (int, float, np.number)):
            v = float(v)
        else:
            return None
        
        # Check for NaN or inf
        if np.isnan(v) or np.isinf(v):
            return None
            
        return v
    except (ValueError, TypeError, AttributeError):
        return None


def get_field_value(eph_data, field_name: str) -> Optional[float]:
    """
    Get field value from ephemeris data with fallback names.
    
    Args:
        eph_data: xarray Dataset with ephemeris
        field_name: Standard field name
    
    Returns:
        Float value or None
    """
    possible_names = FIELD_MAPPING.get(field_name, [field_name])
    
    for name in possible_names:
        try:
            if name in eph_data:
                return to_float(eph_data[name])
        except:
            continue
    
    return None


def read_navigation_file(nav_file_path: str, 
                         systems: Optional[str] = None) -> Dict:
    """
    Read RINEX navigation file and extract ephemeris.
    
    Args:
        nav_file_path: Path to RINEX navigation file (.21n, .nav, .rnx, etc.)
        systems: Satellite systems to load ('G', 'R', 'E', 'GRE', etc.)
                 None = all systems
    
    Returns:
        xarray Dataset with navigation data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file cannot be loaded
    """
    if not os.path.exists(nav_file_path):
        raise FileNotFoundError(f"Navigation file not found: {nav_file_path}")
    
    print(f"{'='*70}")
    print(f"Loading RINEX Navigation File")
    print(f"{'='*70}")
    print(f"File: {os.path.basename(nav_file_path)}")
    
    try:
        # Load navigation file using georinex
        if systems:
            nav = gr.load(nav_file_path, use=systems)
        else:
            nav = gr.load(nav_file_path)
        
        satellites = nav.sv.values if hasattr(nav, 'sv') else []
        time_range = nav.time.values if hasattr(nav, 'time') else []
        
        print(f"✓ Navigation data loaded")
        print(f"  Satellites: {len(satellites)}")
        print(f"  Systems: {set([s[0] for s in satellites])}")
        
        if len(time_range) > 0:
            print(f"  Time range: {pd.Timestamp(time_range[0])} to {pd.Timestamp(time_range[-1])}")
        
        # Print available fields (useful for debugging)
        fields = list(nav.data_vars)
        print(f"  Available fields: {len(fields)}")
        
        print(f"{'='*70}\n")
        
        return nav
        
    except Exception as e:
        raise ValueError(f"Failed to load navigation file: {e}")


def get_ephemeris(nav_data, 
                  sat_id: str, 
                  obs_time: pd.Timestamp,
                  max_age_hours: float = 4.0,
                  verbose: bool = False) -> Optional[Dict]:
    """
    Get ephemeris for a specific satellite at a given time.
    
    Args:
        nav_data: Navigation data from georinex
        sat_id: Satellite ID (e.g., 'G01', 'R01')
        obs_time: Observation time (pandas Timestamp)
        max_age_hours: Maximum age of ephemeris in hours (default 4.0)
        verbose: Print detailed information
    
    Returns:
        Dictionary with ephemeris parameters or None if failed
    """
    try:
        # Check if satellite exists
        if sat_id not in nav_data.sv.values:
            if verbose:
                print(f"  Warning: {sat_id} not in navigation data")
            return None
        
        # Select satellite
        sat_nav = nav_data.sel(sv=sat_id)
        
        # Find closest ephemeris in time
        eph_data = sat_nav.sel(time=obs_time, method='nearest')
        
        # Get ephemeris time
        eph_time_raw = eph_data['time'].values
        eph_time = pd.Timestamp(eph_time_raw)
        
        # Check ephemeris age
        age_seconds = abs((obs_time - eph_time).total_seconds())
        age_hours = age_seconds / 3600.0
        
        if age_hours > max_age_hours:
            if verbose:
                print(f"  Warning: {sat_id} ephemeris too old ({age_hours:.1f} hours)")
            # Still return it, but user should be aware
        
        # Extract satellite system
        sat_system = sat_id[0] if len(sat_id) > 0 else 'G'
        
        # Build ephemeris dictionary
        ephemeris = {
            'sat_id': sat_id,
            'system': sat_system,
            'eph_time': eph_time,
            'obs_time': obs_time,
            'age_hours': age_hours,
        }
        
        if sat_system == 'G':
            # GPS ephemeris parameters
            params = [
                'toe', 'toc', 'M0', 'sqrtA', 'e', 'omega', 'Omega0', 'i0',
                'DeltaN', 'OmegaDot', 'IDOT',
                'Crs', 'Crc', 'Cus', 'Cuc', 'Cis', 'Cic',
                'SVclockBias', 'SVclockDrift', 'SVclockDriftRate',
                'TGD', 'IODE', 'IODC'
            ]
            
            for param in params:
                value = get_field_value(eph_data, param)
                ephemeris[param] = value
            
            # Check if critical parameters are available
            critical = ['toe', 'M0', 'sqrtA', 'e', 'omega', 'Omega0', 'i0']
            missing = [p for p in critical if ephemeris.get(p) is None]
            
            if missing:
                if verbose:
                    print(f"  Warning: {sat_id} missing critical parameters: {missing}")
                return None
            
            # If toc not available, use toe
            if ephemeris['toc'] is None:
                ephemeris['toc'] = ephemeris['toe']
            
            return ephemeris
        
        elif sat_system == 'R':
            # GLONASS ephemeris (different format - not implemented yet)
            if verbose:
                print(f"  Warning: GLONASS ephemeris not implemented yet")
            return None
        
        else:
            # Other systems not implemented
            if verbose:
                print(f"  Warning: System {sat_system} not implemented yet")
            return None
        
    except KeyError:
        if verbose:
            print(f"  Warning: {sat_id} not found in navigation data")
        return None
    except Exception as e:
        if verbose:
            print(f"  Warning: Error getting ephemeris for {sat_id}: {e}")
        return None


def get_ephemeris_batch(nav_data,
                        sat_list: List[str],
                        obs_time: pd.Timestamp,
                        max_age_hours: float = 4.0) -> Dict[str, Dict]:
    """
    Get ephemeris for multiple satellites at once.
    
    Args:
        nav_data: Navigation data from georinex
        sat_list: List of satellite IDs
        obs_time: Observation time
        max_age_hours: Maximum ephemeris age
    
    Returns:
        Dict[sat_id → ephemeris_dict]
    """
    eph_dict = {}
    
    for sat_id in sat_list:
        eph = get_ephemeris(nav_data, sat_id, obs_time, max_age_hours, verbose=False)
        if eph is not None:
            eph_dict[sat_id] = eph
    
    return eph_dict


def print_ephemeris_summary(eph_dict: Dict[str, Dict]):
    """
    Print summary of loaded ephemeris.
    
    Args:
        eph_dict: Dictionary of ephemeris data
    """
    print(f"{'='*70}")
    print("Ephemeris Summary")
    print(f"{'='*70}")
    
    summary = []
    for sat_id, eph in eph_dict.items():
        summary.append({
            'Satellite': sat_id,
            'System': eph['system'],
            'Eph Time': eph['eph_time'].strftime('%Y-%m-%d %H:%M:%S'),
            'Age (h)': f"{eph['age_hours']:.2f}",
            'sqrtA': f"{eph['sqrtA']:.3f}" if eph['sqrtA'] else 'N/A',
            'e': f"{eph['e']:.6f}" if eph['e'] else 'N/A',
        })
    
    if summary:
        df = pd.DataFrame(summary)
        print(df.to_string(index=False))
    else:
        print("No ephemeris data available")
    
    print(f"{'='*70}\n")


if __name__ == "__main__":
    # Test with your navigation file
    nav_file = "../Data/brdc2580.21n"
    
    if os.path.exists(nav_file):
        print("Testing Navigation File Reader")
        print("="*70)
        
        # Load navigation data
        nav_data = read_navigation_file(nav_file, systems='G')
        
        # Test getting ephemeris for a specific satellite and time
        test_sat = 'G01'
        test_time = pd.Timestamp('2021-09-15 12:00:00')
        
        print(f"\nTesting ephemeris extraction for {test_sat} at {test_time}")
        eph = get_ephemeris(nav_data, test_sat, test_time, verbose=True)
        
        if eph:
            print(f"\n✓ Ephemeris extracted successfully:")
            for key, value in list(eph.items())[:10]:
                print(f"  {key}: {value}")
        else:
            print(f"\n✗ Failed to extract ephemeris")
        
        # Test batch extraction
        print(f"\n{'='*70}")
        print("Testing batch extraction")
        sat_list = ['G01', 'G03', 'G06', 'G09']
        eph_batch = get_ephemeris_batch(nav_data, sat_list, test_time)
        print_ephemeris_summary(eph_batch)
        
    else:
        print(f"Test file not found: {nav_file}")
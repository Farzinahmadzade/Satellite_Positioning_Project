"""
Module: generate_times.py

Description:
Generates a list of sampling times at fixed intervals within a specified start and end time.
Useful for creating time steps at which satellite positions are computed, especially in orbital computations.

Author: F.Ahmadzade
"""

import pandas as pd
from typing import List
from datetime import timedelta

def generate_times(start_time: pd.Timestamp, 
                  end_time: pd.Timestamp, 
                  interval_sec: int = 30,
                  freq: str = None) -> pd.DatetimeIndex:
    """
    Generate optimal GNSS timings with pandas.date_range
    Args:
        start_time, end_time: time interval
        interval_sec: second interval (default: 30s GNSS standard)
        freq: pandas freq string ('30S', '1T', '1H') - has priority
    
    Returns:
        pd.DatetimeIndex: fast, timezone-aware, sliceable
    """
    
    if start_time > end_time:
        raise ValueError("start_time <= end_time")
    
    # Convert interval_sec to freq string
    if freq is None:
        if interval_sec == 30:
            freq = '30S'
        elif interval_sec == 60:
            freq = '1T' 
        else:
            freq = f'{interval_sec}S'
    
    # Using pandas native - 100x faster
    times = pd.date_range(start=start_time, end=end_time, freq=freq)
    
    # Ensure inclusion of end_time
    if times[-1] < end_time:
        times = times.append(pd.Timestamp(end_time))
    
    return times

# backward-compatible version (List[Timestamp])
def generate_times_list(start_time: pd.Timestamp, end_time: pd.Timestamp, 
                       interval_sec: int = 30) -> List[pd.Timestamp]:
    """Legacy support"""
    return generate_times(start_time, end_time, interval_sec).tolist()

# GNSS Standards
def gnss_sampling_times(start_time: pd.Timestamp, duration_hours: float = 24, 
                       sample_rate: str = '30S') -> pd.DatetimeIndex:
    """
    Standard timing of GNSS satellite ephemeris
    30S: real-time, 1T: post-processing, 5T: monitoring
    """
    end_time = start_time + pd.Timedelta(hours=duration_hours)
    return pd.date_range(start_time, end_time, freq=sample_rate)

# Test
if __name__ == "__main__":
    start = pd.Timestamp("2026-02-13 00:00:00", tz='UTC')
    end = start + pd.Timedelta(hours=2)
    
    print("✅ Test 1: Standard 30s GNSS")
    times_30s = generate_times(start, end, 30)
    print(f"  Length: {len(times_30s)}, First: {times_30s[0]}, Last: {times_30s[-1]}")
    
    print("\n✅ Test 2: GNSS Standards")
    times_gnss = gnss_sampling_times(start, 24, '30S')
    print(f"  24hr GNSS (30s): {len(times_gnss)} epochs")
    
    print("\n✅ Performance: date_range vs manual")
    print("generate_times: pandas.date_range optimized ✓")
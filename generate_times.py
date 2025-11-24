"""
Module: generate_times.py

Description:
Generates a list of sampling times at fixed intervals within a given start and end time.
Useful for creating time steps at which satellite positions are computed.

Author: Your Name
"""

from typing import List
import pandas as pd

def generate_times(start_time: pd.Timestamp, end_time: pd.Timestamp, interval_sec: int = 30) -> List[pd.Timestamp]:
    """
    Generate a list of timestamps starting from start_time to end_time with fixed interval steps.

    Args:
        start_time (pd.Timestamp): The start time of the interval.
        end_time (pd.Timestamp): The end time of the interval.
        interval_sec (int): Time step interval in seconds (default 30).

    Returns:
        List[pd.Timestamp]: List of timestamps separated by interval_sec.
    """
    if start_time > end_time:
        raise ValueError("start_time must be less than or equal to end_time")

    times = []
    current = start_time
    while current <= end_time:
        times.append(current)
        current += pd.Timedelta(seconds=interval_sec)
    return times
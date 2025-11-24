"""
Module: save_to_csv.py

Description:
Saves satellite position data (e.g., ECEF coordinates) into a CSV file.

Author: F.Ahmadzade
"""

import pandas as pd
from typing import Dict

def save_to_csv(position_data: Dict[str, any], 
                filename: str, 
                timestamps: pd.Series = None) -> None:
    """
    Save satellite position data into a CSV file.

    Args:
        position_data (Dict[str, any]): Dictionary containing position arrays or lists with keys like 'X', 'Y', 'Z'.
        filename (str): Path to the output CSV file.
        timestamps (pd.Series, optional): Corresponding timestamps for the position data. If provided, will be saved as a column.

    Returns:
        None
    """
    df = pd.DataFrame(position_data)

    if timestamps is not None:
        df.insert(0, 'time', timestamps)

    df.to_csv(filename, index=False)
    print(f"Position data saved to {filename}")

if __name__ == "__main__":
    # Example usage
    import numpy as np
    import pandas as pd
    
    # Create dummy data
    positions = {
        'X': np.linspace(0, 10000, 10),
        'Y': np.linspace(0, 5000, 10),
        'Z': np.linspace(1000, 15000, 10)
    }
    times = pd.date_range(start='2025-11-24 00:00:00', periods=10, freq='30S')
    
    save_to_csv(positions, 'satellite_positions.csv', times)
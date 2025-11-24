"""
Module: plot_3d_path.py

Description:
Visualizes satellite trajectory as a 3D plot using computed ECEF coordinates.

Author: F.Ahmadzade
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import; necessary for 3D projection
from typing import Dict

def plot_3d_path(position_data: Dict[str, any], title: str = "Satellite 3D Path") -> None:
    """
    Plot the 3D satellite trajectory.

    Args:
        position_data (Dict[str, any]): Dictionary with keys 'X', 'Y', 'Z' containing position arrays or lists.
        title (str): Title of the plot.

    Returns:
        None
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    X = position_data.get('X')
    Y = position_data.get('Y')
    Z = position_data.get('Z')

    ax.plot(X, Y, Z, marker='o', linestyle='-', color='b', label='Satellite Path')
    ax.set_xlabel('X (meters)')
    ax.set_ylabel('Y (meters)')
    ax.set_zlabel('Z (meters)')
    ax.set_title(title)
    ax.legend()
    plt.show()

if __name__ == "__main__":
    # Example usage
    import numpy as np
    
    pos_data = {
        'X': np.linspace(0, 10000, 100),
        'Y': np.sin(np.linspace(0, 10, 100)) * 10000,
        'Z': np.cos(np.linspace(0, 10, 100)) * 10000
    }
    plot_3d_path(pos_data, "Example Satellite Orbit Path")
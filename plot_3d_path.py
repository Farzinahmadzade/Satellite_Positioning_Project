"""
Module: plot_3d_path.py

Description:
Visualizes satellite trajectory as a 3D plot using computed ECEF coordinates.

Author: F.Ahmadzade
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, Any

def plot_3d_path(position_data: Dict[str, Any], title: str = "GNSS Satellite 3D Trajectory", 
                units: str = 'km', show_earth: bool = True, figsize: tuple = (12, 10)) -> None:
    """
    3D drawing of standard GNSS trajectory with Earth reference
    
    Args:
        position_data: {'X', 'Y', 'Z', 'r'} arrays (meters)
        title: chart title
        units: 'm' or 'km'
        show_earth: show the earth
    """
    
    # Extract positions
    X, Y, Z = np.array(position_data['X']), np.array(position_data['Y']), np.array(position_data['Z'])
    
    # Scale to km
    scale = 1e-3 if units == 'km' else 1
    X, Y, Z = X * scale, Y * scale, Z * scale
    
    # Create figure
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection='3d')
    
    # 1. Satellite trajectory
    ax.plot(X, Y, Z, 'b-', linewidth=3, label='Satellite Orbit', alpha=0.9)
    
    # 2. Start/End points
    ax.scatter(X[0], Y[0], Z[0], c='green', s=200, marker='^', 
               label='Start', edgecolors='darkgreen', linewidth=2)
    ax.scatter(X[-1], Y[-1], Z[-1], c='red', s=200, marker='v', 
               label='End', edgecolors='darkred', linewidth=2)
    
    # 3. Earth (WGS84 ellipsoid)
    if show_earth:
        u = np.linspace(0, 2 * np.pi, 50)
        v = np.linspace(0, np.pi, 50)
        # WGS84 equatorial/polar radii
        a = 6378.137 * scale  # km
        b = 6356.752 * scale
        x_earth = a * np.outer(np.cos(u), np.sin(v))
        y_earth = a * np.outer(np.sin(u), np.sin(v))
        z_earth = b * np.outer(np.ones_like(u), np.cos(v))
        ax.plot_surface(x_earth, y_earth, z_earth, alpha=0.3, color='lightblue', 
                       rstride=4, cstride=4)
    
    # 4. ECEF Reference frame (XYZ axes)
    max_range = np.max(np.abs([X, Y, Z])) * 1.2
    ax.quiver(0, 0, 0, max_range, 0, 0, color='r', alpha=0.7, arrow_length_ratio=0.1)
    ax.quiver(0, 0, 0, 0, max_range, 0, color='g', alpha=0.7, arrow_length_ratio=0.1)
    ax.quiver(0, 0, 0, 0, 0, max_range, color='b', alpha=0.7, arrow_length_ratio=0.1)
    
    # 5. Labels و formatting
    ax.set_xlabel(f'X ECEF ({units})', fontsize=12)
    ax.set_ylabel(f'Y ECEF ({units})', fontsize=12)
    ax.set_zlabel(f'Z ECEF ({units})', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    # 6. Equal aspect ratio
    ax.set_box_aspect([1,1,1])
    
    # 7. Grid و legend
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', framealpha=0.9)
    
    # 8. Statistics
    r = np.sqrt(X**2 + Y**2 + Z**2)
    print(f"📊 Orbit stats: R={np.mean(r):.0f}±{np.std(r):.0f} {units}")
    print(f"   Range: {np.min(r):.0f} - {np.max(r):.0f} {units}")
    
    plt.tight_layout()
    plt.show()

# تست GNSS realistic
if __name__ == "__main__":
    # GPS orbit (~26500km)
    t = np.linspace(0, 24*3600, 2880)      # 30s sampling
    omega = 2 * np.pi / (23*3600 + 56*60)  # sidereal day
    
    pos_data = {
        'X': 26500e3 * np.cos(omega * t),
        'Y': 26500e3 * np.sin(omega * t), 
        'Z': np.zeros_like(t)
    }
    
    plot_3d_path(pos_data, "GPS Satellite 24hr Orbit (ECEF)", units='km')
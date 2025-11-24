# Satellite Positioning Project

This project implements a satellite positioning pipeline that processes RINEX navigation and observation files to calculate 3D satellite positions at specified time intervals. The resulting data is saved as CSV files and visualized through 3D path plots.

# Features
1. Supports RINEX observation files versions 2.x, 3.x, and 4.x
2. Computes satellite positions using orbital parameters in ECEF coordinate system
3. Performs time interpolation of navigation parameters for accuracy
4. Generates 3D plots of satellite trajectories
5. Modular and extendable structure for ease of maintenance

# Installation
Install required Python packages using:
```
pip install -r requirements.txt 
```

# Usage
Place your RINEX data files into the data/ directory

Run processing scripts from the src/ folder

Output files in CSV format will be generated alongside 3D visualizations

# Repository Structure
src/: Source code modules responsible for each stage of the pipeline

data/: Sample or actual RINEX files for processing

tests/: Unit tests to verify correctness and robustness

README.md: Project documentation and instructions

requirements.txt: Lists all Python dependencies


# Modules Overview
read_rinex.py: Reads and parses RINEX observation files reliably

get_time_range.py: Extracts the start and end times for satellite data

generate_times.py: Creates lists of sampling times at specified intervals

interpolate_orbital_params.py: Interpolates navigation parameters for given times

compute_satellite_position.py: Calculates satellite ECEF coordinates from orbital data

save_to_csv.py: Saves computed satellite position data to CSV files

plot_3d_path.py: Visualizes satellite trajectories with 3D plots

# Contribution
Everyone is welcome to contribute via pull requests or issue reports to improve the code, add features, or fix bugs.


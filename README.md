# Satellite Positioning Project

## Overview
This project computes and visualizes the 3D trajectory of GNSS satellites (specifically GPS) using open-source Python modules and RINEX data files. The main goal is to extract satellite ephemeris and observation data, interpolate navigation parameters, and calculate accurate ECEF (Earth-Centered, Earth-Fixed) positions at regular time intervals. Final results include a CSV of the computed path and a 3D visualization.

---

## Project Objective

- Fully parse RINEX navigation and observation files (multi-version and multi-GNSS support)
- Interpolate satellite orbital parameters at custom time intervals
- Compute GNSS satellite positions in the ECEF coordinate system
- Output trajectories to CSV and visualize 3D orbital paths
- Handle incomplete or missing input scenarios with data-recovery protocols

---

## Libraries Used

- **georinex**  
  Python library for reading and parsing RINEX navigation/observation files  
  [https://georinex.readthedocs.io](https://georinex.readthedocs.io)[web:15]
- **pandas**  
  DataFrame library for managing tabular and time-series satellite data  
  [https://pandas.pydata.org/docs/](https://pandas.pydata.org/docs/)[web:15]
- **numpy**  
  Efficient numerical arrays and mathematical operations  
  [https://numpy.org/](https://numpy.org/)[web:15]
- **matplotlib**  
  Powerful scientific visualization package (used for 3D plotting)  
  [https://matplotlib.org/](https://matplotlib.org/)[web:15]
- **scipy.interpolate**  
  Interpolation routines for mapping parameter arrays to desired epochs  
  [https://docs.scipy.org/doc/scipy/reference/interpolate.html](https://docs.scipy.org/doc/scipy/reference/interpolate.html)[web:15]

---

## Module Structure

| Module/File                       | Functionality Description                                                                                          |
|------------------------------------|------------------------------------------------------------------------------------------------------------------|
| `main.py`                         | Main orchestrator. Runs entire pipeline: loading data, interpolation, computation, saving & visualization         |
| `read_navigation.py`               | Reads RINEX navigation files, extracts ephemeris for required satellites, handles missing/legacy fields           |
| `read_rinex.py`                    | Reads RINEX observation files, validates available observation epochs for satellites, distinguishes GNSS systems  |
| `generate_times.py`                | Generates regular sampling epochs (e.g., every 30 seconds) within observation period                             |
| `get_time_range.py`                | Extracts start/end times for a given satellite's observation span                                                |
| `interpolate_orbital_params.py`    | Interpolates navigation (ephemeris) parameters to target time intervals using scipy routines                     |
| `compute_satellite_position.py`    | Implements ECEF position calculation via standard GNSS orbital mechanics                                          |
| `plot_3d_path.py`                  | Creates a 3D plot of computed path using matplotlib                                                              |
| `save_to_csv.py`                   | Saves computed positions, coordinates, and timestamps to a CSV file                                              |
| `constants.py`                     | Provides GNSS-related physical constants (frequencies, wavelengths, etc.)                                        |

---

## Step-by-Step Progress and Development Path

1. **Initial Step: Data Assessment**  
   - Project began with a single observation file, but calculations of orbital positions require navigation (ephemeris) data.
   - Solution: Downloaded a matching navigation file (`brdc2580.21n`) for the same GNSS satellite and day.

2. **Robust Data Parsing**  
   - Developed flexible parsers for both navigation and observation RINEX files.
   - Mapping structures, fallbacks, and data validation routines added to handle all RINEX versions and GNSS types.

3. **Module Design**  
   - Each logical operation was modularized (file parsing, time creation, interpolation, computation, saving, visualization).
   - Each module was documented for clarity and maintainability.

4. **Bug Fixes: Type and Completeness Issues**  
   - Repeatedly encountered NoneType, NaN, and type mismatch errors in parsed data.
   - Solution: Added aggressive data sanitization before any arithmetic or interpolation.
   - Edge cases (missing columns, incomplete ephemeris) were managed by defaults or controlled error messages.

5. **Synchronization & Interpolation**  
   - Automated extraction of observation epochs and generated an evenly-spaced time series for computations.
   - Orbital parameters were interpolated using `scipy.interpolate` to fill in missing or sparse navigation info.

6. **Final Position Computation & Output**  
   - Computed ECEF positions for the specified satellite at all epochs.
   - Output saved as CSV for further GIS/scientific analysis.
   - 3D path plot was rendered and visually verified to match the known GPS orbital patterns.

7. **Documentation and Testing**  
   - Ensured all code sections are in English, commented for clarity, and follow professional standards.
   - README was written to summarize technical decisions, workflow, and practical instructions for users.

---

## Usage Instructions

1. Place your RINEX navigation (`*.21n`) and observation (`*.21o`) files in the `Data/` directory.
2. Edit `main.py` to specify target satellite PRN and data file paths.
3. Install required Python libraries (see above).
4. Run using `python main.py`.
5. Results are saved to `output_satellite_positions.csv` and visualized as a 3D plot.
6. If you lack a navigation file, download a matching one for your time/satellite from public GNSS repositories before running.

---

## Example Output

- **CSV File**: Columns include timestamp, X, Y, Z (ECEF coordinates)
- **3D Plot**: Shows the satellite’s orbital path around the Earth (see `/screenshots/` for examples)

---

## References & Resources

- georinex documentation: [https://georinex.readthedocs.io](https://georinex.readthedocs.io)[web:15]
- GNSS, GPS, and RINEX documentation  
- Matplotlib & pandas documentation  
- سامانه‌های تعیین موقعیت ماهواره‌ای در مهندسی نقشه‌برداری [web:24]
- "معرفی و دانلود کتاب نقشه برداری به روش تعیین موقعیت ماهواره‌ای" [web:22]

---

## Author & Maintainer

- Author: F.Ahmadzade
- Contact: [your-email@example.com]

---

If you use or adapt this code, please refer to the original README. For bug reports or suggestions, open an issue or contact the maintainer directly.


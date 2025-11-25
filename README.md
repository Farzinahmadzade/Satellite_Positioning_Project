# Satellite Positioning Project﻿

## Overview﻿

This project computes and visualizes the three-dimensional trajectory of GNSS satellites (focusing on GPS) using RINEX navigation and observation files with a robust Python workflow. The pipeline extracts and sanitizes satellite ephemeris and observation data, interpolates navigation parameters, calculates ECEF positions at regular intervals, and outputs both tabular and visual results. The implementation is meant to serve academic research, engineering analysis, and as a model pipeline for satellite orbit processing.﻿

---﻿

## Project Objectives﻿

- Robust parsing of RINEX navigation/observation files (supports RINEX 2/3/4 and multiple GNSS constellations)﻿
- Interpolate orbital parameters and compute ECEF (Earth-Centered, Earth-Fixed) satellite positions at custom time steps﻿
- Produce analyzable CSV output and interactive 3D orbit visualization﻿
- Handle incomplete dataset scenarios (including navigation file download and data recovery)﻿
- Enforce professional code hygiene, modular structure, and reproducible scientific results﻿

---﻿

## Used Libraries and Packages﻿

[- georinex: Parsing and processing RINEX navigation/observation files (readthedocs﻿(https://georinex.readthedocs.io/))]
[- pandas: Data management, manipulation, and time-series handling (docs﻿(https://pandas.pydata.org/docs/))]
[- numpy: Efficient matrix operations and math functions (docs﻿(https://numpy.org/))]
[- matplotlib: Visualization, including 3D plotting of computed satellite paths (docs﻿(https://matplotlib.org/))]
[- scipy.interpolate: Advanced interpolation (linear, spline) for parameter mapping and data continuity (docs﻿(https://docs.scipy.org/doc/scipy/reference/interpolate.html))]

---﻿

## Module Structure and Functionality﻿

| Module/File                   | Description                                                                                                                              |﻿
|-------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|﻿
| main.py                     | Pipeline orchestrator: runs loading, interpolation, computation, saving, visualization                                                          |﻿
| read_navigation.py          | Reads navigation file; extracts, cleans and validates satellite ephemeris parameters                                                               |﻿
| read_rinex.py               | Reads the observation file, validates completeness/gaps for satellites, RINEX version compatibility                                                    |﻿
| generate_times.py           | Creates fixed-interval time sequence for sampling observations                                                                                    |﻿
| get_time_range.py           | Extracts the observation time window for the target satellite                                                                                      |﻿
| interpolate_orbital_params.py| Interpolates ephemeris parameters for target epochs using scipy routines                                                                            |﻿
| compute_satellite_position.py| Calculates ECEF positions for the satellite using orbital mechanics                                                                                 |﻿
| plot_3d_path.py             | Produces 3D visualization of the computed trajectory                                                                                              |﻿
| save_to_csv.py              | Exports results (X, Y, Z, time) to CSV for GIS/scientific analysis                                                                               |﻿
| constants.py                | GNSS constants (frequencies, wavelengths, coefficients), multi-system support                                                                      |﻿
| process_prn.py              | Main pipeline function: given a navigation file and PRN, extracts closest ephemeris, generates sample times, interpolates parameters, computes and outputs ECEF satellite trajectory, with options to save CSV and plot |﻿

---﻿

## Project Progression (Development Roadmap)﻿

1. Initial Assessment﻿
   - Started with an observation file only. Ephemeris data was found essential for orbit reconstruction, so a navigation file (brdc2580.21n) was manually downloaded.﻿
2. Flexible Parser Design﻿
   - Wrote modular parsers for RINEX navigation/observation, covering edge cases like missing values and version inconsistencies.﻿
3. Type Safety & Data Cleaning﻿
   - Repeated refactoring to sanitize incoming data (handling None, NaN, float/string conversion), ensuring bug-free downstream computations.﻿
   - Added checks/gaps, fallback logic for incomplete field availability.﻿
4. Pipeline Integration﻿
   - Linked navigation/observation for common satellites, generated sample time intervals, and parameter interpolation routines.﻿
5. Output & Validation﻿
   - ECEF positions computed, results verified, output in science-ready CSV format and visualized as a 3D plot.﻿
6. Addition of process_prn.py﻿
   - Implemented process_prn.py as a main user-facing pipeline function that automates ephemeris extraction, time sampling, interpolation, ECEF computation, CSV output, and 3D plotting for selected satellites.﻿
7. Documentation﻿
   - Codebase fully documented in English, with professional comments and clean design.﻿
   - README updated with detailed workflow, module breakdowns, usage instructions including the new process_prn.py function.﻿

---﻿

## Usage Instructions﻿

1. Place your RINEX navigation (*.21n) and observation (*.21o) files in the Data/ directory.﻿
2. Specify PRN and data file paths in main.py or call process_prn.py directly.﻿
3. Install Python dependencies listed above (pip install georinex pandas numpy matplotlib scipy).﻿
4. Run python main.py for full pipeline or import and call process_prn.process_prn() for single satellite processing.﻿
5. Results are saved to output_satellite_positions.csv (or output_{PRN}.csv if called via process_prn) and visualized as a 3D orbit plot.﻿
6. If navigation file is missing, download the appropriate file for your epoch/system from a public GNSS database.﻿

---﻿

## Example Outputs﻿

- Output CSV: Columns for time and (X, Y, Z) ECEF coordinates﻿
- 3D Plot: Visualizes the computed satellite orbit (see /screenshots/ for references)﻿

---﻿

## References & Further Reading﻿

[- georinex documentation: https://georinex.readthedocs.io﻿(https://georinex.readthedocs.io/)]
- RINEX, GNSS, GPS format documentation and standards﻿
[- Matplotlib﻿(https://matplotlib.org/) | Pandas | Numpy | Scipy Interpolation]
- "جزوه تعیین موقعیت پیشرفته" (Advanced Positioning Course), دکتر سعید فرزانه، دانشگاه تهران﻿
- "سامانه‌های تعیین موقعیت ماهواره‌ای در مهندسی نقشه‌برداری"﻿
- "معرفی و دانلود کتاب نقشه برداری به روش تعیین موقعیت ماهواره‌ای"، هوبرت جان لیکرکرک، ترجمه فارسی﻿
[- Cornell Data Services: Writing READMEs for Research Data﻿(https://data.research.cornell.edu/data-management/sharing/readme/)]
- GNSS fundamentals and practical knowledge — Raymand GNSS﻿
- Additional online technical documentation standards﻿

---﻿

## Author & Maintainer﻿

Author: F.Ahmadzade  
Contact: [farzinahmadzade@ut.ac.ir] | [farzinahmadzade909@gmail.com]

---﻿

If you use or adapt this project, please cite this README and referenced material. For questions, improvements or bugs, open an issue or contact the author directly.﻿
# Satellite Positioning Project

## Overview
This project computes and visualizes the three-dimensional trajectory of GNSS satellites (focusing on GPS) using RINEX navigation and observation files with a robust Python workflow. The pipeline extracts and sanitizes satellite ephemeris and observation data, interpolates navigation parameters, calculates ECEF positions at regular intervals, and outputs both tabular and visual results.

---

## Project Objectives

- Robust parsing of RINEX navigation/observation files (supports RINEX 2/3/4 and multiple GNSS constellations)
- Interpolates orbital parameters and computes ECEF satellite positions at custom time steps
- Produces analyzable CSV output and a 3D orbit visualization
- Handles incomplete dataset scenarios via documented data recovery for navigation files

---

## Used Libraries and Packages

- **georinex**: Parsing and processing RINEX navigation/observation files ([readthedocs](https://georinex.readthedocs.io))
- **pandas**: Data management and manipulation for tabular/temporal satellite data
- **numpy**: Efficient matrix and numerical calculations
- **scipy.interpolate**: Advanced interpolation for parameter mapping and smoothing
- **matplotlib**: Visualization, including 3D plotting of computed satellite paths

---

## Module Structure and Function

| Module/File                       | Description                                                                                       |
|------------------------------------|---------------------------------------------------------------------------------------------------|
| `main.py`                         | Controls pipeline, data flow, reporting, and visualization                                        |
| `read_navigation.py`               | Parses navigation file, extracts & validates satellite ephemeris parameters                       |
| `read_rinex.py`                    | Reads the observation file, validates epoch completeness, handles multiple GNSS systems           |
| `generate_times.py`                | Creates fixed-interval time sequence for sampling observations                                    |
| `get_time_range.py`                | Extracts observation timespan for the chosen satellite                                            |
| `interpolate_orbital_params.py`    | Interpolates navigation parameters for all sample epochs using scipy routines                     |
| `compute_satellite_position.py`    | Calculates positions in ECEF coordinates via GNSS orbital mechanics                              |
| `plot_3d_path.py`                  | Generates 3D visualization of the satellite’s computed trajectory                                |
| `save_to_csv.py`                   | Exports computed positions and timestamps to a CSV file                                           |
| `constants.py`                     | GNSS physical constants: carrier frequencies, wavelengths, and standard coefficients              |

---

## Project Progression

1. **Initial Assessment**
    - Started with just an observation file, realizing navigation/ephemeris data is essential for position computation.
    - Manual download of the matching navigation file (`brdc2580.21n`) solved the dataset completeness.
2. **Parser Development**
    - Built flexible modules handling edge-cases, RINEX version differences, and multi-system support.
    - Added mapping and fallbacks for parameter naming inconsistencies.
3. **Refinement and Debugging**
    - Addressed frequent issues with missing/invalid values, type mismatches (`NoneType`, NaN, float/string conversion).
    - Cleaned ephemeris data before computation to guarantee downstream reliability.
    - Incorporated error handling for gaps, incomplete satellites, and data sanitation.
4. **Pipeline Integration**
    - Linked navigation data with observation epochs for satellites present in both files.
    - Implemented sampled time generation and parameter interpolation.
5. **Computation and Output**
    - ECEF position calculations verified for correctness, output format made analysis-ready (CSV + 3D plot).
    - Path visualization matched expected GPS satellite trajectory.
6. **Documentation and Professionalization**
    - English documentation and comments throughout the codebase.
    - Comprehensive README drafted with all modules, rationales, references, and instructions.

---

## How To Use

1. Put navigation (`*.21n`) and observation (`*.21o`) files into your `Data/` directory.
2. Specify PRN and file paths in `main.py`.
3. Install dependencies as listed above.
4. Run using `python main.py`.
5. Results: output CSV file and interactive 3D orbit plot.
6. If navigation file is missing, download the file corresponding to your observation dates and GNSS system.

---

## Example Outputs

- **Output CSV**: Contains time and (X, Y, Z) ECEF coordinates
- **3D Plot**: Visualizes the computed satellite orbit

---

## References

- georinex documentation: [https://georinex.readthedocs.io](https://georinex.readthedocs.io)[web:15]
- GPS/GNSS/RINEX documentation and format specs
- Matplotlib, pandas, numpy official documentation
- جزوه تعیین موقعیت پیشرفته، دکتر سعید فرزانه (دانشگاه تهران)
- سامانه‌های تعیین موقعیت ماهواره‌ای در مهندسی نقشه‌برداری [web:24]
- "معرفی و دانلود کتاب نقشه برداری به روش تعیین موقعیت ماهواره‌ای" (هوبرت جان لیکرکرک - ترجمه فارسی) [web:22]
- See related reference templates for scientific README at [Cornell Data Services](https://data.research.cornell.edu/data-management/sharing/readme/) [web:15]
- GNSS physical principles — Raymand GNSS knowledge [web:29]

---

## Maintainer

Author: F.Ahmadzade  
Contact: [farzinahmadzade@ut.ac.ir]
         [farzinahmadzade909@gmail.com]
---

If you use or modify this project, please cite this README and referenced material. For improvements or bugs, open an issue or contact the author.


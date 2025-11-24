"""
RINEX Observation File Reader
--------------------------------------------------------
Works with RINEX 2.x, 3.x, 4.x
Handles missing data, multiple observation types, all GNSS systems

Author: F.Ahmadzade
"""
import os
from typing import Dict, Optional, List, Tuple
import pandas as pd
import numpy as np
try:
    import georinex as gr
except ImportError:
    raise ImportError("Please install georinex: pip install georinex")


# Comprehensive mapping: RINEX 3/4 → RINEX 2 standard
RINEX3_MAPPING = {
    # GPS L1 Phase
    'L1C': 'L1', 'L1S': 'L1', 'L1L': 'L1', 'L1X': 'L1',
    'L1P': 'L1', 'L1W': 'L1', 'L1Y': 'L1', 'L1M': 'L1',
    
    # GPS L2 Phase
    'L2C': 'L2', 'L2S': 'L2', 'L2L': 'L2', 'L2X': 'L2',
    'L2P': 'L2', 'L2W': 'L2', 'L2Y': 'L2', 'L2M': 'L2',
    
    # GPS L5 Phase
    'L5I': 'L5', 'L5Q': 'L5', 'L5X': 'L5',
    
    # GPS L1 Code
    'C1C': 'C1', 'C1S': 'C1', 'C1L': 'C1', 'C1X': 'C1',
    'C1P': 'C1', 'C1W': 'C1', 'C1Y': 'C1', 'C1M': 'C1',
    
    # GPS L2 Code
    'C2C': 'C2', 'C2S': 'C2', 'C2L': 'C2', 'C2X': 'C2',
    'C2P': 'C2', 'C2W': 'C2', 'C2Y': 'C2', 'C2M': 'C2',
    
    # GPS L5 Code
    'C5I': 'C5', 'C5Q': 'C5', 'C5X': 'C5',
    
    # GLONASS
    'L1C': 'L1', 'L1P': 'L1', 'L2C': 'L2', 'L2P': 'L2',
    'C1C': 'C1', 'C1P': 'C1', 'C2C': 'C2', 'C2P': 'C2',
    
    # Galileo
    'L1A': 'L1', 'L1B': 'L1', 'L1C': 'L1', 'L1X': 'L1', 'L1Z': 'L1',
    'L5I': 'L5', 'L5Q': 'L5', 'L5X': 'L5',
    'L7I': 'L7', 'L7Q': 'L7', 'L7X': 'L7',
    'L8I': 'L8', 'L8Q': 'L8', 'L8X': 'L8',
    'C1A': 'C1', 'C1B': 'C1', 'C1C': 'C1', 'C1X': 'C1', 'C1Z': 'C1',
    'C5I': 'C5', 'C5Q': 'C5', 'C5X': 'C5',
    'C7I': 'C7', 'C7Q': 'C7', 'C7X': 'C7',
    'C8I': 'C8', 'C8Q': 'C8', 'C8X': 'C8',
    
    # BeiDou
    'L2I': 'L2', 'L2Q': 'L2', 'L2X': 'L2',
    'L6I': 'L6', 'L6Q': 'L6', 'L6X': 'L6',
    'L7I': 'L7', 'L7Q': 'L7', 'L7X': 'L7',
    'C2I': 'C2', 'C2Q': 'C2', 'C2X': 'C2',
    'C6I': 'C6', 'C6Q': 'C6', 'C6X': 'C6',
    'C7I': 'C7', 'C7Q': 'C7', 'C7X': 'C7',
}

# Fallback: If P2 exists but not C2, map P2→C2
RINEX2_FALLBACK = {
    'P1': 'C1',
    'P2': 'C2',
}


def detect_rinex_version(obs_file: str) -> str:
    """
    Detect RINEX version from file header.
    
    Returns:
        Version string (e.g., '2.11', '3.04', '4.00')
    """
    try:
        with open(obs_file, 'r') as f:
            first_line = f.readline()
            # RINEX version is in columns 1-9
            version = first_line[0:9].strip()
            return version
    except:
        return 'Unknown'


def standardize_columns(df: pd.DataFrame, verbose: bool = False) -> pd.DataFrame:
    """
    Convert RINEX 3/4 column names to RINEX 2 standard names.
    Handles priority: prefer modern codes over legacy ones.
    
    Args:
        df: DataFrame with RINEX observations
        verbose: Print standardization details
    
    Returns:
        DataFrame with standardized column names
    """
    rename_dict = {}
    
    # First pass: RINEX 3/4 codes
    for col in df.columns:
        if col in RINEX3_MAPPING:
            standard_name = RINEX3_MAPPING[col]
            if standard_name not in df.columns:
                rename_dict[col] = standard_name
    
    # Second pass: RINEX 2 fallback (P1, P2)
    if 'C1' not in df.columns and 'C2' not in df.columns:
        for col in df.columns:
            if col in RINEX2_FALLBACK:
                standard_name = RINEX2_FALLBACK[col]
                if standard_name not in df.columns:
                    rename_dict[col] = standard_name
    
    if rename_dict:
        df = df.rename(columns=rename_dict)
        if verbose:
            print(f"   Standardized: {rename_dict}")
    
    return df


def add_time_gaps(df: pd.DataFrame, threshold_sec: float = 30.0) -> pd.DataFrame:
    """
    Add columns indicating time gaps and sampling interval.
    """
    df = df.copy()
    df['time_diff'] = df['time'].diff().dt.total_seconds()
    df['has_gap'] = df['time_diff'] > threshold_sec
    df.loc[0, 'has_gap'] = False  # First epoch has no gap
    
    # Estimate nominal sampling interval (most common time_diff)
    if len(df) > 1:
        time_diffs = df['time_diff'].dropna()
        if len(time_diffs) > 0:
            # Mode of time differences
            nominal_interval = time_diffs.mode().iloc[0] if len(time_diffs.mode()) > 0 else 30.0
            df.attrs['sampling_interval'] = nominal_interval
    
    return df


def validate_observation_pair(df: pd.DataFrame, sat_id: str) -> Tuple[bool, str]:
    """
    Validate that satellite has required observation pairs for combinations.
    
    Returns:
        (is_valid, message)
    """
    required_phase = ['L1', 'L2']
    required_code = ['C1', 'C2']
    
    has_phase = all(col in df.columns for col in required_phase)
    has_code = all(col in df.columns for col in required_code)
    
    if has_phase and has_code:
        # Check data completeness (at least 50% valid)
        l1_valid = df['L1'].notna().sum() / len(df)
        l2_valid = df['L2'].notna().sum() / len(df)
        c1_valid = df['C1'].notna().sum() / len(df)
        c2_valid = df['C2'].notna().sum() / len(df)
        
        if l1_valid < 0.5 or l2_valid < 0.5:
            return False, f"Low phase completeness (L1:{l1_valid:.1%}, L2:{l2_valid:.1%})"
        
        return True, "Valid"
    else:
        missing = []
        if not has_phase:
            missing_phase = [p for p in required_phase if p not in df.columns]
            missing.append(f"Phase: {missing_phase}")
        if not has_code:
            missing_code = [c for c in required_code if c not in df.columns]
            missing.append(f"Code: {missing_code}")
        
        return False, f"Missing observations - {', '.join(missing)}"


def read_rinex(obs_file: str, 
               systems: Optional[str] = None,
               min_epochs: int = 10,
               detect_gaps: bool = True,
               gap_threshold: float = 30.0,
               verbose: bool = True) -> Dict[str, pd.DataFrame]:
    """
    Read RINEX observation file (v2/v3/v4) - Robust for any RINEX file.
    
    Args:
        obs_file: Path to RINEX observation file
        systems: Satellite systems to load ('G', 'R', 'E', 'C', 'GRE', etc.)
                 None = all systems
        min_epochs: Minimum number of epochs required
        detect_gaps: Detect time gaps between epochs
        gap_threshold: Time gap threshold in seconds
        verbose: Print detailed information
    
    Returns:
        Dict[str, pd.DataFrame]: Satellite ID → DataFrame with observations
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If no valid satellites found
    """
    # 1. File existence check
    if not os.path.exists(obs_file):
        raise FileNotFoundError(f"RINEX file not found: {obs_file}")
    
    # 2. Detect RINEX version
    version = detect_rinex_version(obs_file)
    if verbose:
        print(f"{'='*70}")
        print(f"Loading RINEX file: {os.path.basename(obs_file)}")
        print(f"RINEX Version: {version}")
        print(f"{'='*70}")
    
    # 3. Load with georinex (handles all versions)
    try:
        if systems:
            obs = gr.load(obs_file, use=systems)
        else:
            obs = gr.load(obs_file)
    except Exception as e:
        raise ValueError(f"Failed to load RINEX: {e}")
    
    # 4. Extract satellites
    satellites = obs.sv.values if hasattr(obs, 'sv') else []
    if len(satellites) == 0:
        raise ValueError("No satellites found in RINEX file")
    
    if verbose:
        print(f"Found {len(satellites)} satellites")
    
    # 5. Process each satellite
    sat_dict: Dict[str, pd.DataFrame] = {}
    skipped = []
    
    for sat in satellites:
        sat_data = obs.sel(sv=sat)
        df = sat_data.to_dataframe().reset_index()
        
        # Standardize columns (RINEX 3→2)
        df = standardize_columns(df, verbose=False)
        
        # Extract observation columns
        obs_cols = [col for col in df.columns if col not in ['time', 'sv']]
        if not obs_cols:
            skipped.append((sat, "No observation columns"))
            continue
        
        # Remove completely empty rows
        df_clean = df[['time'] + obs_cols].dropna(subset=obs_cols, how='all')
        
        if len(df_clean) < min_epochs:
            skipped.append((sat, f"Too few epochs ({len(df_clean)})"))
            continue
        
        # Convert time
        df_clean['time'] = pd.to_datetime(df_clean['time'])
        df_clean = df_clean.sort_values('time').reset_index(drop=True)
        
        # Validate observation pairs
        is_valid, msg = validate_observation_pair(df_clean, sat)
        if not is_valid:
            skipped.append((sat, msg))
            continue
        
        # Add time gap detection
        if detect_gaps:
            df_clean = add_time_gaps(df_clean, gap_threshold)
            n_gaps = df_clean['has_gap'].sum()
            if n_gaps > 0 and verbose:
                print(f"  {sat}: {n_gaps} gap(s) detected")
        
        # Store result
        sat_dict[sat] = df_clean
        
        if verbose:
            obs_list = [col for col in df_clean.columns if col not in ['time', 'time_diff', 'has_gap']]
            print(f"✓ {sat}: {len(df_clean)} epochs, obs: {obs_list}")
    
    # 6. Report skipped satellites
    if verbose and skipped:
        print(f"\n{'='*70}")
        print(f"Skipped {len(skipped)} satellites:")
        for sat, reason in skipped:
            print(f"  ⚠ {sat}: {reason}")
    
    # 7. Final validation
    if not sat_dict:
        raise ValueError("No satellites with valid L1/L2 + C1/C2 observations found")
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"✓ Successfully loaded {len(sat_dict)} satellites")
        print(f"{'='*70}\n")
    
    return sat_dict


def get_observation_summary(sat_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Generate summary table of loaded satellites."""
    summary = []
    
    for sat_id, df in sat_dict.items():
        system = sat_id[0] if len(sat_id) > 0 else 'G'
        n_epochs = len(df)
        
        # Time span
        duration = (df['time'].max() - df['time'].min()).total_seconds() / 3600
        
        # Sampling interval
        sampling = df.attrs.get('sampling_interval', 'N/A')
        
        # Completeness
        obs_types = [col for col in df.columns if col not in ['time', 'time_diff', 'has_gap', 'sv']]
        completeness = {obs: (df[obs].notna().sum() / n_epochs * 100) for obs in obs_types}
        
        # Gaps
        n_gaps = df['has_gap'].sum() if 'has_gap' in df.columns else 0
        
        summary.append({
            'Satellite': sat_id,
            'System': system,
            'Epochs': n_epochs,
            'Duration (h)': f"{duration:.2f}",
            'Sampling (s)': f"{sampling:.1f}" if isinstance(sampling, (int, float)) else 'N/A',
            'Gaps': n_gaps,
            'L1 (%)': f"{completeness.get('L1', 0):.1f}",
            'L2 (%)': f"{completeness.get('L2', 0):.1f}",
            'C1 (%)': f"{completeness.get('C1', 0):.1f}",
            'C2 (%)': f"{completeness.get('C2', 0):.1f}",
        })
    
    return pd.DataFrame(summary)


if __name__ == "__main__":
    # Test
    test_file = "../Data/tehn2580.21o"
    
    if os.path.exists(test_file):
        sat_dict = read_rinex(test_file, systems='G')
        summary = get_observation_summary(sat_dict)
        print(summary.to_string(index=False))
    else:
        print("Test file not found. Provide RINEX file path.")
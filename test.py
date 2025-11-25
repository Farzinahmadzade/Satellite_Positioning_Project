from process_prn import process_prn
import pandas as pd

nav_path = "Data/brdc2580.21n"
prn_id = "G05"
obs_time = pd.Timestamp("2021-09-15 00:00:00")

df = process_prn(nav_path, prn_id, obs_time=obs_time, save_csv=True, show_plot=True)

if df is not None:
    print(df.head())
else:
    print("Ephemeris not found or computation aborted.")

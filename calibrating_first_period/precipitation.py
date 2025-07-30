# ----------------------------------------------------
# Import Required Libraries
# ----------------------------------------------------
import hf_hydrodata as hf
import xarray as xr
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ----------------------------------------------------
# Define Output Directory
# ----------------------------------------------------
output_dir = "/home/ms6730/SBI_calibration/calibrating_first_period"
os.makedirs(output_dir, exist_ok=True)

# ----------------------------------------------------
# Download NetCDF File using hf_hydrodata
# ----------------------------------------------------
variables = ["precipitation"]
huc_id = "02070001"
options = {
    "dataset": "CW3E",
    "dataset_version": "0.9",
    "temporal_resolution": "daily",
    "start_time": "2003-12-16",
    "end_time": "2004-01-18",
    "huc_id": huc_id,
    "grid": "conus2"
}

hf.get_gridded_files(options, variables=variables, filename_template="{dataset}_{wy}.nc")

# ----------------------------------------------------
# Load NetCDF Dataset
# ----------------------------------------------------
nc_filename = "CW3E_2004.nc"
if not os.path.exists(nc_filename):
    raise FileNotFoundError(f"{nc_filename} not found.")

ds = xr.open_dataset(nc_filename)
print(ds)

# ----------------------------------------------------
# Extract precipitation data
# ----------------------------------------------------
if "precipitation" not in ds:
    raise KeyError("The variable 'precipitation' was not found in the dataset.")

precip = ds["precipitation"]  # shape: (time, y, x)
time = ds["time"].values

# ----------------------------------------------------
# Compute spatial mean
# ----------------------------------------------------
precip_mean = precip.mean(dim=["x", "y"])  # shape: (time,)

# ----------------------------------------------------
# Save hourly precipitation to CSV
# ----------------------------------------------------
hourly_df = pd.DataFrame({
    "time": time,
    "precip_mm_hr": precip_mean.values
})
hourly_csv = os.path.join(output_dir, "precipitation_huc02070001_hourly.csv")
hourly_df.to_csv(hourly_csv, index=False)
print(f"Saved hourly data to: {hourly_csv}")

# ----------------------------------------------------
# Load hourly CSV and convert to daily totals
# ----------------------------------------------------
df = pd.read_csv(hourly_csv)
df["time"] = pd.to_datetime(df["time"])
df.set_index("time", inplace=True)

# Resample to daily totals
df_daily = df.resample("D").sum().reset_index()
df_daily.columns = ["date", "precip_mm_day"]

# ----------------------------------------------------
# Save daily totals to CSV
# ----------------------------------------------------
daily_csv = os.path.join(output_dir, "precipitation_huc02070001_daily.csv")
df_daily.to_csv(daily_csv, index=False)
print(f"Saved daily data to: {daily_csv}")

# ----------------------------------------------------
# Plot daily precipitation
# ----------------------------------------------------
plt.figure(figsize=(12, 5))
plt.plot(df_daily["date"], df_daily["precip_mm_day"], color='royalblue', linewidth=1.5)
plt.title("Daily Precipitation over HUC 02070001")
plt.xlabel("Date")
plt.ylabel("Precipitation (mm/day)")
plt.grid(True)

# ----------------------------------------------------
# Format x-axis
# ----------------------------------------------------
locator = mdates.AutoDateLocator(minticks=6, maxticks=12)
formatter = mdates.DateFormatter('%d %b %Y')
plt.gca().xaxis.set_major_locator(locator)
plt.gca().xaxis.set_major_formatter(formatter)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

# ----------------------------------------------------
# Save plot
# ----------------------------------------------------
plot_path = os.path.join(output_dir, "precipitation_huc02070001_daily_plot.png")
plt.savefig(plot_path, dpi=300, bbox_inches='tight')
print(f"Saved plot to: {plot_path}")
plt.show()

# ----------------------------------------------------
# Filter days with non-zero precipitation
# ----------------------------------------------------
nonzero_precip = df_daily[df_daily["precip_mm_day"] > 0]
nonzero_csv = os.path.join(output_dir, "nonzero_precip_dates.csv")
nonzero_precip.to_csv(nonzero_csv, index=False)
print(f"Saved non-zero precipitation dates to: {nonzero_csv}")

import json
import pandas as pd
from pathlib import Path

# Resolve paths relative to project root
project_root = Path(__file__).resolve().parent.parent

# Location of raw data
input_file = project_root / "data" / "raw" / "weather_raw.json"

# Read raw JSON
with open(input_file, "r") as file:
    data = json.load(file)

# Extract the current weather section
current_weather = data["current"]

# Convert dictionary into DataFrame
df = pd.DataFrame([current_weather])

# Add location information for Alur, Kurnool District
df["city"] = "Alur"

# Rename columns
df = df.rename(
    columns={
        "time": "timestamp",
        "temperature_2m": "temperature",
        "relative_humidity_2m": "humidity",
        "wind_speed_10m": "wind_speed"
    }
)

# Select only the columns we need
df = df[
    [
        "city",
        "timestamp",
        "temperature",
        "humidity",
        "wind_speed"
    ]
]

# Convert timestamp to datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Display transformed data
print("\nTransformed data:")
print(df)

# Create processed directory
output_dir = project_root / "data" / "processed"
output_dir.mkdir(parents=True, exist_ok=True)

# Save transformed data
output_file = output_dir / "weather_clean.csv"
df.to_csv(output_file, index=False)

print(f"\nClean data saved to: {output_file}")

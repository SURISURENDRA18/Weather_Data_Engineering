import requests
import json
from pathlib import Path

url = "https://api.open-meteo.com/v1/forecast"

# Parameters configured for Alur (Kurnool District, Andhra Pradesh - PIN 518395)
# Geographic coordinates: 15°23′39″N 77°13′35″E (15.39417°N, 77.22639°E)
params = {
    "latitude": 15.39417,
    "longitude": 77.22639,
    "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
    "timezone": "Asia/Kolkata"
}

response = requests.get(url, params=params, timeout=10)

print("Status code:", response.status_code)

response.raise_for_status()

data = response.json()

# Project data directory
project_root = Path(__file__).resolve().parent.parent
output_dir = project_root / "data" / "raw"
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / "weather_raw.json"

with open(output_file, "w") as file:
    json.dump(data, file, indent=4)

print(f"Raw weather data saved to: {output_file}")

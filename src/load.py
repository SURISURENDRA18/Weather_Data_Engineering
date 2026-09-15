import os
from pathlib import Path
import pandas as pd
import mysql.connector
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Read transformed data
project_root = Path(__file__).resolve().parent.parent
input_file = project_root / "data" / "processed" / "weather_clean.csv"
df = pd.read_csv(input_file)

print("Data to load:")
print(df)

# Detect host: If running inside Docker, connect to host machine via host.docker.internal
mysql_host = os.getenv("MYSQL_HOST", "127.0.0.1")
if mysql_host in ("127.0.0.1", "localhost") and Path("/.dockerenv").exists():
    mysql_host = "host.docker.internal"

connection = mysql.connector.connect(
    host=mysql_host,
    port=int(os.getenv("MYSQL_PORT", 3306)),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE")
)

cursor = connection.cursor()

# Idempotent Upsert query: Insert new records, update if (city, timestamp) already exists
upsert_query = """
INSERT INTO weather_data
(city, timestamp, temperature, humidity, wind_speed)
VALUES (%s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    temperature = VALUES(temperature),
    humidity = VALUES(humidity),
    wind_speed = VALUES(wind_speed);
"""

for _, row in df.iterrows():
    values = (
        row["city"],
        row["timestamp"],
        row["temperature"],
        row["humidity"],
        row["wind_speed"]
    )

    cursor.execute(upsert_query, values)

# Save changes
connection.commit()

print(f"\n{len(df)} row(s) processed (inserted/updated) into MySQL.")

# Close connection
cursor.close()
connection.close()

print("MySQL connection closed.")

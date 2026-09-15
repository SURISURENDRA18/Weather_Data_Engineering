# 🌤️ Weather Data Engineering Pipeline

An end-to-end, production-grade Data Engineering ETL pipeline that extracts live weather data, cleans and validates it using **Pandas**, loads it into a **MySQL** data warehouse with **idempotent upsert logic**, and orchestrates scheduled execution using **Apache Airflow 3** on **Docker Compose**.

Built entirely using free, open-source tools and zero paid cloud services.

---

## 🏛️ Pipeline Architecture

```text
               ┌───────────────────────┐
               │    Open-Meteo API     │
               └──────────┬────────────┘
                          │ HTTP GET (REST API)
                          ▼
               ┌───────────────────────┐
               │    src/extract.py     │ ──► Saves data/raw/weather_raw.json
               └──────────┬────────────┘
                          │ Raw JSON Payload
                          ▼
               ┌───────────────────────┐
               │   src/transform.py    │ ──► Cleans & formats with Pandas
               └──────────┬────────────┘     Saves data/processed/weather_clean.csv
                          │ Structured Tabular DataFrame
                          ▼
               ┌───────────────────────┐
               │     src/load.py       │ ──► Idempotent Upsert (ON DUPLICATE KEY UPDATE)
               └──────────┬────────────┘
                          │ SQL Connection
                          ▼
               ┌───────────────────────┐
               │   MySQL (weather_db)  │ ──► Stores weather_data table
               └───────────────────────┘
                          ▲
                          │ Task Orchestration & Scheduling
               ┌──────────┴────────────┐
               │     Apache Airflow    │ ──► extract >> transform >> load
               │    (Docker Compose)   │     Scheduled every 5 minutes
               └───────────────────────┘
```

---

## 🛠️ Tech Stack & Technologies Used

| Technology | Purpose |
| :--- | :--- |
| **Python 3** | Core programming language for extraction, transformation, and database loading scripts |
| **Open-Meteo API** | Free, open-source weather forecast API (no API key required) |
| **Pandas** | Data manipulation, schema structuring, timestamp conversion, and cleaning |
| **MySQL 8.0 / 9.x** | Relational Database Management System (RDBMS) storing final weather records |
| **Apache Airflow 3.3.1** | Workflow orchestrator managing DAG execution, task retries, dependencies, and logs |
| **Docker & Docker Compose** | Multi-container isolation for Airflow, PostgreSQL (metadata), Redis (broker), and MySQL |
| **python-dotenv** | Decoupling credentials and sensitive environment variables from source code |
| **Git & GitHub** | Version control with strict `.gitignore` patterns protecting credentials |

---

## 📂 Project Structure

```text
weather-data-engineering/
│
├── dags/
│   └── weather_etl_dag.py        # Airflow DAG defining extract >> transform >> load
│
├── src/
│   ├── extract.py                # Extracts current weather metrics from Open-Meteo
│   ├── transform.py              # Cleans raw JSON, converts datetimes, outputs CSV
│   ├── load.py                   # Connects to MySQL and executes idempotent upsert
│   └── extractor.py              # Script alias wrapper
│
├── data/
│   ├── raw/                      # Raw JSON API snapshots (ignored in git)
│   │   └── weather_raw.json
│   └── processed/                # Cleaned, structured CSV ready for database ingestion
│       └── weather_clean.csv
│
├── sql/
│   └── create_tables.sql         # DDL script creating weather_data table with UNIQUE constraint
│
├── config/                       # Airflow configuration directory
├── plugins/                      # Airflow custom plugins directory
├── Dockerfile                    # Custom Airflow image with pandas, requests, and mysql connectors
├── requirements.txt              # Python dependency manifest
├── docker-compose.yaml           # Official Apache Airflow 3 multi-service compose stack
├── docker-compose.yml            # Standalone MySQL service container configuration
├── .env.example                  # Safe template for required environment variables
├── .gitignore                    # Prevents secrets (.env), virtualenv, and runtime logs from git
└── README.md                     # Project documentation
```

---

## 🔑 Key Engineering Concepts Implemented

### 1. Task Orchestration & Dependency Management
In Airflow, tasks are organized into a **Directed Acyclic Graph (DAG)**:
```python
extract >> transform >> load
```
Airflow guarantees that transformation only begins if extraction succeeds, and database loading only begins if transformation is successful.

### 2. Idempotency & Duplicate Prevention
A critical rule in data engineering: **running a pipeline multiple times with the same data must produce the same result without creating duplicates.**
- **Business Key**: `(city, timestamp)`
- **Database Constraint**: `CONSTRAINT unique_city_timestamp UNIQUE (city, timestamp)`
- **Upsert Logic** in `load.py`:
  ```sql
  INSERT INTO weather_data
  (city, timestamp, temperature, humidity, wind_speed)
  VALUES (%s, %s, %s, %s, %s)
  ON DUPLICATE KEY UPDATE
      temperature = VALUES(temperature),
      humidity = VALUES(humidity),
      wind_speed = VALUES(wind_speed);
  ```
If the DAG reruns for the same timestamp, MySQL updates the existing record instead of inserting a duplicate row.

### 3. Container-to-Host Networking
Because Airflow runs inside Docker while MySQL can run on the host or in Docker:
- `127.0.0.1` inside a container refers to the container itself.
- `src/load.py` dynamically detects the environment:
  - If running in Docker (`/.dockerenv` exists): routes host connection via `host.docker.internal:3306`.
  - If running on local Mac: connects directly via `127.0.0.1:3306`.

### 4. Credential Security
- Database passwords and API configurations are loaded at runtime via `.env`.
- `.env` is listed in `.gitignore` to prevent leaking credentials to GitHub.
- `.env.example` is committed as a template for other developers.

---

## 🚀 Getting Started

### 1. Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (allocate at least 4 GB RAM)
- Python 3.10+
- Git

### 2. Clone the Repository
```zsh
git clone https://github.com/SURISURENDRA18/Weather_Data_Engineering.git
cd Weather_Data_Engineering
```

### 3. Set Up Virtual Environment (Local Run)
```zsh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the example template to create your `.env`:
```zsh
cp .env.example .env
```
Edit `.env` with your database credentials and configuration:
```ini
# MySQL Database Configuration
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password_here
MYSQL_DATABASE=weather_db

# Airflow User ID (required for Linux/Mac volume permissions)
AIRFLOW_UID=50000
```

---

## 🗄️ Database Setup

Run the DDL script in MySQL or MySQL Workbench:
```sql
USE weather_db;

CREATE TABLE IF NOT EXISTS weather_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    timestamp DATETIME NOT NULL,
    temperature FLOAT,
    humidity FLOAT,
    wind_speed FLOAT,
    CONSTRAINT unique_city_timestamp UNIQUE (city, timestamp)
);
```

---

## 🐳 Running with Apache Airflow (Docker)

### 1. Initialize Airflow
Run the initialization container to migrate the metadata database and create the admin user:
```zsh
docker compose -f docker-compose.yaml up airflow-init
```

### 2. Build the Custom Airflow Image
Build the container with project dependencies (`pandas`, `mysql-connector-python`, `requests`):
```zsh
docker compose -f docker-compose.yaml build
```

### 3. Start Airflow
```zsh
docker compose -f docker-compose.yaml up -d
```

### 4. Access the Airflow Web UI
Open your browser at **[http://localhost:8080](http://localhost:8080)**:
- **Username**: `airflow`
- **Password**: `airflow`

Find the **`weather_etl`** DAG:
- Toggle the switch to **Unpause**
- Click **Trigger DAG** to run the pipeline manually, or let it run automatically on its **5-minute schedule**.

### 5. Stop Airflow
```zsh
docker compose -f docker-compose.yaml down
```

---

## 📊 Sample SQL Analytics Queries

Once data is loaded, run these analytical queries in MySQL:

#### 1. View Latest Weather Records
```sql
USE weather_db;
SELECT * FROM weather_data 
ORDER BY timestamp DESC 
LIMIT 10;
```

#### 2. Verify Zero Duplicates (Idempotency Audit)
```sql
SELECT 
    city, 
    timestamp, 
    COUNT(*) AS record_count
FROM weather_data
GROUP BY city, timestamp
HAVING COUNT(*) > 1;
```

#### 3. Weather Summary Statistics
```sql
SELECT 
    city,
    ROUND(AVG(temperature), 2) AS avg_temp_c,
    ROUND(MIN(temperature), 2) AS min_temp_c,
    ROUND(MAX(temperature), 2) AS max_temp_c,
    ROUND(AVG(humidity), 2) AS avg_humidity_pct,
    ROUND(AVG(wind_speed), 2) AS avg_wind_speed_kmh,
    COUNT(*) AS total_readings
FROM weather_data
GROUP BY city;
```

---

## 👤 Author

- **Suri Surendra** – [GitHub](https://github.com/SURISURENDRA18)

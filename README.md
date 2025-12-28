# EV Charging Analytics Platform - Backend

A comprehensive backend system for analyzing EV charging patterns with real-time insights, built with **FastAPI**, **PostgreSQL** and **SQLAlchemy**.

## Overview

This project provides a robust API-driven analytics platform that processes EV charging data, calculates key performance indicators (KPIs), and enables detailed analysis of charging behavior patterns. It's designed to support power grid management and energy forecasting by providing actionable insights into EV charging demand.

## Key Features

- **RESTful API** for accessing charging load data and analytics
- **Comprehensive KPI Calculations** for energy demand analysis
- **Time-Series Analysis** with hourly and daily aggregations
- **PostgreSQL Database** for persistent data storage
- **CORS Support** for integration with frontend applications
- **Flexible Filtering** with date range queries

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Relational database for data persistence
- **Pandas** - Data manipulation and preprocessing
- **Python 3.10+** - Core runtime

## Project Structure

```
├── main.py                      # FastAPI application and API endpoints
├── database_model.py            # SQLAlchemy ORM models
├── ev_charging_database.py      # Database connection and session management
├── models.py                    # Pydantic data models
├── preprocessing.py             # Data preprocessing and cleaning
├── ingestion.py                 # Data ingestion pipeline
├── pyproject.toml              # Project dependencies and metadata
└── ev_charging_data/           # Raw CSV datasets
    └── Dataset 2_Hourly EV loads - Per user.csv (primary dataset)
```

## Installation & Setup

### Prerequisites

- Python 3.10 or higher
- PostgreSQL database
- pip, poetry or uv for dependency management

### Installation Steps

1. **Clone or download the project**
   ```bash
   cd /home/user/ev_charging_analytics
   ```

2. **Install dependencies**

   **Option 1: Using pip with pyproject.toml**
   ```bash
   pip install -e .
   ```

   **Option 2: Using uv (faster, recommended)**
   ```bash
   uv pip sync requirements.txt
   ```
   
   Or to use uv's project management:
   ```bash
   uv sync
   ```

   **Option 3: Using requirements.txt with pip**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Option 4: Using poetry**
   ```bash
   poetry install
   ```

3. **Set up environment variables**
   Create a `.env` file with your PostgreSQL credentials:
   ```
   DATABASE_URL=postgresql://user:password@localhost/database_name
   ```

4. **Run data ingestion** (one-time setup)
   ```bash
   python ingestion.py
   ```
   This loads the EV charging data into the PostgreSQL database.

5. **Start the API server**
   ```bash
   uvicorn main:app --reload
   ```
   
   The API will be available at `http://localhost:8000`
   - Interactive API docs: `http://localhost:8000/docs`
   - Alternative docs: `http://localhost:8000/redoc`

## Database Schema

### HrlyEVLoad Table

The core table storing hourly EV charging load data:

| Column | Type | Description |
|--------|------|-------------|
| `index` | Integer (PK) | Primary key |
| `date_from` | DateTime | Session start time (indexed) |
| `date_to` | DateTime | Session end time |
| `user_id` | String | Unique user identifier |
| `session_id` | Integer | Charging session identifier |
| `synthetic_3_6_kwh` | Numeric | 3.6 kW synthetic load data |
| `synthetic_7_2_kwh` | Numeric | 7.2 kW synthetic load data |
| `flex_3_6_kwh` | Numeric | 3.6 kW flexible load data |
| `flex_7_2_kwh` | Numeric | 7.2 kW flexible load data |

## API Endpoints

### Data Access Endpoints

#### **GET /** 
Welcome endpoint
```bash
curl http://localhost:8000/
# Response: "Welcome to from EV Charging Project!"
```

#### **GET /users**
Retrieve all unique users in the database
```bash
curl http://localhost:8000/users
# Response: ["user_1", "user_2", "user_3", ...]
```

#### **GET /hourly_loads**
Get hourly load data (limited to 20 records)
```bash
curl http://localhost:8000/hourly_loads
```

#### **GET /load/{user_id}/hourly**
Get hourly charging data for a specific user with optional date filtering
```bash
curl "http://localhost:8000/load/user_1/hourly?start_date=2024-01-01T00:00:00&end_date=2024-01-31T23:59:59"
```

**Query Parameters:**
- `user_id` (path) - Required user identifier
- `start_date` (query) - Optional ISO format start date
- `end_date` (query) - Optional ISO format end date

#### **GET /load/daily**
Get daily aggregated energy consumption
```bash
curl "http://localhost:8000/load/daily?start_date=2024-01-01T00:00:00&end_date=2024-01-31T23:59:59"
```

**Response:**
```json
[
  {"day": "2024-01-01", "daily_energy_kwh": 1234.56},
  {"day": "2024-01-02", "daily_energy_kwh": 1567.89}
]
```

---

### KPI Endpoints

#### **GET /kpi/total-energy**
Calculate total energy consumption across all users
```bash
curl "http://localhost:8000/kpi/total-energy?start_date=2024-01-01T00:00:00&end_date=2024-01-31T23:59:59"
```

**Response:**
```json
{
  "total_energy_kwh": 45678.90
}
```

#### **GET /kpi/daily-average**
Calculate average daily energy consumption
```bash
curl "http://localhost:8000/kpi/daily-average?start_date=2024-01-01T00:00:00&end_date=2024-01-31T23:59:59"
```

**Response:**
```json
{
  "avg_daily_energy_kwh": 1234.56
}
```

#### **GET /kpi/daily-average-last-7-days**
Calculate 7-day rolling average of daily energy consumption (automatically uses latest data)
```bash
curl http://localhost:8000/kpi/daily-average-last-7-days
```

**Response:**
```json
{
  "avg_daily_energy_kwh": 1456.78,
  "period": "last_7_days",
  "from": "2024-01-25",
  "to": "2024-02-01"
}
```

#### **GET /kpi/peak-daily**
Find the peak daily energy consumption
```bash
curl "http://localhost:8000/kpi/peak-daily?start_date=2024-01-01T00:00:00&end_date=2024-01-31T23:59:59"
```

**Response:**
```json
{
  "peak_daily_energy_kwh": 2100.45
}
```

#### **GET /kpi/peak-hourly**
Find the peak hourly load across all users
```bash
curl "http://localhost:8000/kpi/peak-hourly?start_date=2024-01-01T00:00:00&end_date=2024-01-31T23:59:59"
```

**Response:**
```json
{
  "peak_hourly_load_kwh": 567.89
}
```

#### **GET /kpi/daily_utilization**
Get daily charging utilization (active hours per day)
```bash
curl "http://localhost:8000/kpi/daily_utilization?start_date=2024-01-01T00:00:00&end_date=2024-01-31T23:59:59"
```

**Response:**
```json
[
  {"day": "2024-01-01", "active_hours": 18},
  {"day": "2024-01-02", "active_hours": 16}
]
```

#### **GET /kpi/avg-active-hours-per-day**
Calculate average active charging hours per day
```bash
curl "http://localhost:8000/kpi/avg-active-hours-per-day?start_date=2024-01-01T00:00:00&end_date=2024-01-31T23:59:59"
```

**Response:**
```json
{
  "avg_active_charging_hours_per_day": 16.5
}
```

---

## Key Performance Indicators (KPIs)

### Energy Metrics

1. **Total Energy Consumption** - Aggregated energy consumption across all users over a period
2. **Daily Average Energy** - Mean daily energy consumption, useful for baseline planning
3. **7-Day Rolling Average** - Recent consumption trends for short-term forecasting
4. **Peak Daily Load** - Maximum daily energy demand, critical for infrastructure planning
5. **Peak Hourly Load** - Maximum single-hour demand across all users

### Utilization Metrics

1. **Daily Utilization** - Number of active charging hours per day
2. **Average Active Hours** - Mean active charging hours per day across a period

### Business Applications

These KPIs enable:
- **Grid Capacity Planning** - Understanding peak demand to size infrastructure
- **Demand Forecasting** - Trend analysis for future load predictions
- **Pricing Strategy** - Dynamic pricing based on utilization patterns
- **Resource Allocation** - Optimal distribution of charging infrastructure
- **Performance Monitoring** - Tracking system efficiency and user engagement

## Data Preprocessing

The system includes robust data preprocessing in `preprocessing.py`:

- **Column Normalization** - Standardizes input column names to database schema
- **Date Parsing** - Converts date strings (DD.MM.YYYY HH:MM format) to ISO format
- **Numeric Conversion** - Handles comma-decimal conversion and type coercion
- **Data Cleaning** - Handles missing/invalid values gracefully

## Data Ingestion Pipeline

The `ingestion.py` script handles:
- Loading raw CSV data from `ev_charging_data/` directory
- Applying preprocessing transformations
- Inserting cleaned data into PostgreSQL
- Creating necessary database tables automatically

## Cross-Origin Resource Sharing (CORS)

The API is configured to accept requests from:
- `http://localhost:3000`
- `http://127.0.0.1:3000`
- Frontend dashboard applications

CORS middleware is enabled for:
- All HTTP methods
- All headers
- Credentials support

## Error Handling

The API implements comprehensive error handling:

- **404 Not Found** - User data or date range returns no results
- **400 Bad Request** - Invalid date range (start_date > end_date)
- **500 Server Error** - Database connectivity or query execution issues

Example error response:
```json
{
  "detail": "No data found for given user"
}
```

## Usage Examples

### Get all users
```bash
curl http://localhost:8000/users
```

### Get daily energy for January 2024
```bash
curl "http://localhost:8000/load/daily?start_date=2024-01-01T00:00:00&end_date=2024-01-31T23:59:59"
```

### Get specific user's hourly data
```bash
curl "http://localhost:8000/load/user_1/hourly"
```

### Get system-wide KPIs
```bash
curl http://localhost:8000/kpi/total-energy
curl http://localhost:8000/kpi/peak-hourly
curl http://localhost:8000/kpi/avg-active-hours-per-day
```

## Development

### Running Tests

```bash
pytest
```

### Code Structure Best Practices

- **Separation of Concerns** - Database models, API endpoints, and preprocessing are in separate modules
- **Dependency Injection** - SQLAlchemy session management via FastAPI dependencies
- **Type Hints** - Full type annotations for better IDE support and code clarity
- **Modular Design** - Easy to extend with new endpoints or KPI calculations

## Performance Considerations

- **Database Indexing** - The `date_from` column is indexed for faster time-range queries
- **Query Optimization** - Subqueries are used efficiently to aggregate large datasets
- **Date Range Filtering** - Endpoints support optional date filters to reduce data transfer
- **Numerical Precision** - Numeric(6,3) ensures 3 decimal places for energy measurements

## Contributing

To add new endpoints or KPIs:

1. Define the calculation logic in `main.py`
2. Use SQLAlchemy query builders for database operations
3. Return standardized JSON responses
4. Include proper error handling
5. Document the endpoint with curl examples

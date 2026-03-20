# ⚡ Energy Consumption Dashboard — Noida Campus

A Streamlit multi-page web application serving as the unified energy dashboard for the Noida campus. It ingests data from three energy sources — **Grid**, **Solar**, and **Diesel Generator** — normalises them into a single data model, displays a unified live dashboard with source-specific tabs, and runs a configurable scheduled job that curates and sends a formatted HTML email report every morning.

The project is organised into three agent sub-modules:
- **Data Ingestion Agent** — loads, validates, processes, and exports energy data
- **Dashboard** — Streamlit UI with five tabs
- **Mail Scheduling Agent** — background email scheduler with configurable HTML reports

## Quick Start

```bash
# Create virtual environment
python -m venv venv

# Activate
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up SMTP credentials
cp .env.example .env
# Edit .env with your actual SMTP credentials

# Launch the dashboard
streamlit run app.py
# Opens at http://localhost:8501
```

## Features

### 📊 Overview Tab
- Six KPI metric cards (Total consumption, Solar generated, Solar %, Total cost, Energy saved, Avg temperature)
- Date range filter affecting all charts and tables
- Stacked bar chart: Daily energy mix (Grid + Solar + Diesel)
- Line chart: Source cost comparison
- Unified data table with Excel download

### 🔌 Grid Tab
- Grid data follows the Electrical Optimization (1) Excel ECS format (no solar column)
- Grid-specific KPIs (Total KWh, Cost, Peak day, Average per day)
- Bar chart: Consumption by date
- Grid data table with download

### ☀️ Solar Tab
- Solar KPIs (Total KWh, Target %, Peak day, Energy saved, Fault events)
- Inverter SMB status indicators (green/red)
- Area chart: Solar generation by day with target line
- Stacked bar chart: SMB contribution breakdown
- Solar data table with download

### ⛽ Diesel Tab
- DG KPIs (Total KWh, Cost, Runtime, Fuel consumed)
- Bar chart: DG usage by date
- DG usage log (only active entries)
- Diesel data table with download

### 📧 Job Scheduler Tab
- Email configuration (To, CC, send time)
- Upload custom Excel template
- Email body customisation with section toggles
- Start/Stop scheduler controls
- Send now (test) button
- Schedule history log
- Email table follows Electrical Optimization (1) ECS sheet format

## Data Sources

Grid data is fetched from the configured remote Excel URL in `config.yaml` (`data.grid_file`) without credentials and modelled after the ECS sheet with columns:
`Date | Day | Time | Ambient Temperature °C | Grid Units Consumed (KWh) | Total Units Consumed (KWh) | Total Units Consumed in INR | Energy Saving in INR`

If the remote URL is unavailable/unauthorized, loader automatically falls back to `data.grid_file_fallback` (default: `./data/grid_data.csv`).

Solar column is **omitted** from the grid data per design.

Sample data covers 16 Feb – 19 Mar 2026. Replace with real data as source feeds come online.

## Project Structure

```
energy-dashboard/
├── app.py                                  # Streamlit entry point
├── config.yaml                             # App and email defaults
├── requirements.txt
├── .env / .env.example                     # SMTP credentials
├── .gitignore
├── README.md
│
├── data_ingestion_agent/                   # DATA INGESTION AGENT
│   ├── __init__.py
│   ├── loader.py                           # Read & validate CSVs
│   ├── processor.py                        # Merge, derive columns, KPIs
│   ├── exporter.py                         # Generate .xlsx exports
│   └── seed.py                             # Seed dummy CSV data
│
├── dashboard/                              # DASHBOARD
│   ├── __init__.py
│   ├── overview.py                         # Overview tab
│   ├── grid_tab.py                         # Grid tab
│   ├── solar_tab.py                        # Solar tab
│   ├── diesel_tab.py                       # Diesel tab
│   └── scheduler_tab.py                    # Job Scheduler tab UI
│
├── mail_scheduling_agent/                  # MAIL SCHEDULING AGENT
│   ├── __init__.py
│   ├── scheduler.py                        # Background scheduler thread
│   ├── emailer.py                          # Build HTML email & send SMTP
│   └── templates/
│       └── email_body.html                 # Jinja2 email template (ECS format)
│
├── data/                                   # Local data files (solar/diesel); grid can be remote URL
│   ├── solar_data.csv
│   └── diesel_data.csv
│
└── output/                                 # Auto-created
    ├── scheduler_log.json
    └── *.xlsx
```

## Tech Stack

- **Streamlit** — Web UI framework
- **Pandas** — Data processing
- **Plotly** — Interactive charts
- **Jinja2** — HTML email templating
- **schedule** — Background job scheduling
- **openpyxl** — Excel export
- **python-dotenv** — Environment variable management

---

*Version 1.0 · Phase 1 · Energy Consumption Optimization & Sustainability Agent · Noida Campus*

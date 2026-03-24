# ⚡ Energy Data + Mail Services — Noida Campus

This module now provides backend data-processing and email-report services used by the FastAPI backend and React frontend.

It includes:

- **Data Ingestion Agent**: load, validate, merge, and transform Grid/Solar/Diesel data
- **Mail Scheduling Agent**: build ECS-format HTML mail content and send scheduled reports

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

# Configure SMTP and secrets
cp .env.example .env
```

## Project Structure

```
energy-dashboard/
├── config.yaml
├── requirements.txt
├── README.md
├── data_ingestion_agent/
├── mail_scheduling_agent/
├── data/
└── output/
```

## Notes

- Streamlit UI components have been removed.
- Frontend UI is provided by the React app in the workspace `frontend` folder.

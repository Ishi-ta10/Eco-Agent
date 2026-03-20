"""
app.py — Streamlit entry point for the Energy Consumption Dashboard.
Tabs: Overview · Grid · Solar · Diesel · Job Scheduler

Project layout:
  energy-dashboard/
  ├── app.py                          ← this file
  ├── config.yaml
  ├── data_ingestion_agent/           ← data loading, processing, export
  ├── dashboard/                      ← Streamlit UI tabs
  ├── mail_scheduling_agent/          ← email scheduling & sending
  ├── data/                           ← CSV seed data
  └── output/                         ← generated reports & logs
"""

import os
import sys

import streamlit as st

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from data_ingestion_agent.seed import seed_data_files
from data_ingestion_agent.loader import load_config, load_all
from data_ingestion_agent.processor import build_unified_dataframe

from dashboard.overview import render_overview_tab
from dashboard.grid_tab import render_grid_tab
from dashboard.solar_tab import render_solar_tab
from dashboard.diesel_tab import render_diesel_tab
from dashboard.scheduler_tab import render_scheduler_tab

from mail_scheduling_agent.scheduler import (
    start_background_scheduler, load_scheduler_config,
)
from mail_scheduling_agent.emailer import send_daily_report

# ──────────────────────────────────────────────
# Seed data files on first run
# ──────────────────────────────────────────────
seed_data_files()

# ──────────────────────────────────────────────
# Page config
# ──────────────────────────────────────────────
config = load_config()
st.set_page_config(
    page_title=config["app"]["title"],
    page_icon=config["app"]["page_icon"],
    layout="wide",
)

st.title(f"{config['app']['page_icon']} {config['app']['title']}")
st.caption(f"Version {config['app']['version']}")

# ──────────────────────────────────────────────
# Load data
# ──────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    cfg, grid, solar, diesel = load_all()
    unified = build_unified_dataframe(grid, solar, diesel)
    return cfg, grid, solar, diesel, unified

cfg, grid_raw, solar_raw, diesel_raw, unified_all = load_data()

# ──────────────────────────────────────────────
# Background scheduler — start once
# ──────────────────────────────────────────────
if "scheduler_started" not in st.session_state:
    st.session_state["scheduler_started"] = False
    st.session_state["scheduler_running"] = False

sched_cfg = load_scheduler_config(PROJECT_ROOT)
if sched_cfg.get("auto_start", False) and not st.session_state.get("scheduler_started"):
    send_time = sched_cfg.get("send_time", cfg["email"]["send_time_ist"])
    start_background_scheduler(send_daily_report, send_time)
    st.session_state["scheduler_started"] = True
    st.session_state["scheduler_running"] = True

# ──────────────────────────────────────────────
# Date range filter (shared across tabs)
# ──────────────────────────────────────────────
all_dates = sorted(unified_all["Date"].unique())
min_date = all_dates[0]
max_date = all_dates[-1]

date_range = st.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    key="global_date_range",
)
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_d, end_d = date_range
else:
    start_d, end_d = min_date, max_date

# ──────────────────────────────────────────────
# Tabs
# ──────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", "🔌 Grid", "☀️ Solar", "⛽ Diesel", "📧 Job Scheduler"
])

with tab1:
    render_overview_tab(unified_all, cfg, start_d, end_d)

with tab2:
    render_grid_tab(grid_raw, start_d, end_d)

with tab3:
    render_solar_tab(solar_raw, cfg, start_d, end_d)

with tab4:
    render_diesel_tab(diesel_raw, start_d, end_d)

with tab5:
    render_scheduler_tab(cfg, PROJECT_ROOT)

"""
Dashboard module — __init__.py
Contains the Streamlit page renderers for each tab.
"""

from dashboard.overview import render_overview_tab
from dashboard.grid_tab import render_grid_tab
from dashboard.solar_tab import render_solar_tab
from dashboard.diesel_tab import render_diesel_tab

__all__ = [
    "render_overview_tab",
    "render_grid_tab",
    "render_solar_tab",
    "render_diesel_tab",
]

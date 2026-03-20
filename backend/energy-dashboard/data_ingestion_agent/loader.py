"""
loader.py — Read and validate energy data CSV files (Grid, Solar, Diesel).
Part of the Data Ingestion Agent.
"""

import os
import pandas as pd
import yaml


def _project_root() -> str:
    """Return the energy-dashboard project root."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_config(config_path: str = None) -> dict:
    """Load the application configuration from config.yaml."""
    if config_path is None:
        config_path = os.path.join(_project_root(), "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _resolve_path(relative_path: str) -> str:
    """Resolve a path relative to the project root."""
    return os.path.join(_project_root(), relative_path)


def load_grid_data(config: dict) -> pd.DataFrame:
    """Load and validate Grid data CSV (no solar column)."""
    path = _resolve_path(config["data"]["grid_file"])
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    numeric_cols = [
        "Grid Units Consumed (KWh)",
        "Total Units Consumed (KWh)",
        "Total Units Consumed in INR",
        "Energy Saving in INR",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    # Keep "Ambient Temperature °C" as string (range format e.g. "9-29")
    return df


def load_solar_data(config: dict) -> pd.DataFrame:
    """Load and validate Solar data CSV."""
    path = _resolve_path(config["data"]["solar_file"])
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    numeric_cols = [
        "Solar Units Generated (KWh)", "SMB1 (KWh)", "SMB2 (KWh)",
        "SMB3 (KWh)", "SMB4 (KWh)", "SMB5 (KWh)",
        "Plant Capacity (KW)", "Irradiance (W/m²)",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def load_diesel_data(config: dict) -> pd.DataFrame:
    """Load and validate Diesel data CSV."""
    path = _resolve_path(config["data"]["diesel_file"])
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    numeric_cols = [
        "DG Units Consumed (KWh)", "DG Runtime (hrs)",
        "Fuel Consumed (Litres)", "Cost per Unit (INR)", "Total Cost (INR)",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def load_all(config: dict = None):
    """Convenience: load config and all three dataframes."""
    if config is None:
        config = load_config()
    grid = load_grid_data(config)
    solar = load_solar_data(config)
    diesel = load_diesel_data(config)
    return config, grid, solar, diesel

"""
loader.py — Read and validate energy data CSV files (Grid, Solar, Diesel).
Part of the Data Ingestion Agent.
"""

import os
import io
import pandas as pd
import yaml
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from urllib.request import urlopen


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


def _is_url(path_or_url: str) -> bool:
    return isinstance(path_or_url, str) and path_or_url.startswith(("http://", "https://"))


def _sharepoint_candidate_urls(url: str) -> list[str]:
    """Build candidate URLs for anonymous SharePoint CSV download."""
    candidates = [url]
    if "sharepoint.com" not in url.lower():
        return candidates

    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))

    q1 = dict(query)
    q1["download"] = "1"
    candidates.append(urlunparse(parsed._replace(query=urlencode(q1))))

    q2 = dict(q1)
    q2.pop("web", None)
    candidates.append(urlunparse(parsed._replace(query=urlencode(q2))))

    # Preserve order and remove duplicates.
    return list(dict.fromkeys(candidates))


def _read_csv_from_url(url: str) -> pd.DataFrame:
    with urlopen(url, timeout=60) as response:
        content = response.read()
    return pd.read_csv(io.BytesIO(content))


def _read_local_grid_csv(path: str) -> pd.DataFrame:
    """Read local grid source; supports pointer files containing a URL on line 1."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        first_line = f.readline().strip()

    if _is_url(first_line):
        last_err = None
        for candidate in _sharepoint_candidate_urls(first_line):
            try:
                return _read_csv_from_url(candidate)
            except Exception as err:
                last_err = err
        raise RuntimeError(f"Pointer URL in {os.path.basename(path)} failed: {last_err}")

    return pd.read_csv(path)


def load_grid_data(config: dict) -> pd.DataFrame:
    """Load and validate Grid data CSV (no solar column)."""
    data_cfg = config.get("data", {})
    source = data_cfg.get("grid_file", "./data/grid_data.csv")
    fallback = data_cfg.get("grid_file_fallback", "./data/grid_data_fallback.csv")

    try:
        if _is_url(source):
            df = None
            last_err = None
            for candidate in _sharepoint_candidate_urls(source):
                try:
                    df = _read_csv_from_url(candidate)
                    break
                except Exception as err:
                    last_err = err
            if df is None:
                raise RuntimeError(f"Remote grid URL failed: {last_err}")
        else:
            df = _read_local_grid_csv(_resolve_path(source))
    except Exception as err:
        print(f"[WARN] Grid source failed ({err}). Falling back to {fallback}")
        df = pd.read_csv(_resolve_path(fallback))

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

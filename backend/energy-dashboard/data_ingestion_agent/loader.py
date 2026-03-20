"""
loader.py — Read and validate energy data CSV files (Grid, Solar, Diesel).
Part of the Data Ingestion Agent.
"""

import os
import io
import pandas as pd
import yaml
import requests
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse


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


def _read_grid_source(path_or_url: str, source_format: str = None) -> pd.DataFrame:
    """Read grid source from local path or remote URL supporting CSV/Excel."""
    fmt = (source_format or "").strip().lower()
    is_url = _is_url(path_or_url)

    if is_url:
        candidate_urls = [path_or_url]

        # For SharePoint links, try anonymous-friendly download URL variations.
        if "sharepoint.com" in path_or_url.lower():
            parsed = urlparse(path_or_url)
            query = dict(parse_qsl(parsed.query, keep_blank_values=True))
            if query.get("download") != "1":
                q = dict(query)
                q["download"] = "1"
                candidate_urls.append(urlunparse(parsed._replace(query=urlencode(q))))

            # Some links work better with web=1 removed and download=1 set.
            if "web" in query:
                q = dict(query)
                q.pop("web", None)
                q["download"] = "1"
                candidate_urls.append(urlunparse(parsed._replace(query=urlencode(q))))

        last_error = None
        for candidate in dict.fromkeys(candidate_urls):
            try:
                response = requests.get(candidate, timeout=60)
                response.raise_for_status()
                content = response.content

                if fmt == "excel" or fmt == "xlsx":
                    return pd.read_excel(io.BytesIO(content))
                if fmt == "csv":
                    return pd.read_csv(io.BytesIO(content))

                # Auto-detect by URL token or fallback to Excel first.
                lower_url = candidate.lower()
                if "xlsx" in lower_url or "isspofile=1" in lower_url or ":x:" in lower_url:
                    return pd.read_excel(io.BytesIO(content))
                try:
                    return pd.read_excel(io.BytesIO(content))
                except Exception:
                    return pd.read_csv(io.BytesIO(content))
            except Exception as err:
                last_error = err
                continue

        raise RuntimeError(f"Unable to fetch grid source URL without credentials: {last_error}")

    # Local file path
    resolved = _resolve_path(path_or_url)
    if fmt == "excel" or fmt == "xlsx":
        return pd.read_excel(resolved)
    if fmt == "csv":
        return pd.read_csv(resolved)
    if resolved.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(resolved)
    return pd.read_csv(resolved)


def load_grid_data(config: dict) -> pd.DataFrame:
    """Load and validate Grid data CSV (no solar column)."""
    data_cfg = config.get("data", {})
    source = data_cfg.get("grid_file")
    source_format = data_cfg.get("grid_file_format")
    try:
        df = _read_grid_source(source, source_format)
    except Exception as err:
        fallback = data_cfg.get("grid_file_fallback", "./data/grid_data.csv")
        print(f"[WARN] Remote grid source failed ({err}). Falling back to {fallback}")
        df = _read_grid_source(fallback, "csv")
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

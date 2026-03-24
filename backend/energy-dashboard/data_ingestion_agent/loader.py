"""
loader.py — Read and validate energy data CSV files (Grid, Solar, Diesel).
Part of the Data Ingestion Agent.
"""

import os
import io
import re
import pandas as pd
import yaml
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from urllib.request import urlopen, Request
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))


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


def _history_dir() -> str:
    """Directory for rolling historical snapshots used by dashboard/email."""
    path = os.path.join(_project_root(), "output", "history")
    os.makedirs(path, exist_ok=True)
    return path


def _history_file(dataset_name: str) -> str:
    return os.path.join(_history_dir(), f"{dataset_name}_history.csv")


def _merge_and_keep_last_n_days(dataset_name: str, new_df: pd.DataFrame, keep_days: int = 7) -> pd.DataFrame:
    """Persist incoming rows and return a deduped rolling window of the latest N dates."""
    if new_df is None or len(new_df) == 0:
        return new_df

    df = new_df.copy()
    if "Date" not in df.columns:
        return df

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df[df["Date"].notna()].copy()
    if df.empty:
        return df

    if "Day" not in df.columns:
        df["Day"] = df["Date"].dt.day_name()
    if "Time" not in df.columns:
        df["Time"] = "09:00"

    df = _normalize_day_and_time_columns(df)

    history_path = _history_file(dataset_name)
    if os.path.exists(history_path):
        try:
            old_df = pd.read_csv(history_path)
            if "Date" in old_df.columns:
                old_df["Date"] = pd.to_datetime(old_df["Date"], errors="coerce")
                old_df = old_df[old_df["Date"].notna()].copy()
                if "Day" not in old_df.columns:
                    old_df["Day"] = old_df["Date"].dt.day_name()
                if "Time" not in old_df.columns:
                    old_df["Time"] = "09:00"
                old_df = _normalize_day_and_time_columns(old_df)
                merged = pd.concat([old_df, df], ignore_index=True, sort=False)
            else:
                merged = df
        except Exception:
            merged = df
    else:
        merged = df

    merged["Date"] = pd.to_datetime(merged["Date"], errors="coerce")
    merged = merged[merged["Date"].notna()].copy()
    merged = _normalize_day_and_time_columns(merged)

    dedupe_keys = [k for k in ["Date", "Time"] if k in merged.columns]
    if dedupe_keys:
        merged = merged.sort_values(["Date", "Time"] if "Time" in merged.columns else ["Date"])
        merged = merged.drop_duplicates(subset=dedupe_keys, keep="last")

    unique_dates = sorted(merged["Date"].dt.normalize().dropna().unique())
    keep_set = set(unique_dates[-keep_days:]) if unique_dates else set()
    if keep_set:
        merged = merged[merged["Date"].dt.normalize().isin(keep_set)].copy()

    merged = merged.sort_values(["Date", "Time"] if "Time" in merged.columns else ["Date"]).reset_index(drop=True)

    save_df = merged.copy()
    save_df["Date"] = save_df["Date"].dt.strftime("%Y-%m-%d")
    save_df.to_csv(history_path, index=False)

    merged["Date"] = merged["Date"].dt.date
    return merged


def _is_url(path_or_url: str) -> bool:
    return isinstance(path_or_url, str) and path_or_url.startswith(("http://", "https://"))


def _sharepoint_candidate_urls(url: str) -> list[str]:
    """Build candidate URLs for SharePoint and Google Sheets CSV download."""
    candidates = [url]
    lower = url.lower()

    if "docs.google.com" in lower and "/spreadsheets/" in lower:
        parsed = urlparse(url)
        parts = [p for p in parsed.path.split("/") if p]
        sheet_id = None
        if "d" in parts:
            idx = parts.index("d")
            if idx + 1 < len(parts):
                sheet_id = parts[idx + 1]

        if sheet_id:
            query = dict(parse_qsl(parsed.query, keep_blank_values=True))
            gid = query.get("gid")
            export_base = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export"
            google_candidates = [f"{export_base}?format=csv"]
            if gid:
                google_candidates.append(f"{export_base}?format=csv&gid={gid}")

            # For Google Sheets, prioritize direct export endpoints over edit/view URLs.
            candidates = google_candidates + candidates

        return list(dict.fromkeys(candidates))

    if "sharepoint.com" not in lower:
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


def _auth_header_candidates() -> list[dict]:
    """Build request header candidates for public, bearer-token and cookie flows."""
    mode = os.getenv("GRID_DATA_AUTH_MODE", "auto").strip().lower()
    bearer_token = os.getenv("GRID_DATA_BEARER_TOKEN", "").strip()
    cookie = os.getenv("GRID_DATA_COOKIE", "").strip()
    user_agent = os.getenv("GRID_DATA_USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)").strip()

    public_headers = {"User-Agent": user_agent}
    bearer_headers = {"User-Agent": user_agent, "Authorization": f"Bearer {bearer_token}"} if bearer_token else None
    cookie_headers = {"User-Agent": user_agent, "Cookie": cookie} if cookie else None

    if mode == "none":
        return [public_headers]
    if mode == "bearer":
        return [h for h in [bearer_headers, public_headers] if h]
    if mode == "cookie":
        return [h for h in [cookie_headers, public_headers] if h]
    if mode == "both":
        combo = {
            "User-Agent": user_agent,
            "Authorization": f"Bearer {bearer_token}",
            "Cookie": cookie,
        } if bearer_token and cookie else None
        return [h for h in [combo, bearer_headers, cookie_headers, public_headers] if h]

    # auto mode
    return [h for h in [public_headers, bearer_headers, cookie_headers] if h]


def _read_csv_from_url(url: str, headers: dict | None = None) -> pd.DataFrame:
    req = Request(url, headers=headers or {})
    with urlopen(req, timeout=60) as response:
        content = response.read()
    return pd.read_csv(io.BytesIO(content))


def _read_local_grid_csv(path: str) -> pd.DataFrame:
    """Read local grid source; supports pointer files containing a URL on line 1."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        first_line = f.readline().strip()

    if _is_url(first_line):
        last_err = None
        for candidate in _sharepoint_candidate_urls(first_line):
            for headers in _auth_header_candidates():
                try:
                    return _read_csv_from_url(candidate, headers=headers)
                except Exception as err:
                    last_err = err
        raise RuntimeError(f"Pointer URL in {os.path.basename(path)} failed: {last_err}")

    return pd.read_csv(path)


def _normalize_day_and_time_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize day/time text so cross-source merge keys are consistent."""
    if "Day" in df.columns:
        df["Day"] = df["Day"].astype(str).str.strip().str.title()

    if "Time" in df.columns:
        # Handle values like "9:00", "09:00", "9:00:00", etc.
        time_text = df["Time"].astype(str).str.strip()
        normalized = pd.to_datetime(time_text, format="%H:%M", errors="coerce")
        needs_seconds = normalized.isna()
        if needs_seconds.any():
            normalized_seconds = pd.to_datetime(
                time_text[needs_seconds],
                format="%H:%M:%S",
                errors="coerce",
            )
            normalized.loc[needs_seconds] = normalized_seconds

        parsed = normalized.dt.strftime("%H:%M")
        # Keep original text for rows that cannot be parsed, after trimming.
        df["Time"] = parsed.fillna(time_text)

    return df


def _extract_numeric(value) -> float:
    """Extract a numeric value from strings like '11 Liter' or return 0 for blanks."""
    if pd.isna(value):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()
    if not text:
        return 0.0

    match = re.search(r"[-+]?\d*\.?\d+", text)
    return float(match.group(0)) if match else 0.0


def _has_required_columns(df: pd.DataFrame, required_columns: list[str]) -> bool:
    return all(col in df.columns for col in required_columns)


def _normalize_solar_generation_scale(df: pd.DataFrame, kwh_col: str, wh_col: str) -> pd.DataFrame:
    """
    Normalize inconsistent generation scale from external sheets.

    Some external sheets provide both a small decimal kWh column (e.g. 0.991)
    and a larger interval column labeled Wh (e.g. 991) that aligns with existing
    dashboard KPI expectations. If that pattern is detected, we use the interval
    values directly as Solar Units Generated (KWh) for compatibility.
    """
    if kwh_col not in df.columns or wh_col not in df.columns:
        return df

    kwh_vals = pd.to_numeric(df[kwh_col], errors="coerce")
    wh_vals = pd.to_numeric(df[wh_col], errors="coerce")

    if kwh_vals.notna().sum() == 0 or wh_vals.notna().sum() == 0:
        return df

    max_kwh = float(kwh_vals.max()) if pd.notna(kwh_vals.max()) else 0.0
    max_wh = float(wh_vals.max()) if pd.notna(wh_vals.max()) else 0.0

    # Heuristic for current datasource format: 0.xxx vs 100-1000 scale.
    if max_kwh <= 5 and max_wh >= 50:
        df[kwh_col] = wh_vals

    return df


def _read_remote_table(source: str, required_columns: list[str]) -> pd.DataFrame:
    """Read a remote CSV-like source URL with fallback URL candidates."""
    df = None
    last_err = None
    for candidate in _sharepoint_candidate_urls(source):
        for headers in _auth_header_candidates():
            try:
                candidate_df = _read_csv_from_url(candidate, headers=headers)
                if _has_required_columns(candidate_df, required_columns):
                    df = candidate_df
                    break
            except Exception as err:
                last_err = err
        if df is not None:
            break

    if df is None:
        raise RuntimeError(f"Remote table load failed: {last_err}")
    return df


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
                for headers in _auth_header_candidates():
                    try:
                        candidate_df = _read_csv_from_url(candidate, headers=headers)
                        if _has_required_columns(candidate_df, ["Date", "Day", "Time"]):
                            df = candidate_df
                            break
                    except Exception as err:
                        last_err = err
                if df is not None:
                    break
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
    df = _normalize_day_and_time_columns(df)
    return _merge_and_keep_last_n_days("grid", df, keep_days=7)


def load_solar_data(config: dict) -> pd.DataFrame:
    """Load and validate Solar data, supporting remote unified + SMB status sources."""
    data_cfg = config.get("data", {})
    source = data_cfg.get("solar_file", "./data/solar_data.csv")
    smb_source = data_cfg.get("solar_smb_status_file", "")

    # Remote unified solar source flow.
    if _is_url(source):
        try:
            df = _read_remote_table(source, ["Date"])

            # Map new unified solar sheet format to the dashboard contract.
            if (
                "Solar Units Generated (KWh)" not in df.columns
                and (
                    "Daily Generation Solar (kWh)" in df.columns
                    or "Generation Interval (kWh)" in df.columns
                )
            ):
                solar_col = (
                    "Daily Generation Solar (kWh)"
                    if "Daily Generation Solar (kWh)" in df.columns
                    else "Generation Interval (kWh)"
                )
                df["Solar Units Generated (KWh)"] = pd.to_numeric(df[solar_col], errors="coerce").fillna(0)

            # Correct for inconsistent unit labeling in the provided sheet.
            if "Generation Interval (Wh)" in df.columns and "Solar Units Generated (KWh)" in df.columns:
                df = _normalize_solar_generation_scale(
                    df,
                    kwh_col="Solar Units Generated (KWh)",
                    wh_col="Generation Interval (Wh)",
                )

            df["Date"] = pd.to_datetime(df["Date"]).dt.date
            df["Day"] = pd.to_datetime(df["Date"]).dt.day_name()

            # Align with grid merge key (grid data is daily at 09:00).
            df["Time"] = "09:00"

            smb_values = {f"SMB{i} (KWh)": 0.0 for i in range(1, 6)}
            inverter_status = "All Online"

            # Merge SMB inverter status snapshot source.
            if _is_url(smb_source):
                try:
                    smb_df = _read_remote_table(smb_source, ["SMB", "Status"])
                    faulted = []

                    for _, smb_row in smb_df.iterrows():
                        smb_name = str(smb_row.get("SMB", "")).strip().upper().replace("_", "")
                        status = str(smb_row.get("Status", "")).strip().upper()

                        if smb_name.startswith("SMB") and smb_name[3:].isdigit():
                            idx = smb_name[3:]
                            key = f"SMB{idx} (KWh)"
                            if key in smb_values:
                                if "Power Output (kW)" in smb_df.columns:
                                    smb_values[key] = _extract_numeric(smb_row.get("Power Output (kW)"))
                                else:
                                    smb_values[key] = _extract_numeric(smb_row.get("Power Output (W)")) / 1000.0

                            if status not in {"ACTIVE", "ON", "ONLINE", "ALL ONLINE"}:
                                faulted.append(f"SMB{idx}")

                    if faulted:
                        inverter_status = ", ".join(f"{name} Fault" for name in faulted)
                except Exception:
                    # Keep default status/SMB values if SMB source is unavailable.
                    pass

            df["Inverter Status"] = inverter_status
            for smb_col, smb_val in smb_values.items():
                df[smb_col] = smb_val

            if "Irradiance (W/m²)" not in df.columns:
                df["Irradiance (W/m²)"] = 0
            # Keep plant capacity static for dashboard display.
            df["Plant Capacity (KW)"] = 598.60

            selected_cols = [
                "Date", "Day", "Time", "Solar Units Generated (KWh)",
                "Inverter Status", "SMB1 (KWh)", "SMB2 (KWh)",
                "SMB3 (KWh)", "SMB4 (KWh)", "SMB5 (KWh)",
                "Plant Capacity (KW)", "Irradiance (W/m²)",
            ]
            df = df[selected_cols].copy()

            numeric_cols = [
                "Solar Units Generated (KWh)", "SMB1 (KWh)", "SMB2 (KWh)",
                "SMB3 (KWh)", "SMB4 (KWh)", "SMB5 (KWh)",
                "Plant Capacity (KW)", "Irradiance (W/m²)",
            ]
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

            df = _normalize_day_and_time_columns(df)
            return _merge_and_keep_last_n_days("solar", df, keep_days=7)
        except Exception as err:
            print(f"[WARN] Solar source failed ({err}). Falling back to local solar file.")

    # Local fallback flow.
    path = _resolve_path(source)
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
    df = _normalize_day_and_time_columns(df)
    return _merge_and_keep_last_n_days("solar", df, keep_days=7)


def load_solar_last7_data(config: dict) -> pd.DataFrame:
    """Load static last-7-days solar table used for solar tab metrics/trend."""
    data_cfg = config.get("data", {})
    source = data_cfg.get("solar_last7_file", "")

    if _is_url(source):
        try:
            df = _read_remote_table(source, ["Date"])
            df["Date"] = pd.to_datetime(df["Date"]).dt.date

            if "Day" not in df.columns:
                df["Day"] = pd.to_datetime(df["Date"]).dt.day_name()
            if "Time" not in df.columns:
                df["Time"] = "09:00"

            if "Generation (kWh)" not in df.columns and "Generation Interval (kWh)" in df.columns:
                df["Generation (kWh)"] = pd.to_numeric(df["Generation Interval (kWh)"], errors="coerce")

            if "Generation (kWh)" in df.columns and "Generation (Wh)" in df.columns:
                df = _normalize_solar_generation_scale(
                    df,
                    kwh_col="Generation (kWh)",
                    wh_col="Generation (Wh)",
                )

            for col in ["Generation (Wh)", "Generation (kWh)", "Start Value", "End Value"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            df = _normalize_day_and_time_columns(df)
            return df
        except Exception as err:
            print(f"[WARN] Solar last7 source failed ({err}). Falling back to solar dataset.")

    fallback = load_solar_data(config)
    fallback = fallback[["Date", "Day", "Time", "Solar Units Generated (KWh)"]].copy()
    fallback.rename(columns={"Solar Units Generated (KWh)": "Generation (kWh)"}, inplace=True)
    fallback["Generation (Wh)"] = fallback["Generation (kWh)"] * 1000
    fallback = fallback.sort_values(["Date", "Time"], ascending=[False, True]).head(7)
    return fallback


def load_diesel_data(config: dict) -> pd.DataFrame:
    """Load diesel data from grid source column when available; fallback to diesel CSV."""
    data_cfg = config.get("data", {})
    source = data_cfg.get("grid_file", "./data/grid_data.csv")
    fallback = data_cfg.get("diesel_file", "./data/diesel_data.csv")
    diesel_rate = float(config.get("costs", {}).get("diesel_per_unit_inr", 30.0))

    try:
        if _is_url(source):
            source_df = None
            last_err = None
            for candidate in _sharepoint_candidate_urls(source):
                for headers in _auth_header_candidates():
                    try:
                        candidate_df = _read_csv_from_url(candidate, headers=headers)
                        if _has_required_columns(candidate_df, ["Date", "Day", "Time"]):
                            source_df = candidate_df
                            break
                    except Exception as err:
                        last_err = err
                if source_df is not None:
                    break
            if source_df is None:
                raise RuntimeError(f"Remote diesel source via grid_file failed: {last_err}")
        else:
            source_df = _read_local_grid_csv(_resolve_path(source))

        normalized_cols = {str(c).strip().lower(): c for c in source_df.columns}
        diesel_col = normalized_cols.get("diesel_consumed") or normalized_cols.get("diesel consumed")

        required = ["Date", "Day", "Time"]
        if diesel_col and all(col in source_df.columns for col in required):
            df = source_df[required + [diesel_col]].copy()
            df.rename(columns={diesel_col: "Diesel consumed"}, inplace=True)
            df["Diesel consumed"] = df["Diesel consumed"].apply(_extract_numeric)
            df["DG Units Consumed (KWh)"] = df["Diesel consumed"]
            df["DG Runtime (hrs)"] = 0.0
            df["Cost per Unit (INR)"] = diesel_rate
            df["Total Cost (INR)"] = df["Diesel consumed"] * diesel_rate
            df["DG ID"] = "DG1"
            df["Date"] = pd.to_datetime(df["Date"]).dt.date

            numeric_cols = [
                "DG Units Consumed (KWh)", "DG Runtime (hrs)",
                "Diesel consumed", "Cost per Unit (INR)", "Total Cost (INR)",
            ]
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

            df = _normalize_day_and_time_columns(df)
            return _merge_and_keep_last_n_days("diesel", df, keep_days=7)
    except Exception as err:
        print(f"[WARN] Diesel source from grid_file failed ({err}). Falling back to {fallback}")

    path = _resolve_path(fallback)
    if os.path.exists(path):
        df = pd.read_csv(path)
        if "Fuel Consumed (Litres)" in df.columns and "Diesel consumed" not in df.columns:
            df.rename(columns={"Fuel Consumed (Litres)": "Diesel consumed"}, inplace=True)
        df["Date"] = pd.to_datetime(df["Date"]).dt.date
        numeric_cols = [
            "DG Units Consumed (KWh)", "DG Runtime (hrs)",
            "Diesel consumed", "Cost per Unit (INR)", "Total Cost (INR)",
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        df = _normalize_day_and_time_columns(df)
        return _merge_and_keep_last_n_days("diesel", df, keep_days=7)

    # Last-resort fallback: return zero-diesel rows aligned to grid keys.
    print(f"[WARN] Diesel fallback file not found at {path}. Using zero diesel values.")
    try:
        grid_df = load_grid_data(config)
        required = ["Date", "Day", "Time"]
        if all(col in grid_df.columns for col in required):
            df = grid_df[required].copy()
        else:
            df = pd.DataFrame(columns=required)
    except Exception:
        df = pd.DataFrame(columns=["Date", "Day", "Time"])

    df["DG Units Consumed (KWh)"] = 0.0
    df["DG Runtime (hrs)"] = 0.0
    df["Diesel consumed"] = 0.0
    df["Cost per Unit (INR)"] = diesel_rate
    df["Total Cost (INR)"] = 0.0
    df["DG ID"] = "DG1"

    if "Date" in df.columns and not df.empty:
        df["Date"] = pd.to_datetime(df["Date"]).dt.date

    df = _normalize_day_and_time_columns(df)
    return _merge_and_keep_last_n_days("diesel", df, keep_days=7)


def load_all(config: dict = None):
    """Convenience: load config and all three dataframes."""
    if config is None:
        config = load_config()
    grid = load_grid_data(config)
    solar = load_solar_data(config)
    diesel = load_diesel_data(config)
    return config, grid, solar, diesel

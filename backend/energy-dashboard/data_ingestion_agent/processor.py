"""
processor.py — Merge the three data sources into a unified model and compute derived metrics.
Part of the Data Ingestion Agent.
"""

import pandas as pd


def build_unified_dataframe(grid: pd.DataFrame, solar: pd.DataFrame, diesel: pd.DataFrame) -> pd.DataFrame:
    """
    Merge grid, solar and diesel data on Date + Time into a single
    master DataFrame with all derived columns.
    """
    # ── Grid: rename to unified names ──
    g = grid.copy()
    g.rename(columns={
        "Ambient Temperature °C": "Ambient Temp (°C)",
        "Grid Units Consumed (KWh)": "Grid KWh",
        "Total Units Consumed (KWh)": "Grid Total KWh",
        "Total Units Consumed in INR": "Grid Cost (INR)",
        "Energy Saving in INR": "Grid Energy Saving (INR)",
    }, inplace=True)
    # Diesel is sourced through the diesel dataframe; avoid duplicate raw sheet columns.
    g.drop(columns=["diesel_consumed", "Diesel consumed"], errors="ignore", inplace=True)

    # ── Solar: rename ──
    s = solar[["Date", "Day", "Time", "Solar Units Generated (KWh)",
               "Inverter Status", "SMB1 (KWh)", "SMB2 (KWh)",
               "SMB3 (KWh)", "SMB4 (KWh)", "SMB5 (KWh)",
               "Irradiance (W/m²)"]].copy()
    s.rename(columns={"Day": "Solar Day"}, inplace=True)
    s.rename(columns={
        "Solar Units Generated (KWh)": "Solar KWh",
    }, inplace=True)

    # ── Diesel: normalize/rename ──
    d = diesel.copy()
    if "Fuel Consumed (Litres)" in d.columns and "Diesel consumed" not in d.columns:
        d.rename(columns={"Fuel Consumed (Litres)": "Diesel consumed"}, inplace=True)
    if "Diesel consumed" not in d.columns:
        d["Diesel consumed"] = 0.0

    d = d[["Date", "Day", "Time", "DG Units Consumed (KWh)",
           "DG Runtime (hrs)", "Diesel consumed",
           "Total Cost (INR)", "DG ID"]].copy()
    d.rename(columns={
        "Day": "Diesel Day",
        "DG Units Consumed (KWh)": "Diesel KWh",
        "Total Cost (INR)": "Diesel Cost (INR)",
    }, inplace=True)

    # ── Merge on Date + Time key ──
    merged = g.merge(s, on=["Date", "Time"], how="outer")
    merged = merged.merge(d, on=["Date", "Time"], how="outer")

    # Resolve day label from available sources.
    if "Day" not in merged.columns:
        merged["Day"] = None
    if "Solar Day" in merged.columns:
        merged["Day"] = merged["Day"].fillna(merged["Solar Day"])
    if "Diesel Day" in merged.columns:
        merged["Day"] = merged["Day"].fillna(merged["Diesel Day"])
    merged.drop(columns=["Solar Day", "Diesel Day"], errors="ignore", inplace=True)

    # Fill NaN numerics with 0
    num_fill = ["Grid KWh", "Solar KWh", "Diesel KWh",
                "Grid Cost (INR)", "Diesel Cost (INR)",
                "Grid Energy Saving (INR)"]
    for col in num_fill:
        if col in merged.columns:
            merged[col] = merged[col].fillna(0)

    # ── Derived columns ──
    # Total consumption for dashboard/email KPIs should reflect grid + solar only.
    merged["Total KWh"] = merged["Grid KWh"] + merged["Solar KWh"]
    grid_rate = 7.11
    solar_rate = 1.50
    merged["Solar Cost (INR)"] = merged["Solar KWh"] * solar_rate
    merged["Total Cost (INR)"] = merged["Grid Cost (INR)"] + merged["Diesel Cost (INR)"] + merged["Solar Cost (INR)"]
    merged["Energy Saving (INR)"] = merged["Solar KWh"] * (grid_rate - solar_rate)
    merged["Solar %"] = ((merged["Solar KWh"] / merged["Total KWh"]) * 100).round(1).fillna(0)

    # Source label
    def _source(row):
        parts = []
        if row.get("Grid KWh", 0) > 0:
            parts.append("Grid")
        if row.get("Solar KWh", 0) > 0:
            parts.append("Solar")
        if row.get("Diesel KWh", 0) > 0:
            parts.append("Diesel")
        return " + ".join(parts) if parts else "None"
    merged["Source"] = merged.apply(_source, axis=1)

    merged = merged.sort_values(["Date", "Time"], ascending=[False, True]).reset_index(drop=True)
    return merged


def compute_daily_summary(unified: pd.DataFrame) -> pd.DataFrame:
    """Aggregate the unified data by date."""
    daily = unified.groupby("Date").agg({
        "Grid KWh": "sum",
        "Solar KWh": "sum",
        "Diesel KWh": "sum",
        "Total KWh": "sum",
        "Grid Cost (INR)": "sum",
        "Diesel Cost (INR)": "sum",
        "Total Cost (INR)": "sum",
        "Energy Saving (INR)": "sum",
        "Ambient Temp (°C)": "first",
    }).reset_index()
    daily["Solar %"] = ((daily["Solar KWh"] / daily["Total KWh"]) * 100).round(1).fillna(0)
    daily = daily.sort_values("Date").reset_index(drop=True)
    return daily


def compute_overview_kpis(unified: pd.DataFrame, config: dict) -> dict:
    """Compute the six overview KPI values."""
    total_kwh = unified["Total KWh"].sum()
    solar_kwh = unified["Solar KWh"].sum()
    solar_pct = round((solar_kwh / total_kwh * 100), 1) if total_kwh > 0 else 0.0
    total_cost = unified["Total Cost (INR)"].sum()
    energy_saved = unified["Energy Saving (INR)"].sum()
    avg_temp_raw = unified["Ambient Temp (°C)"].dropna()
    # Temp is a range string like "11-31" or "9-29"; compute average of low and high
    def _parse_temp_avg(val):
        try:
            if isinstance(val, str):
                # Handle range format e.g. "9-29", "11-31", "12-37"
                val = val.strip()
                if "-" in val:
                    parts = [p.strip() for p in val.split("-") if p.strip()]
                    if len(parts) == 2:
                        return (float(parts[0]) + float(parts[1])) / 2
                    elif len(parts) == 1:
                        return float(parts[0])
            return float(val)
        except (ValueError, TypeError):
            return None

    temps = avg_temp_raw.apply(_parse_temp_avg).dropna()
    avg_temp = temps.mean() if len(temps) > 0 else 0.0

    # Day-over-day deltas
    dates = sorted(unified["Date"].unique())
    if len(dates) >= 2:
        last_day = unified[unified["Date"] == dates[-1]]
        prev_day = unified[unified["Date"] == dates[-2]]
        delta_kwh = last_day["Total KWh"].sum() - prev_day["Total KWh"].sum()
        l_total = last_day["Total KWh"].sum()
        p_total = prev_day["Total KWh"].sum()
        delta_solar_pct = (
            round((last_day["Solar KWh"].sum() / l_total * 100), 1) if l_total > 0 else 0
        ) - (
            round((prev_day["Solar KWh"].sum() / p_total * 100), 1) if p_total > 0 else 0
        )
        delta_cost = last_day["Total Cost (INR)"].sum() - prev_day["Total Cost (INR)"].sum()
    else:
        delta_kwh = delta_solar_pct = delta_cost = None

    solar_target = config.get("solar", {}).get("daily_target_kwh", 3000)
    n_days = max(len(dates), 1)
    delta_solar_gen = round(solar_kwh - solar_target * n_days, 1)

    return {
        "total_kwh": round(total_kwh, 1),
        "solar_kwh": round(solar_kwh, 1),
        "solar_pct": solar_pct,
        "total_cost": round(total_cost, 0),
        "energy_saved": round(energy_saved, 0),
        "avg_temp": round(avg_temp, 1),
        "delta_kwh": round(delta_kwh, 1) if delta_kwh is not None else None,
        "delta_solar_pct": delta_solar_pct,
        "delta_cost": round(delta_cost, 0) if delta_cost is not None else None,
        "delta_solar_gen": delta_solar_gen,
    }

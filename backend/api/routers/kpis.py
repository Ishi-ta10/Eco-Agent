"""
KPI endpoints router
"""
from fastapi import APIRouter, Query
from typing import Optional
from ..services import data_service
import numpy as np
import json


def convert_numpy_types(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {key: convert_numpy_types(val) for key, val in obj.items()}
    if isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    return obj


router = APIRouter(prefix="/api/kpis", tags=["kpis"])


@router.get("/overview")
async def get_overview_kpis(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get overview KPIs with deltas"""
    kpis = data_service.compute_overview_kpis(start_date, end_date)
    return convert_numpy_types(kpis)


@router.get("/grid")
async def get_grid_kpis(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get grid-specific KPIs"""
    # Compute from grid data
    grid_data = data_service.load_grid_data(start_date, end_date)
    data = grid_data["data"]

    if not data:
        return {
            "total_grid_kwh": 0,
            "avg_grid_kwh": 0,
            "peak_grid_kwh": 0,
            "total_grid_cost": 0
        }

    import pandas as pd
    df = pd.DataFrame(data)

    result = {
        "total_grid_kwh": float(df['Grid Units Consumed (KWh)'].sum()),
        "avg_grid_kwh": float(df['Grid Units Consumed (KWh)'].mean()),
        "peak_grid_kwh": float(df['Grid Units Consumed (KWh)'].max()),
        "total_grid_cost": float(df['Total Units Consumed in INR'].sum())
    }
    return result


@router.get("/solar")
async def get_solar_kpis(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get solar-specific KPIs with inverter status."""
    # Respect selected dashboard date filter, similar to Grid/Diesel tabs.
    solar_data = data_service.load_solar_data(start_date, end_date)
    data = solar_data["data"]

    if not data:
        return {
            "total_solar_kwh": 0,
            "avg_solar_kwh": 0,
            "peak_solar_kwh": 0,
            "solar_target_pct": 25.0,
            "actual_solar_pct": 0,
            "energy_saved": 0,
            "inverter_faults": 0,
            "weekly_trend": [],
        }

    import pandas as pd
    from config import SOLAR_TARGET_PERCENTAGE, GRID_COST_PER_UNIT

    df = pd.DataFrame(data)
    generation_col = "Generation (kWh)" if "Generation (kWh)" in df.columns else "Solar Units Generated (KWh)"

    # Fault count derived from same selected date range.
    solar_status_data = data_service.load_solar_data(start_date, end_date).get("data", [])
    inverter_faults = 0
    if solar_status_data:
        sdf = pd.DataFrame(solar_status_data)
        if "Inverter Status" in sdf.columns:
            inverter_faults = int(len(sdf[sdf["Inverter Status"] != "All Online"]))

    total_solar = float(pd.to_numeric(df[generation_col], errors="coerce").fillna(0).sum())
    energy_saved = float(total_solar * GRID_COST_PER_UNIT)

    if "Date" in df.columns:
        trend_df = df[["Date", generation_col]].copy()
        trend_df["Date"] = pd.to_datetime(trend_df["Date"], errors="coerce")
        trend_df = trend_df.sort_values("Date")
        trend_df["Day"] = trend_df["Date"].dt.day_name()
        trend_df["Date"] = trend_df["Date"].dt.strftime("%Y-%m-%d")
        trend_df["Generation"] = pd.to_numeric(trend_df[generation_col], errors="coerce").fillna(0)
        weekly_trend = trend_df[["Date", "Day", "Generation"]].to_dict("records")
    else:
        weekly_trend = []

    return {
        "total_solar_kwh": total_solar,
        "avg_solar_kwh": float(pd.to_numeric(df[generation_col], errors="coerce").fillna(0).mean()),
        "peak_solar_kwh": float(pd.to_numeric(df[generation_col], errors="coerce").fillna(0).max()),
        "solar_target_pct": float(SOLAR_TARGET_PERCENTAGE),
        "actual_solar_pct": 0.0,  # Would need unified data
        "energy_saved": energy_saved,
        "inverter_faults": inverter_faults,
        "weekly_trend": weekly_trend,
    }


@router.get("/diesel")
async def get_diesel_kpis(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get diesel generator KPIs"""
    diesel_data = data_service.load_diesel_data(start_date, end_date)
    data = diesel_data["data"]

    if not data:
        return {
            "total_diesel_kwh": 0,
            "total_runtime": 0,
            "total_fuel": 0,
            "total_diesel_cost": 0
        }

    import pandas as pd
    df = pd.DataFrame(data)
    fuel_col = 'Diesel consumed' if 'Diesel consumed' in df.columns else 'Fuel Consumed (Litres)'

    return {
        "total_diesel_kwh": float(df['DG Units Consumed (KWh)'].sum()),
        "total_runtime": float(df['DG Runtime (hrs)'].sum()),
        "total_fuel": float(df[fuel_col].sum()),
        "total_diesel_cost": float(df['Total Cost (INR)'].sum())
    }

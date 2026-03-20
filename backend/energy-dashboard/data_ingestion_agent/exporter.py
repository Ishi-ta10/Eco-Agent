"""
exporter.py — Generate .xlsx report attachments.
Part of the Data Ingestion Agent.
"""

import os
import io
from datetime import date

import pandas as pd


def _ensure_output_dir() -> str:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(project_root, "output")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def export_unified_xlsx(unified: pd.DataFrame) -> bytes:
    """Generate the unified energy report as .xlsx bytes."""
    buf = io.BytesIO()
    display_cols = [
        "Date", "Day", "Time", "Ambient Temp (°C)",
        "Grid KWh", "Solar KWh", "Diesel KWh", "Total KWh",
        "Grid Cost (INR)", "Diesel Cost (INR)", "Solar Cost (INR)",
        "Total Cost (INR)", "Energy Saving (INR)", "Solar %", "Source",
    ]
    cols = [c for c in display_cols if c in unified.columns]
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        unified[cols].to_excel(writer, index=False, sheet_name="Unified Report")
    buf.seek(0)
    return buf.getvalue()


def export_grid_xlsx(grid_df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        grid_df.to_excel(writer, index=False, sheet_name="Grid Data")
    buf.seek(0)
    return buf.getvalue()


def export_solar_xlsx(solar_df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        solar_df.to_excel(writer, index=False, sheet_name="Solar Data")
    buf.seek(0)
    return buf.getvalue()


def export_diesel_xlsx(diesel_df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        diesel_df.to_excel(writer, index=False, sheet_name="Diesel Data")
    buf.seek(0)
    return buf.getvalue()


def export_ecs_style_xlsx(unified: pd.DataFrame) -> bytes:
    """
    Generate an Excel report following the Electrical Optimization (1)
    ECS sheet format:
    Date | Day | Time | Ambient Temperature °C | Grid Units Consumed (KWh) |
    Total Units Consumed (KWh) | Total Units Consumed in INR | Energy Saving in INR
    """
    buf = io.BytesIO()
    ecs_df = pd.DataFrame({
        "Date": unified["Date"],
        "Day": unified["Day"],
        "Time": unified["Time"],
        "Ambient Temperature °C": unified.get("Ambient Temp (°C)", ""),
        "Grid Units Consumed (KWh)": unified["Grid KWh"],
        "Total Units Consumed (KWh)": unified["Total KWh"],
        "Total Units Consumed in INR": unified["Total Cost (INR)"],
        "Energy Saving in INR": unified["Energy Saving (INR)"],
    })
    # Append totals row
    totals = pd.DataFrame([{
        "Date": "Total",
        "Day": "",
        "Time": "",
        "Ambient Temperature °C": "",
        "Grid Units Consumed (KWh)": ecs_df["Grid Units Consumed (KWh)"].sum(),
        "Total Units Consumed (KWh)": ecs_df["Total Units Consumed (KWh)"].sum(),
        "Total Units Consumed in INR": ecs_df["Total Units Consumed in INR"].sum(),
        "Energy Saving in INR": ecs_df["Energy Saving in INR"].sum(),
    }])
    ecs_df = pd.concat([ecs_df, totals], ignore_index=True)

    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        ecs_df.to_excel(writer, index=False, sheet_name="ECS")
    buf.seek(0)
    return buf.getvalue()

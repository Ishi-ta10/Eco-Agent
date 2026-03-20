"""
Data service that wraps the data_ingestion_agent functionality
"""
import sys
from pathlib import Path
from typing import Optional, Dict, List, Any
import pandas as pd
from datetime import datetime

# Add the energy-dashboard directory to the path
energy_dashboard_path = Path(__file__).parent.parent.parent / "energy-dashboard"
sys.path.insert(0, str(energy_dashboard_path))

from data_ingestion_agent import loader, processor
from config import DATA_DIR, config


def load_unified_data(start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Load unified energy data with optional date filtering

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Dictionary with data, date_range, and total_records
    """
    # Load all data
    grid_df = loader.load_grid_data(config)
    solar_df = loader.load_solar_data(config)
    diesel_df = loader.load_diesel_data(config)

    # Build unified dataframe
    unified_df = processor.build_unified_dataframe(grid_df, solar_df, diesel_df)

    # Filter by date if provided
    if start_date or end_date:
        unified_df['Date'] = pd.to_datetime(unified_df['Date'])
        if start_date:
            unified_df = unified_df[unified_df['Date'] >= pd.to_datetime(start_date)]
        if end_date:
            unified_df = unified_df[unified_df['Date'] <= pd.to_datetime(end_date)]
        unified_df['Date'] = unified_df['Date'].dt.strftime('%Y-%m-%d')

    # Get date range
    all_dates = pd.to_datetime(unified_df['Date'])
    date_range = {
        "min_date": all_dates.min().strftime('%Y-%m-%d') if len(all_dates) > 0 else None,
        "max_date": all_dates.max().strftime('%Y-%m-%d') if len(all_dates) > 0 else None
    }

    # Convert to dict
    data = unified_df.to_dict('records')

    return {
        "data": data,
        "date_range": date_range,
        "total_records": len(data)
    }


def load_grid_data(start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
    """Load grid data with optional filtering"""
    grid_df = loader.load_grid_data(config)

    # Filter by date if provided
    if start_date or end_date:
        grid_df['Date'] = pd.to_datetime(grid_df['Date'])
        if start_date:
            grid_df = grid_df[grid_df['Date'] >= pd.to_datetime(start_date)]
        if end_date:
            grid_df = grid_df[grid_df['Date'] <= pd.to_datetime(end_date)]
        grid_df['Date'] = grid_df['Date'].dt.strftime('%Y-%m-%d')

    all_dates = pd.to_datetime(grid_df['Date'])
    date_range = {
        "min_date": all_dates.min().strftime('%Y-%m-%d') if len(all_dates) > 0 else None,
        "max_date": all_dates.max().strftime('%Y-%m-%d') if len(all_dates) > 0 else None
    }

    data = grid_df.to_dict('records')

    return {
        "data": data,
        "date_range": date_range,
        "total_records": len(data)
    }


def load_solar_data(start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
    """Load solar data with optional filtering"""
    solar_df = loader.load_solar_data(config)

    # Filter by date if provided
    if start_date or end_date:
        solar_df['Date'] = pd.to_datetime(solar_df['Date'])
        if start_date:
            solar_df = solar_df[solar_df['Date'] >= pd.to_datetime(start_date)]
        if end_date:
            solar_df = solar_df[solar_df['Date'] <= pd.to_datetime(end_date)]
        solar_df['Date'] = solar_df['Date'].dt.strftime('%Y-%m-%d')

    all_dates = pd.to_datetime(solar_df['Date'])
    date_range = {
        "min_date": all_dates.min().strftime('%Y-%m-%d') if len(all_dates) > 0 else None,
        "max_date": all_dates.max().strftime('%Y-%m-%d') if len(all_dates) > 0 else None
    }

    data = solar_df.to_dict('records')

    return {
        "data": data,
        "date_range": date_range,
        "total_records": len(data)
    }


def load_diesel_data(start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
    """Load diesel data with optional filtering"""
    diesel_df = loader.load_diesel_data(config)

    # Filter by date if provided
    if start_date or end_date:
        diesel_df['Date'] = pd.to_datetime(diesel_df['Date'])
        if start_date:
            diesel_df = diesel_df[diesel_df['Date'] >= pd.to_datetime(start_date)]
        if end_date:
            diesel_df = diesel_df[diesel_df['Date'] <= pd.to_datetime(end_date)]
        diesel_df['Date'] = diesel_df['Date'].dt.strftime('%Y-%m-%d')

    all_dates = pd.to_datetime(diesel_df['Date'])
    date_range = {
        "min_date": all_dates.min().strftime('%Y-%m-%d') if len(all_dates) > 0 else None,
        "max_date": all_dates.max().strftime('%Y-%m-%d') if len(all_dates) > 0 else None
    }

    data = diesel_df.to_dict('records')

    return {
        "data": data,
        "date_range": date_range,
        "total_records": len(data)
    }


def load_daily_summary(start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
    """Load daily summary data"""
    # Load all data
    grid_df = loader.load_grid_data(config)
    solar_df = loader.load_solar_data(config)
    diesel_df = loader.load_diesel_data(config)

    # Build unified dataframe
    unified_df = processor.build_unified_dataframe(grid_df, solar_df, diesel_df)

    # Compute daily summary
    daily_df = processor.compute_daily_summary(unified_df)

    # Filter by date if provided
    if start_date or end_date:
        daily_df['Date'] = pd.to_datetime(daily_df['Date'])
        if start_date:
            daily_df = daily_df[daily_df['Date'] >= pd.to_datetime(start_date)]
        if end_date:
            daily_df = daily_df[daily_df['Date'] <= pd.to_datetime(end_date)]
        daily_df['Date'] = daily_df['Date'].dt.strftime('%Y-%m-%d')

    all_dates = pd.to_datetime(daily_df['Date'])
    date_range = {
        "min_date": all_dates.min().strftime('%Y-%m-%d') if len(all_dates) > 0 else None,
        "max_date": all_dates.max().strftime('%Y-%m-%d') if len(all_dates) > 0 else None
    }

    data = daily_df.to_dict('records')

    return {
        "data": data,
        "date_range": date_range,
        "total_records": len(data)
    }


def compute_overview_kpis(start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
    """Compute overview KPIs"""
    # Load all data
    grid_df = loader.load_grid_data(config)
    solar_df = loader.load_solar_data(config)
    diesel_df = loader.load_diesel_data(config)

    # Build unified dataframe
    unified_df = processor.build_unified_dataframe(grid_df, solar_df, diesel_df)

    # Filter by date if provided
    if start_date or end_date:
        unified_df['Date'] = pd.to_datetime(unified_df['Date'])
        if start_date:
            unified_df = unified_df[unified_df['Date'] >= pd.to_datetime(start_date)]
        if end_date:
            unified_df = unified_df[unified_df['Date'] <= pd.to_datetime(end_date)]

    # Compute KPIs - pass config parameter
    kpis = processor.compute_overview_kpis(unified_df, config)

    return kpis

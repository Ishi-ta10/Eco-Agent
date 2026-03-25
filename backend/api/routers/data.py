"""
Data endpoints router
"""
from fastapi import APIRouter, Query
from typing import Optional
from ..services import data_service
from ..schemas.energy import EnergyDataResponse

router = APIRouter(prefix="/api/data", tags=["data"])


@router.get("/unified", response_model=EnergyDataResponse)
async def get_unified_data(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get unified energy data (grid + solar + diesel)"""
    return data_service.load_unified_data(start_date, end_date)


@router.get("/grid", response_model=EnergyDataResponse)
async def get_grid_data(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get grid energy data"""
    return data_service.load_grid_data(start_date, end_date)


@router.get("/solar", response_model=EnergyDataResponse)
async def get_solar_data(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get solar energy data with SMB breakdown"""
    return data_service.load_solar_data(start_date, end_date)


@router.get("/diesel", response_model=EnergyDataResponse)
async def get_diesel_data(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get diesel generator data"""
    return data_service.load_diesel_data(start_date, end_date)


@router.get("/daily-summary", response_model=EnergyDataResponse)
async def get_daily_summary(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get daily aggregated summary"""
    return data_service.load_daily_summary(start_date, end_date)

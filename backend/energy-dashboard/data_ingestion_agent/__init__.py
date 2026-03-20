"""
Data Ingestion Agent — __init__.py
Exposes the public API for loading and validating energy data from CSV/Excel sources.
"""

from data_ingestion_agent.loader import load_config, load_all
from data_ingestion_agent.seed import seed_data_files

__all__ = ["load_config", "load_all", "seed_data_files"]

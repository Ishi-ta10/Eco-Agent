"""
Configuration loader for the Energy Dashboard API.
Loads configuration from energy-dashboard/config.yaml
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any

# Path to the energy-dashboard directory
ENERGY_DASHBOARD_DIR = Path(__file__).parent.parent / "energy-dashboard"
CONFIG_FILE = ENERGY_DASHBOARD_DIR / "config.yaml"
DATA_DIR = ENERGY_DASHBOARD_DIR / "data"


def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml"""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Configuration file not found: {CONFIG_FILE}")

    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)

    return config


# Load configuration once at startup
config = load_config()

# Export commonly used config values
GRID_COST_PER_UNIT = config.get("costs", {}).get("grid_cost_per_unit", 7.11)
SOLAR_COST_PER_UNIT = config.get("costs", {}).get("solar_cost_per_unit", 0.0)
DIESEL_COST_PER_UNIT = config.get("costs", {}).get("diesel_cost_per_unit", 25.0)
SOLAR_TARGET_PERCENTAGE = config.get("targets", {}).get("solar_percentage", 25.0)
EMAIL_CONFIG = config.get("email", {})

"""
scheduler.py — Background scheduler that runs alongside Streamlit.
Uses the `schedule` library in a daemon thread.
Part of the Mail Scheduling Agent.
"""

import schedule
import threading
import time
import json
import os


def _project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_scheduler():
    """Polling loop: checks for pending jobs every 30 seconds."""
    while True:
        schedule.run_pending()
        time.sleep(30)


def start_background_scheduler(send_fn, run_time: str):
    """
    Schedule `send_fn` to run daily at `run_time` (HH:MM format)
    and start the polling loop in a daemon thread.
    """
    schedule.clear()
    schedule.every().day.at(run_time).do(send_fn)
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
    return thread


def stop_scheduler():
    """Clear all scheduled jobs."""
    schedule.clear()


def get_next_run() -> str:
    """Return the next scheduled run time as a string."""
    jobs = schedule.get_jobs()
    if jobs:
        return str(jobs[0].next_run)
    return "No jobs scheduled"


def save_scheduler_config(config_data: dict, project_root: str = None):
    """Persist scheduler configuration to scheduler_config.json."""
    if project_root is None:
        project_root = _project_root()
    path = os.path.join(project_root, "scheduler_config.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2, default=str)


def load_scheduler_config(project_root: str = None) -> dict:
    """Load scheduler configuration from scheduler_config.json."""
    if project_root is None:
        project_root = _project_root()
    path = os.path.join(project_root, "scheduler_config.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_scheduler_log(project_root: str = None) -> list:
    """Load the scheduler run log."""
    if project_root is None:
        project_root = _project_root()
    path = os.path.join(project_root, "output", "scheduler_log.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return []
    return []

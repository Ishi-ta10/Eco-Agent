"""
Mail Scheduling Agent — __init__.py
Handles scheduled email report generation and delivery.
"""

from mail_scheduling_agent.scheduler import (
    start_background_scheduler,
    stop_scheduler,
    get_next_run,
    save_scheduler_config,
    load_scheduler_config,
    load_scheduler_log,
)
from mail_scheduling_agent.emailer import send_daily_report, send_email, build_email_html

__all__ = [
    "start_background_scheduler", "stop_scheduler", "get_next_run",
    "save_scheduler_config", "load_scheduler_config", "load_scheduler_log",
    "send_daily_report", "send_email", "build_email_html",
]

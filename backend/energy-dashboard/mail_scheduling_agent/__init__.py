"""
Mail Scheduling Agent — __init__.py
Handles scheduled email report generation and delivery.
"""

_SCHEDULER_IMPORT_ERROR = None

try:
    from mail_scheduling_agent.scheduler import (
        start_background_scheduler,
        stop_scheduler,
        get_next_run,
        save_scheduler_config,
        load_scheduler_config,
        load_scheduler_log,
    )
except ModuleNotFoundError as exc:
    # Keep email rendering/import paths usable even if optional scheduler deps are absent.
    _SCHEDULER_IMPORT_ERROR = exc

    def _missing_scheduler_dependency(*args, **kwargs):
        raise ModuleNotFoundError(
            "Optional dependency 'schedule' is required for scheduler controls. "
            "Install it with: pip install schedule"
        ) from _SCHEDULER_IMPORT_ERROR

    start_background_scheduler = _missing_scheduler_dependency
    stop_scheduler = _missing_scheduler_dependency
    get_next_run = _missing_scheduler_dependency
    save_scheduler_config = _missing_scheduler_dependency
    load_scheduler_config = _missing_scheduler_dependency
    load_scheduler_log = _missing_scheduler_dependency

from mail_scheduling_agent.emailer import send_daily_report, send_email, build_email_html

__all__ = [
    "start_background_scheduler", "stop_scheduler", "get_next_run",
    "save_scheduler_config", "load_scheduler_config", "load_scheduler_log",
    "send_daily_report", "send_email", "build_email_html",
]

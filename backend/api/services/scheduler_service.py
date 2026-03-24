"""
Scheduler service (simplified for MVP)
"""
import json
import sys
import os
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo

SCHEDULER_CONFIG_FILE = Path(__file__).parent.parent.parent / "energy-dashboard" / "scheduler_config.json"
SCHEDULER_LOG_FILE = Path(__file__).parent.parent.parent / "energy-dashboard" / "output" / "scheduler_log.json"
SCHEDULER_JOB_ID = "daily_energy_report"

# Load email environment variables
energy_dashboard_path = Path(__file__).parent.parent.parent / "energy-dashboard"
load_dotenv(energy_dashboard_path / ".env")

# Add energy-dashboard to sys.path at module level so imports work throughout the module
if str(energy_dashboard_path) not in sys.path:
    sys.path.insert(0, str(energy_dashboard_path))

# Debug marker
import time
_module_load_time = time.time()
_debug_log_path = energy_dashboard_path / "output" / "scheduler_module_debug.txt"
_debug_log_path.parent.mkdir(parents=True, exist_ok=True)
with open(_debug_log_path, 'a', encoding='utf-8') as f:
    f.write(f"Module loaded at {_module_load_time}\n")

_build_email_html_cached = None
_build_email_html_cached_mtime = None
_scheduler = BackgroundScheduler(timezone=ZoneInfo("Asia/Kolkata"))


def _get_build_email_html():
    """Load build_email_html directly from emailer.py to avoid package side effects."""
    global _build_email_html_cached, _build_email_html_cached_mtime

    emailer_path = energy_dashboard_path / "mail_scheduling_agent" / "emailer.py"
    current_mtime = emailer_path.stat().st_mtime if emailer_path.exists() else None

    # Reload when file changes so scheduler picks new email format without restart.
    if (
        _build_email_html_cached is not None
        and _build_email_html_cached_mtime is not None
        and current_mtime == _build_email_html_cached_mtime
    ):
        return _build_email_html_cached

    spec = importlib.util.spec_from_file_location("energy_dashboard_emailer", emailer_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load emailer module from {emailer_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _build_email_html_cached = module.build_email_html
    _build_email_html_cached_mtime = current_mtime
    return _build_email_html_cached


def _validate_send_time(send_time: str) -> tuple[int, int]:
    """Validate HH:MM time and return (hour, minute)."""
    if not isinstance(send_time, str) or ":" not in send_time:
        raise ValueError("send_time must be in HH:MM format")
    hour_str, minute_str = send_time.split(":", 1)
    if not hour_str.isdigit() or not minute_str.isdigit():
        raise ValueError("send_time must be in HH:MM format")

    hour = int(hour_str)
    minute = int(minute_str)
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        raise ValueError("send_time must be in HH:MM format")
    return hour, minute


def _ensure_scheduler_started() -> None:
    if not _scheduler.running:
        _scheduler.start()


def _schedule_daily_job(send_time: str) -> None:
    hour, minute = _validate_send_time(send_time)
    _ensure_scheduler_started()

    trigger = CronTrigger(hour=hour, minute=minute, timezone=ZoneInfo("Asia/Kolkata"))
    _scheduler.add_job(
        send_email_now,
        trigger=trigger,
        id=SCHEDULER_JOB_ID,
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=1800,
    )


def initialize_scheduler_from_config() -> None:
    """Initialize scheduler from persisted config when API starts."""
    cfg = load_scheduler_config()
    if cfg.get("auto_start", False):
        try:
            _schedule_daily_job(cfg.get("send_time", "10:00"))
        except Exception as exc:
            with open(_debug_log_path, 'a', encoding='utf-8') as f:
                f.write(f"Scheduler auto-start failed: {exc}\n")


def load_scheduler_config() -> Dict[str, Any]:
    """Load scheduler configuration"""
    if SCHEDULER_CONFIG_FILE.exists():
        with open(SCHEDULER_CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        # Return default config
        return {
            "to": "",
            "cc": "",
            "send_time": "10:00",
            "subject": "Daily Energy Report — Noida Campus — {date}",
            "custom_message": "",
            "auto_start": False,
            "include_sections": {
                "summary_kpis": True,
                "unified_table": True,
                "grid_summary": True,
                "solar_summary": True,
                "diesel_summary": True,
                "inverter_status": True,
                "raw_data": False
            },
            "uploaded_template_path": None
        }


def save_scheduler_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Save scheduler configuration"""
    with open(SCHEDULER_CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

    # If scheduler is already active, immediately apply updated send_time.
    if _scheduler.get_job(SCHEDULER_JOB_ID) is not None:
        _schedule_daily_job(config.get("send_time", "10:00"))

    # Respect auto_start preference for future startup and current runtime.
    if config.get("auto_start", False) and _scheduler.get_job(SCHEDULER_JOB_ID) is None:
        _schedule_daily_job(config.get("send_time", "10:00"))
    if not config.get("auto_start", False) and _scheduler.get_job(SCHEDULER_JOB_ID) is not None:
        _scheduler.remove_job(SCHEDULER_JOB_ID)

    return config


def get_scheduler_status() -> Dict[str, Any]:
    """Get scheduler status"""
    job = _scheduler.get_job(SCHEDULER_JOB_ID)
    next_run_time = job.next_run_time if job else None
    history = load_scheduler_history(limit=1)
    return {
        "status": "running" if job else "stopped",
        "next_run": next_run_time.isoformat() if next_run_time else None,
        "last_run": history[0] if history else None,
    }


def start_scheduler(send_time: str) -> Dict[str, Any]:
    """Start the scheduler"""
    _schedule_daily_job(send_time)

    # Persist chosen time so UI refresh reflects latest schedule.
    config = load_scheduler_config()
    config["send_time"] = send_time
    with open(SCHEDULER_CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

    job = _scheduler.get_job(SCHEDULER_JOB_ID)
    next_run_time = job.next_run_time if job else None
    return {
        "status": "running",
        "next_run": next_run_time.isoformat() if next_run_time else None,
    }


def stop_scheduler() -> Dict[str, Any]:
    """Stop the scheduler"""
    if _scheduler.get_job(SCHEDULER_JOB_ID) is not None:
        _scheduler.remove_job(SCHEDULER_JOB_ID)
    return {
        "status": "stopped"
    }


def build_energy_report_html(config: Dict[str, Any]) -> tuple:
    """Build HTML body and CSV content for Energy Consumption Report format.
    Returns: (html_content, csv_content)
    """
    try:
        # Add energy-dashboard to path BEFORE importing energy modules
        energy_dashboard_path = Path(__file__).parent.parent.parent / "energy-dashboard"
        if str(energy_dashboard_path) not in sys.path:
            sys.path.insert(0, str(energy_dashboard_path))

        # Load energy data
        from data_ingestion_agent import loader, processor
        build_email_html = _get_build_email_html()

        # Load the main config.yaml used by the data and KPI processor
        data_config = loader.load_config()

        # Load data
        grid_df = loader.load_grid_data(data_config)
        solar_df = loader.load_solar_data(data_config)
        diesel_df = loader.load_diesel_data(data_config)

        # Build unified dataframe
        unified_df = processor.build_unified_dataframe(grid_df, solar_df, diesel_df)

        # Align report to the same 7-day date set used by dashboard views.
        try:
            solar_last7_df = loader.load_solar_last7_data(data_config)
            if len(solar_last7_df) > 0 and "Date" in solar_last7_df.columns:
                allowed_dates = set(
                    pd.to_datetime(solar_last7_df["Date"], errors="coerce").dt.normalize().dropna()
                )
                unified_dates = pd.to_datetime(unified_df["Date"], errors="coerce").dt.normalize()
                unified_df = unified_df[unified_dates.isin(allowed_dates)].copy()
        except Exception as exc:
            with open(_debug_log_path, 'a', encoding='utf-8') as f:
                f.write(f"7-day alignment failed in scheduler report builder: {exc}\n")

        # Fallback: if aligned data is empty, use latest 7 dates from unified data.
        if unified_df.empty:
            working = processor.build_unified_dataframe(grid_df, solar_df, diesel_df).copy()
            working["_date_norm"] = pd.to_datetime(working["Date"], errors="coerce").dt.normalize()
            unique_dates = sorted([d for d in working["_date_norm"].dropna().unique()])
            keep_dates = set(unique_dates[-7:])
            unified_df = working[working["_date_norm"].isin(keep_dates)].drop(columns=["_date_norm"], errors="ignore")

        # Reverse dataframe to show chronologically (oldest to newest)
        display_df = unified_df.sort_values('Date', ascending=True).reset_index(drop=True)

        # Prepare CSV content
        csv_df = display_df.copy()
        csv_content = csv_df.to_csv(index=False)

        # Reuse the template-based renderer used by the dashboard scheduler emails.
        html = build_email_html(
            display_df,
            data_config,
            config.get("custom_message", ""),
            config.get("include_sections", None),
        )

        return html, csv_content

    except Exception as e:
        # Fallback simple HTML if data loading fails
        html = f"""
        <html>
            <body style="font-family: Arial; padding: 20px;">
                <h2>Energy Consumption Report</h2>
                <p>Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Daily energy consumption and cost analysis report.</p>
                <p style='color: orange;'>Note: Could not load detailed energy data. {str(e)}</p>
            </body>
        </html>
        """
        csv_content = "Error generating report"
        return html, csv_content


def send_email_now() -> Dict[str, Any]:
    """Send email immediately with Energy Report and CSV attachment"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email import encoders
    from datetime import datetime

    with open(_debug_log_path, 'a', encoding='utf-8') as f:
        f.write("send_email_now called\n")

    config = load_scheduler_config()

    try:
        # Load env variables for email
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        sender_email = os.getenv("SENDER_EMAIL", "")
        sender_password = os.getenv("SENDER_PASSWORD", "").strip('"')
        use_tls = os.getenv("SMTP_USE_TLS", "True").lower() == "true"
        timeout = int(os.getenv("SMTP_TIMEOUT", "10"))

        # Get recipient from config or env
        to_list = [addr.strip() for addr in config.get("to", os.getenv("DEFAULT_RECIPIENT_EMAIL", "")).split(",") if addr.strip()]
        cc_list = [addr.strip() for addr in config.get("cc", "").split(",") if addr.strip()] if config.get("cc") else []

        if not to_list:
            raise ValueError("No recipient email address configured")

        # Build the Energy Report HTML and CSV
        html_body, csv_content = build_energy_report_html(config)

        # Create email message with mixed content (HTML + attachment)
        msg = MIMEMultipart("mixed")
        msg["From"] = sender_email
        msg["To"] = ", ".join(to_list)
        if cc_list:
            msg["Cc"] = ", ".join(cc_list)

        subject = config.get("subject", "Daily Energy Report").replace("{date}", datetime.now().strftime("%d %b %Y"))
        msg["Subject"] = subject

        # Create alternative part for HTML
        msg_alternative = MIMEMultipart("alternative")
        msg.attach(msg_alternative)

        # Attach HTML body
        msg_alternative.attach(MIMEText(html_body, "html"))

        uploaded_template_path = config.get("uploaded_template_path")
        attachment_name = None

        if uploaded_template_path and Path(uploaded_template_path).exists():
            attachment_name = Path(uploaded_template_path).name
            with open(uploaded_template_path, "rb") as f:
                attachment_bytes = f.read()
        else:
            attachment_name = f"Energy_Report_{datetime.now().strftime('%Y-%m-%d')}.csv"
            attachment_bytes = csv_content.encode('utf-8')

        attachment = MIMEBase("application", "octet-stream")
        attachment.set_payload(attachment_bytes)
        encoders.encode_base64(attachment)
        attachment.add_header("Content-Disposition", f"attachment; filename= {attachment_name}")
        msg.attach(attachment)

        # Connect and send
        all_recipients = to_list + cc_list

        print(f"[DEBUG] Connecting to {smtp_server}:{smtp_port}")
        with smtplib.SMTP(smtp_server, smtp_port, timeout=timeout) as server:
            if use_tls:
                server.starttls()

            if sender_email and sender_password:
                server.login(sender_email, sender_password)

            server.sendmail(sender_email, all_recipients, msg.as_string())

        # Log successful send
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "status": "Success",
            "recipients": ", ".join(to_list),
            "attachment": attachment_name,
            "notes": f"Email sent successfully to {', '.join(to_list)} with HTML report and attachment"
        }
        print(f"[DEBUG] Log Entry Attac: {log_entry['attachment']}", flush=True)

        logs = load_scheduler_history()
        logs.insert(0, log_entry)
        logs = logs[:50]

        with open(SCHEDULER_LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=2)

        return log_entry

    except Exception as e:
        # Log failed send
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "status": "Failed",
            "recipients": config.get("to", ""),
            "attachment": None,
            "notes": f"Error: {str(e)[:150]}"
        }

        logs = load_scheduler_history()
        logs.insert(0, log_entry)
        logs = logs[:50]

        with open(SCHEDULER_LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=2)

        return log_entry


def load_scheduler_history(limit: int = 10) -> list:
    """Load scheduler history"""
    if SCHEDULER_LOG_FILE.exists():
        with open(SCHEDULER_LOG_FILE, 'r') as f:
            logs = json.load(f)
            return logs[:limit]
    return []


def upload_template(file_path: str) -> Dict[str, Any]:
    """Handle template upload"""
    config = load_scheduler_config()
    config["uploaded_template_path"] = file_path

    save_scheduler_config(config)

    return {
        "filename": Path(file_path).name,
        "path": file_path,
        "uploaded_at": datetime.now().isoformat()
    }

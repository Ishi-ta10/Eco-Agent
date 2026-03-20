"""
Scheduler service (simplified for MVP)
"""
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

SCHEDULER_CONFIG_FILE = Path(__file__).parent.parent.parent / "energy-dashboard" / "scheduler_config.json"
SCHEDULER_LOG_FILE = Path(__file__).parent.parent.parent / "energy-dashboard" / "scheduler_log.json"

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
    return config


def get_scheduler_status() -> Dict[str, Any]:
    """Get scheduler status"""
    # For MVP, return a mock status
    # In production, this would check APScheduler status
    return {
        "status": "stopped",
        "next_run": None,
        "last_run": None
    }


def start_scheduler(send_time: str) -> Dict[str, Any]:
    """Start the scheduler"""
    # For MVP, just return success
    # In production, this would start APScheduler
    return {
        "status": "running",
        "next_run": f"{datetime.now().strftime('%Y-%m-%d')} {send_time}:00"
    }


def stop_scheduler() -> Dict[str, Any]:
    """Stop the scheduler"""
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
        from mail_scheduling_agent.emailer import build_email_html

        # Load the main config.yaml used by the data and KPI processor
        data_config = loader.load_config()

        # Load data
        grid_df = loader.load_grid_data(data_config)
        solar_df = loader.load_solar_data(data_config)
        diesel_df = loader.load_diesel_data(data_config)

        # Build unified dataframe
        unified_df = processor.build_unified_dataframe(grid_df, solar_df, diesel_df)

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

        # Create and attach CSV file
        csv_filename = f"Energy_Report_{datetime.now().strftime('%Y-%m-%d')}.csv"
        print(f"[DEBUG] CSV Filename: {csv_filename}", flush=True)
        csv_attachment = MIMEBase("application", "octet-stream")
        csv_attachment.set_payload(csv_content.encode('utf-8'))
        encoders.encode_base64(csv_attachment)
        csv_attachment.add_header("Content-Disposition", f"attachment; filename= {csv_filename}")
        msg.attach(csv_attachment)

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
            "attachment": csv_filename,
            "notes": f"Email sent successfully to {', '.join(to_list)} with HTML report and CSV attachment"
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
